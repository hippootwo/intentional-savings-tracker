from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timezone

app = FastAPI(
    title="Intentional Agent Middleware",
    description="Mock server-side agent acting as middleware for the Intentional Spending Tracker.",
    version="1.0.0"
)

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Restrict to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SpendingRecord(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    category: str = Field(..., description="Category must be Expense, Income, or Savings")
    description: str = Field(..., min_length=1, description="Description cannot be empty")

class ProcessedRecord(SpendingRecord):
    timestamp: str
    status: str
    message: str

@app.post("/api/track", response_model=ProcessedRecord)
async def track_spending(record: SpendingRecord):
    """
    Receives the confirmed payload from the frontend.
    Validates it, appends a timestamp, and prepares data for Firebase.
    """
    # Validate Category
    if record.category not in ["Expense", "Income", "Savings"]:
        raise HTTPException(status_code=400, detail="Invalid category. Must be Expense, Income, or Savings")
    
    # Append timestamp in ISO 8601 format
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Prepare data payload for Firebase Firestore
    firebase_payload = {
        "amount": record.amount,
        "category": record.category,
        "description": record.description,
        "timestamp": timestamp,
    }
    
    # -------------------------------------------------------------------------
    # MOCK BEHAVIOR:
    # In a production environment, you would use the firebase-admin SDK to
    # authenticate and write this `firebase_payload` directly to Firestore.
    # e.g. db.collection('transactions').add(firebase_payload)
    # -------------------------------------------------------------------------
    
    print(f"[INTENTIONAL AGENT] Validated record. Preparing to write to Firebase:\n{firebase_payload}")
    
    return ProcessedRecord(
        amount=record.amount,
        category=record.category,
        description=record.description,
        timestamp=timestamp,
        status="success",
        message="Record successfully processed and prepared for Firebase."
    )

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
