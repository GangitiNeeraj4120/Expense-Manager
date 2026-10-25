
from collections import defaultdict

from .database import transactions, goals, serialize_document, _parse_date


def get_total_spending(start_date=None, end_date=None):
    match = {}

    if start_date is not None or end_date is not None:
        match["date"] = {}

        if start_date is not None:
            match["date"]["$gte"] = _parse_date(start_date)

        if end_date is not None:
            match["date"]["$lt"] = _parse_date(end_date)

    pipeline = [
        {"$match": match},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]

    result = list(transactions.aggregate(pipeline))
    return round(float(result[0]["total"]), 2) if result else 0.0


def get_category_totals(start_date=None, end_date=None):
    match = {}

    if start_date is not None or end_date is not None:
        match["date"] = {}

        if start_date is not None:
            match["date"]["$gte"] = _parse_date(start_date)

        if end_date is not None:
            match["date"]["$lt"] = _parse_date(end_date)

    pipeline = [
        {"$match": match},
        {
            "$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"},
            }
        },
    ]

    return {
        row["_id"]: round(float(row["total"]), 2)
        for row in transactions.aggregate(pipeline)
    }


def get_budget_summary(start_date, end_date): # Minimal first version of budget summary
    start = _parse_date(start_date)
    end = _parse_date(end_date)

    total_spending = get_total_spending(start, end)
    matching_goals = goals.find({
        "start_date": {"$lt": end},
        "end_date": {"$gte": start},
    })

    budgets = []

    for raw_goal in matching_goals:
        goal = serialize_document(raw_goal)

        if goal["type"] != "spending_limit":
            continue

        target = float(goal["target"])

        budgets.append({
            "goal_id": goal["id"],
            "name": goal["name"],
            "target": target,
            "spent": total_spending,
            "remaining": round(target - total_spending, 2),
            "progress_percent": (
                round(total_spending / target * 100, 2)
                if target > 0 else None
            ),
        })

    return {
        "period": {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        },
        "total_spending": total_spending,
        "budgets": budgets,
        "savings_progress": [],
    }
