"""FastAPI bridge between the SpendSense React frontend and existing backend."""
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Literal

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from Agent.graph import build_graph
from Agent.analysis_state import needs_analysis_refresh
from Agent.financial_Analysis import run_financial_analysis
from Agent.memory_engine import retrieve_memories, upsert_memory
from database.database import (
    get_goals,
    get_transactions,
    memories as memories_collection,
    serialize_document,
)
from database.finance import get_category_totals, get_total_spending

app = FastAPI(title="SpendSense API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = None
USER_ID_DEFAULT = "demo-user"


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def month_bounds():
    today = datetime.now(timezone.utc).date()
    start = today.replace(day=1)
    end = today + timedelta(days=1)  # end is exclusive for DB queries
    return start.isoformat(), end.isoformat()


def as_ui_transaction(tx):
    amount = float(tx.get("amount", 0) or 0)
    category = str(tx.get("category", "Other"))
    low = category.lower()
    icon = "Coffee" if any(x in low for x in ("food", "drink", "coffee")) else (
        "Car" if any(x in low for x in ("transport", "travel", "fuel")) else (
            "ShoppingBag" if any(x in low for x in ("shop", "retail")) else "Wallet"
        )
    )
    raw_date = tx.get("date")
    try:
        parsed_date = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
        display_date = parsed_date.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        display_date = str(raw_date or "")
    # Current DB schema stores positive amounts and does not distinguish income.
    # Treat these records as expenses in the UI until a transaction type is added.
    return {
        "id": str(tx.get("id", "")),
        "name": tx.get("merchant", "Unknown transaction"),
        "category": category,
        "date": display_date,
        "amount": -abs(amount),
        "icon": icon,
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/dashboard/summary")
def dashboard_summary():
    try:
        start, end = month_bounds()
        total = float(get_total_spending(start, end))
        categories_raw = get_category_totals(start, end)
        categories = [
            {"category": name or "Other", "amount": float(amount),
             "percentage": round(float(amount) / total * 100, 1) if total else 0}
            for name, amount in categories_raw.items()
        ]
        categories.sort(key=lambda item: item["amount"], reverse=True)

        transactions_raw = get_transactions(start_date=start, end_date=end, limit=10)
        recent = [as_ui_transaction(tx) for tx in transactions_raw]

        today = datetime.now(timezone.utc).date()
        week_start = today - timedelta(days=6)
        week_txs = get_transactions(start_date=week_start.isoformat(), end_date=(today + timedelta(days=1)).isoformat(), limit=1000)
        daily = defaultdict(float)
        for tx in week_txs:
            try:
                d = datetime.fromisoformat(str(tx.get("date")).replace("Z", "+00:00")).date()
                daily[d.isoformat()] += float(tx.get("amount", 0) or 0)
            except (ValueError, TypeError):
                continue
        daily_spending = [
            {"date": (week_start + timedelta(days=i)).isoformat(),
             "day": (week_start + timedelta(days=i)).strftime("%a"),
             "amount": round(daily[(week_start + timedelta(days=i)).isoformat()], 2)}
            for i in range(7)
        ]

        goals = get_goals(goal_type="spending_limit", start_date=start, end_date=end, limit=100)
        budget_target = float(goals[0]["target"]) if goals else None
        return {
            "monthly_spending": total,
            "total_balance": None,
            "budget_target": budget_target,
            "budget_remaining": round(budget_target - total, 2) if budget_target is not None else None,
            "category_totals": categories,
            "daily_spending": daily_spending,
            "transactions": recent,
            "period_start": start,
            "period_end_exclusive": end,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not load dashboard data: {exc}") from exc


class ChatRequest(BaseModel):
    user_id: str = USER_ID_DEFAULT
    message: str = Field(min_length=1, max_length=4000)


@app.post("/api/assistant/chat")
def assistant_chat(payload: ChatRequest):
    try:
        result = get_graph().invoke({"user_id": payload.user_id, "message": payload.message})
        return {"response": result.get("answer", "I couldn't generate a response.")}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent request failed: {exc}") from exc


@app.get("/api/memory-lab")
def memory_lab(user_id: str = USER_ID_DEFAULT):
    try:
        # Refresh the agent-generated observations if none exist or the refresh is due.
        if needs_analysis_refresh(user_id):
            run_financial_analysis(user_id)
        start, end = month_bounds()
        total = float(get_total_spending(start, end))
        categories_raw = get_category_totals(start, end)
        categories = [
            {"category": name or "Other", "amount": float(amount),
             "percentage": round(float(amount) / total * 100, 1) if total else 0}
            for name, amount in categories_raw.items()
        ]
        categories.sort(key=lambda item: item["amount"], reverse=True)
        memories = retrieve_memories(limit=100)
        recent = [as_ui_transaction(tx) for tx in get_transactions(start_date=start, end_date=end, limit=10)]
        insights = [m for m in memories if m.get("type") == "observed_pattern"]
        return {
            "summary": {"monthly_spending": total, "memory_count": len(memories)},
            "memories": memories,
            "insights": insights,
            "category_totals": categories,
            "recent_transactions": recent,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not load Memory Lab: {exc}") from exc


class MemoryRequest(BaseModel):
    user_id: str = USER_ID_DEFAULT
    type: Literal["semantic", "observed_pattern", "user_confirmed", "preference"]
    condition: str = Field(min_length=1, max_length=300)
    value: str = Field(min_length=1, max_length=2000)
    source: str = "memory_lab"
    confidence: float = Field(default=0.9, ge=0, le=1)


@app.post("/api/memories")
def create_memory(payload: MemoryRequest):
    try:
        saved = upsert_memory(payload.model_dump(exclude={"user_id"}))
        return {"memory": saved}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not save memory: {exc}") from exc


@app.delete("/api/memories/{memory_id}")
def delete_memory(memory_id: str):
    if not ObjectId.is_valid(memory_id):
        raise HTTPException(status_code=400, detail="Invalid memory ID")
    result = memories_collection.delete_one({"_id": ObjectId(memory_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"deleted": True}