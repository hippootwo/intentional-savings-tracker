import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Delete conflicting system env var that causes the SDK to break
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]

from typing import Any
from google.adk.workflow import Workflow, node
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.events import Event

# Initialize Firebase Admin
if not firebase_admin._apps:
    if os.path.exists("serviceAccountKey.json"):
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    elif os.path.exists("../../serviceAccountKey.json"):
        cred = credentials.Certificate("../../serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()
db = firestore.client()

def get_financial_totals() -> dict:
    """Queries the Firestore transactions collection and aggregates Total Income, Total Expenses, and Total Savings. You MUST use this tool to get financial data."""
    transactions_ref = db.collection("transactions")
    docs = transactions_ref.stream()
    
    totals = {"Income": 0, "Expense": 0, "Savings": 0}
    for doc in docs:
        data = doc.to_dict()
        cat = data.get("category", "")
        amt = data.get("amount", 0)
        if cat in totals:
            totals[cat] += amt
            
    print(f"[TOOL EXECUTION] get_financial_totals called by agent. Returning: {totals}")
    return totals

def strip_json_markdown(text: str) -> str:
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

@node(name="PRE_LLM_SCREEN")
def pre_llm_screen(node_input: Any) -> Event:
    import sys
    print(f"DEBUG node_input: {type(node_input)} {node_input!r}", file=sys.stderr)
    sys.stderr.flush()
    data = node_input
    
    # Unwrap if it's a message object
    if hasattr(data, 'text'):
        data = data.text
    elif isinstance(data, dict) and 'message' in data:
        data = data['message']
    elif hasattr(data, 'parts') and data.parts:
        data = data.parts[0].text

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return Event(route="ERROR", output="Invalid JSON")
            
    if not isinstance(data, dict):
        return Event(route="ERROR", output="Expected dictionary")
        
    amount = data.get("amount", 0)
    try:
        amount = float(amount)
        if amount <= 0:
            return Event(route="ERROR", output="Negative amount")
    except Exception:
        return Event(route="ERROR", output="Invalid amount")
        
    return Event(route="ROUTER", output=data)

@node(name="ROUTER")
def router_node(node_input: Any) -> Event:
    data = node_input
    if hasattr(data, 'text'):
        data = data.text
    elif isinstance(data, dict) and 'message' in data:
        data = data['message']
    elif hasattr(data, 'parts') and data.parts:
        data = data.parts[0].text

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            pass
            
    if isinstance(data, dict):
        if data.get("category") == "Analytics":
            return Event(route="visualizer", output=data)
        if data.get("category") == "Savings":
            return Event(route="stoic", output=data)
    return Event(route="context", output=data)

def load_skill_prompt(skill_name: str) -> str:
    # Need to go up two directories from backend/app/agent.py to reach .agents
    path = os.path.join(os.path.dirname(__file__), "..", "..", ".agents", "skills", skill_name, "SKILL.md")
    if not os.path.exists(path):
        return f"Execute {skill_name} skill."
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("---")
    if len(parts) >= 3:
        return "---".join(parts[2:]).strip()
    return content.strip()

stoic_agent = Agent(
    name="stoic_reinforcer",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction=load_skill_prompt("stoic-reinforcer"),
)

context_validator_agent = Agent(
    name="context_validator",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction=load_skill_prompt("context-validator"),
)

visualizer_agent = Agent(
    name="visualizer",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction=load_skill_prompt("financial-visualizer"),
    tools=[get_financial_totals]
)

workflow = Workflow(
    name="intentional_spending_workflow",
    edges=[
        ("START", pre_llm_screen),
        (pre_llm_screen, {
            "ROUTER": router_node,
        }),
        (router_node, {
            "stoic": stoic_agent,
            "context": context_validator_agent,
            "visualizer": visualizer_agent
        })
    ]
)

app = App(
    root_agent=workflow,
    name="app",
)

root_agent = workflow
