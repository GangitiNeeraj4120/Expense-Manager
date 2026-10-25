"""
from pymongo import MongoClient
uri = "mongodb+srv://ananybahekar28_db_user:<db_password>@spendsense.jecxjaq.mongodb.net/"
client = MongoClient(uri)
try:
    client.admin.command("ping")
    print("Connected successfully")
    client.close()

except Exception as e:
    raise Exception(
        "The following error occurred: ", e)

"""


import os
from datetime import datetime, timezone

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "spendsense")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is missing. Add it to your local .env file."
    )

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000,
)

db = client[MONGODB_DATABASE]

transactions = db["transactions"]
memories = db["memories"]
goals = db["goals"]
analysis_state = db["analysis_state"]

def init_db():
    """Verify the connection and create basic indexes."""
    client.admin.command("ping")

    transactions.create_index(
        [("date", DESCENDING)]
    )
    transactions.create_index(
        [("category", ASCENDING), ("date", DESCENDING)]
    )
    memories.create_index(
        [("type", ASCENDING), ("status", ASCENDING)]
    )
    goals.create_index(
        [("start_date", ASCENDING), ("end_date", ASCENDING)]
    )
    analysis_state.create_index(
        [("user_id", ASCENDING)],
        unique=True,
    )
    return True


def serialize_document(document):
    """Convert MongoDB-specific values to UI-friendly values."""
    if document is None:
        return None

    result = dict(document)

    if "_id" in result:
        result["id"] = str(result.pop("_id"))

    for key, value in result.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()

    return result


def _parse_date(value):
    """Convert a date/datetime/string to a timezone-aware datetime."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ValueError("date must be a datetime or ISO date string")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def add_transaction(
    amount,
    merchant,
    category,
    date,
    context="",
    memory_ids=None,
):
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("amount must be a positive INR amount")

    if not merchant or not merchant.strip():
        raise ValueError("merchant is required")

    if not category or not category.strip():
        raise ValueError("category is required")

    doc = {
        "amount": round(float(amount), 2),
        "merchant": merchant.strip(),
        "category": category.strip(),
        "date": _parse_date(date),
        "context": context.strip(),
        "memory_ids": memory_ids or [],
    }

    result = transactions.insert_one(doc)
    return serialize_document(
        transactions.find_one({"_id": result.inserted_id})
    )


def get_transactions(
    start_date=None,
    end_date=None,
    category=None,
    limit=100,
):
    query = {}
    date_filter = {}

    if start_date is not None:
        date_filter["$gte"] = _parse_date(start_date)

    if end_date is not None:
        date_filter["$lt"] = _parse_date(end_date)

    if date_filter:
        query["date"] = date_filter

    if category:
        query["category"] = category

    cursor = (
        transactions.find(query)
        .sort("date", DESCENDING)
        .limit(limit)
    )

    return [serialize_document(doc) for doc in cursor]


def delete_transaction(transaction_id):
    if not ObjectId.is_valid(transaction_id):
        raise ValueError("Invalid transaction ID")

    result = transactions.delete_one(
        {"_id": ObjectId(transaction_id)}
    )
    return result.deleted_count == 1


def save_memory(memory):
    required = [
        "type", "condition", "value",
        "source", "confidence", "status",
    ]

    missing = [key for key in required if key not in memory]
    if missing:
        raise ValueError(f"Missing memory fields: {missing}")

    confidence = memory["confidence"]
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")

    doc = {
        "type": memory["type"], # type -> category
        "condition": str(memory["condition"]),
        "value": str(memory["value"]),
        "source": memory["source"],
        "confidence": float(confidence),
        "created_at": _parse_date(
            memory.get("created_at", datetime.now(timezone.utc))
        ),
        "status": memory["status"],
    }

    result = memories.insert_one(doc)
    return serialize_document(
        memories.find_one({"_id": result.inserted_id})
    )


def get_memories(type=None, status="active", limit=100):
    query = {}

    if type:
        query["type"] = type

    if status is not None:
        query["status"] = status

    cursor = (
        memories.find(query)
        .sort("created_at", DESCENDING)
        .limit(limit)
    )

    return [serialize_document(doc) for doc in cursor]


def save_goal(goal: dict) -> dict: # only saves new goals, does not update existing ones
    """Validate and save a financial goal to MongoDB."""

    required_fields = [
        "name",
        "type",
        "target",
        "start_date",
        "end_date",
    ]

    for field in required_fields:
        if field not in goal or goal[field] is None:
            raise ValueError(f"Missing required goal field: {field}")

    allowed_types = {"savings_target", "spending_limit"}
    if goal["type"] not in allowed_types:
        raise ValueError(
            f"Goal type must be one of: {allowed_types}"
        )

    if not isinstance(goal["name"], str) or not goal["name"].strip():
        raise ValueError("Goal name cannot be empty.")

    target = float(goal["target"])
    if target <= 0:
        raise ValueError("Goal target must be greater than zero.")

    start_date = _parse_date(goal["start_date"])
    end_date = _parse_date(goal["end_date"])

    if start_date >= end_date:
        raise ValueError("end_date must be after start_date.")

    document = {
        "name": goal["name"].strip(),
        "type": goal["type"],
        "target": round(target, 2),
        "start_date": start_date,
        "end_date": end_date,
    }

    result = goals.insert_one(document)
    saved = goals.find_one({"_id": result.inserted_id})

    return serialize_document(saved)


def get_goals( # only has specific goal types, a bit hardcoded
    goal_type: str | None = None,
    start_date=None,
    end_date=None,
    limit: int = 100,
) -> list[dict]:
    """Retrieve goals, optionally filtered by type and date range."""

    if limit < 1:
        raise ValueError("limit must be at least 1.")

    query = {}

    if goal_type is not None:
        allowed_types = {"savings_target", "spending_limit"}
        if goal_type not in allowed_types:
            raise ValueError("Invalid goal type.")
        query["type"] = goal_type

    # Return goals whose periods overlap the requested period.
    if start_date is not None:
        query["end_date"] = {"$gt": _parse_date(start_date)}

    if end_date is not None:
        query.setdefault("start_date", {})
        query["start_date"]["$lt"] = _parse_date(end_date)

    cursor = (
        goals.find(query)
        .sort("start_date", -1)
        .limit(limit)
    )

    return [serialize_document(doc) for doc in cursor]


def get_analysis_state(user_id: str) -> dict | None:
    """Return the saved financial-analysis state for a user."""
    document= analysis_state.find_one(
        {"user_id": user_id}
    )
    return(serialize_document(document))

def mark_analysis_success(user_id: str) -> None:
    """Record a successful financial analysis."""
    now = datetime.now(timezone.utc)

    analysis_state.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "last_successful_analysis_at": now,
                "last_attempt_at": now,
                "status": "success",
            }
        },
        upsert=True,
    )
def mark_analysis_failure(user_id: str) -> None:
    """Record a failed refresh without resetting its success timestamp."""
    analysis_state.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "status": "failed",
                "last_attempt_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )