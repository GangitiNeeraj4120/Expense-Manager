
from datetime import datetime, timezone

from database import (
    init_db,
    transactions,
    goals,
    memories,
)

BATCH = "spendsense_demo_v1"


def seed():
    init_db()

    # Re-running this script replaces only this demo batch.
    for collection in (transactions, goals, memories):
        collection.delete_many({"demo_batch": BATCH})

    now = datetime.now(timezone.utc)
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    end = datetime(2026, 11, 1, tzinfo=timezone.utc)

    memory = {
        "type": "semantic",
        "condition": "cafe visit with friends",
        "value": "Social Spending",
        "source": "user_correction",
        "confidence": 1.0,
        "created_at": now,
        "status": "active",
        "demo_batch": BATCH,
    }
    memory_id = memories.insert_one(memory).inserted_id

    transaction_data = [
        (300, "Campus Cafe", "Social Spending", "Meeting friends"),
        (150, "Campus Canteen", "Food & Dining", "Lunch"),
        (1200, "Amazon", "Shopping", "Headphones"),
        (250, "Campus Cafe", "Social Spending", "Meeting friends"),
        (100, "Bus", "Transport", "Travel to college"),
    ]

    transactions.insert_many([
        {
            "amount": amount,
            "merchant": merchant,
            "category": category,
            "date": now,
            "context": context,
            "memory_ids": (
                [str(memory_id)]
                if merchant == "Campus Cafe" else []
            ),
            "demo_batch": BATCH,
        }
        for amount, merchant, category, context in transaction_data
    ])

    goals.insert_many([
        {
            "name": "October spending limit",
            "type": "spending_limit",
            "target": 12000.0,
            "start_date": start,
            "end_date": end,
            "demo_batch": BATCH,
        },
        {
            "name": "Save ₹5,000 this month",
            "type": "savings_target",
            "target": 5000.0,
            "start_date": start,
            "end_date": end,
            "demo_batch": BATCH,
        },
    ])

    print("Demo data inserted.")
    print("Expected total spending: ₹2,000")
    print("Expected category totals:")
    print({
        "Social Spending": 550,
        "Food & Dining": 150,
        "Shopping": 1200,
        "Transport": 100,
    })


if __name__ == "__main__":
    seed()
