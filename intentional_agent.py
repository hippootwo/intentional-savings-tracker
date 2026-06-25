import os
import json
from typing import Optional, Literal, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timezone
from app.agent import workflow, strip_json_markdown, db, get_financial_totals

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

session_service = InMemorySessionService()
runner = Runner(agent=workflow, session_service=session_service, app_name="intentional_tracker")

async def run_agent_workflow(payload: dict) -> dict:
    session = session_service.create_session_sync(user_id="user", app_name="intentional_tracker")
    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=json.dumps(payload))]
    )
    
    final_text = None
    error_message = None
    
    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=message,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE)
    ):
        if event.actions and event.actions.route == "ERROR":
            error_message = str(event.output)
        elif event.author in ["context_validator", "stoic_reinforcer", "visualizer"] and getattr(event, "partial", None) is False:
            if event.content and event.content.parts:
                final_text = "".join(part.text for part in event.content.parts if part.text)
                
    if error_message:
        return {"status": "rejected", "user_message": error_message}
        
    if final_text:
        return json.loads(strip_json_markdown(final_text))
            
    raise Exception("Workflow did not yield a valid final response.")

app = FastAPI(
    title="Intentional Agent Middleware",
    description="Two-phase hybrid validation pipeline for the Intentional Spending Tracker.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    for error in errors:
        msg = str(error.get("msg", ""))
        if "Please enter a positive amount." in msg:
            return JSONResponse(
                status_code=400,
                content={"detail": "Please enter a positive amount."}
            )
    return JSONResponse(
        status_code=400,
        content={"detail": "Validation error", "errors": errors}
    )

class TransactionInput(BaseModel):
    amount: float = Field(...)
    category: Literal["Expense", "Income", "Savings"] = Field(...)
    description: Optional[str] = Field(default=None)
    flags: List[str] = Field(default_factory=list)

    @field_validator("amount", mode="before")
    def parse_amount(cls, v):
        if isinstance(v, str):
            v = v.replace(",", ".")
        try:
            val = float(v)
        except ValueError:
            raise ValueError("Amount must be a valid number.")
        if val <= 0:
            raise ValueError("Please enter a positive amount.")
        return val

    @model_validator(mode="after")
    def attach_flags(self) -> 'TransactionInput':
        flags = []
        if not self.description or not self.description.strip():
            flags.append("missing_context")
        
        if self.amount < 2:
            flags.append("suspiciously_low")
        if self.amount > 150:
            flags.append("high_impact")
            
        self.flags = flags
        return self

class CognitiveOutput(BaseModel):
    status: Literal["approved", "rejected", "warning"]
    user_message: str
    final_category: str



@app.post("/api/validate-transaction", response_model=CognitiveOutput)
async def validate_transaction(transaction: TransactionInput):
    # Phase 1: ADK 2.0 Graph Workflow triggers from this endpoint.
    
    user_payload = {
        "amount": transaction.amount,
        "category": transaction.category,
        "description": transaction.description or "",
        "flags": transaction.flags
    }

    try:
        # Pass the payload to the true ADK 2.0 stateful graph workflow via Runner
        result = await run_agent_workflow(user_payload)

        output = CognitiveOutput(
            status=result.get("status", "warning"),
            user_message=result.get("user_message", "Could not fully parse agent response."),
            final_category=result.get("final_category", transaction.category)
        )
        
        # Write to Firestore if approved
        if output.status == "approved":
            timestamp = datetime.now(timezone.utc).isoformat()
            db.collection("transactions").add({
                "amount": transaction.amount,
                "category": output.final_category,
                "description": transaction.description or "",
                "timestamp": timestamp,
                "ai_overridden": False
            })
            
        return output
    except Exception as e:
        print(f"[ERROR] Cognitive Phase failed: {e}")
        return CognitiveOutput(
            status="warning",
            user_message="Sorry, validation offline. Please review and confirm your transaction manually.",
            final_category=transaction.category
        )

class ForceSubmitInput(BaseModel):
    amount: float
    category: str
    description: str

@app.post("/api/force-submit")
async def force_submit(transaction: ForceSubmitInput):
    timestamp = datetime.now(timezone.utc).isoformat()
    db.collection("transactions").add({
        "amount": transaction.amount,
        "category": transaction.category,
        "description": transaction.description,
        "timestamp": timestamp,
        "ai_overridden": True
    })
    return {"status": "success", "message": "Transaction forced successfully."}

@app.get("/api/analytics")
async def get_analytics():
    try:
        analytics_payload = {
            "amount": 1.0,
            "category": "Analytics",
            "description": "Trigger analytics process and generate JSON chart payload",
            "flags": []
        }
        
        result = await run_agent_workflow(analytics_payload)
        return result
        
    except Exception as e:
        print(f"[ERROR] Analytics Phase failed: {e}")
        print("[FALLBACK] Agent offline. Triggering deterministic fallback logic.")
        
        # 1. Fetch totals deterministically
        totals = get_financial_totals()
        
        # 2. Extract values
        income = totals.get("Income", 0)
        expenses = totals.get("Expense", 0)
        savings = totals.get("Savings", 0)
        
        # 3. Calculate Rate
        rate = round((savings / income) * 100, 1) if income > 0 else 0.0
        
        # 4. Construct Fallback JSON
        fallback_data = {
            "status": "stream_fallback",
            "metrics": {
                "intentional_savings_rate": rate,
                "total_expenses": expenses
            },
            "chart_data": [
                {"name": "Income", "value": income},
                {"name": "Expenses", "value": expenses},
                {"name": "Savings", "value": savings}
            ]
        }
        
        return fallback_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
