
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from statistics import median

from database.database import transactions, goals


def load_transactions(days=180):
    """Load transactions from the requested historical period."""

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    return list(transactions.find({
        "date": {
            "$gte": start,
            "$lt": end
        }
    }).sort("date", 1))


def spending_trends():
    """Compare spending in the latest 30 days with the
    preceding 30 days."""

    now = datetime.now(timezone.utc)
    current_start = now - timedelta(days=30)
    previous_start = now - timedelta(days=60)

    current = list(transactions.find({
        "date": {"$gte": current_start, "$lt": now}
    }))

    previous = list(transactions.find({
        "date": {
            "$gte": previous_start,
            "$lt": current_start
        }
    }))

    def totals(records):
        result = defaultdict(float)

        for transaction in records:
            result[transaction["category"]] += float(
                transaction["amount"]
            )

        return dict(result)

    current_totals = totals(current)
    previous_totals = totals(previous)

    categories = set(current_totals) | set(previous_totals)
    insights = []

    for category in categories:
        current_amount = current_totals.get(category, 0)
        previous_amount = previous_totals.get(category, 0)

        if previous_amount == 0:
            continue

        change = (
            (current_amount - previous_amount)
            / previous_amount
        ) * 100

        insights.append({
            "category": category,
            "current_spending": round(current_amount, 2),
            "previous_spending": round(previous_amount, 2),
            "change_percent": round(change, 2)
        })

    return sorted(
        insights,
        key=lambda item: abs(item["change_percent"]),
        reverse=True
    )


def detect_recurring_expenses():
    """Identify merchants with repeated transactions
    at approximately monthly intervals."""

    records = load_transactions(180)
    merchants = defaultdict(list)

    for transaction in records:
        merchant = transaction.get("merchant", "").strip().lower()

        if merchant:
            merchants[merchant].append(transaction)

    recurring = []

    for merchant, items in merchants.items():
        items.sort(key=lambda item: item["date"])

        if len(items) < 3:
            continue

        monthly_intervals = 0

        for first, second in zip(items, items[1:]):
            days = (
                second["date"] - first["date"]
            ).total_seconds() / 86400

            if 25 <= days <= 35:
                monthly_intervals += 1

        if monthly_intervals >= 2:
            recurring.append({
                "merchant": merchant,
                "occurrences": len(items),
                "total_spending": round(
                    sum(float(t["amount"]) for t in items), 2
                ),
                "average_amount": round(
                    sum(float(t["amount"]) for t in items)
                    / len(items), 2
                )
            })

    return recurring


def detect_spending_anomalies():
    """Identify unusually large transactions relative
    to historical spending in the same category."""

    records = load_transactions(180)

    by_category = defaultdict(list)

    for transaction in records:
        by_category[transaction["category"]].append(transaction)

    anomalies = []

    for category, items in by_category.items():
        if len(items) < 6:
            continue

        amounts = [float(item["amount"]) for item in items]
        center = median(amounts)

        deviations = [abs(amount - center) for amount in amounts]
        mad = median(deviations)

        # Skip categories with no historical variation.
        if mad == 0:
            continue

        threshold = center + (3 * 1.4826 * mad)

        for item in items:
            amount = float(item["amount"])

            if amount > threshold:
                anomalies.append({
                    "merchant": item.get("merchant", "Unknown"),
                    "category": category,
                    "amount": round(amount, 2),
                    "historical_median": round(center, 2),
                    "date": item["date"].isoformat()
                })

    return anomalies


def detect_behavioural_patterns():
    """Compare average daily spending on weekdays and weekends."""

    records = load_transactions(90)

    if not records:
        return {"message": "No transactions available."}

    weekday_total = 0.0
    weekend_total = 0.0

    for transaction in records:
        amount = float(transaction["amount"])

        if transaction["date"].weekday() >= 5:
            weekend_total += amount
        else:
            weekday_total += amount

    # Use calendar days rather than transaction counts.
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=90)

    weekday_days = sum(
        1 for offset in range(90)
        if (start + timedelta(days=offset)).weekday() < 5
    )
    weekend_days = 90 - weekday_days

    weekday_average = weekday_total / weekday_days
    weekend_average = weekend_total / weekend_days

    return {
        "weekday_average_daily_spending": round(
            weekday_average, 2
        ),
        "weekend_average_daily_spending": round(
            weekend_average, 2
        ),
        "weekend_vs_weekday_change_percent": round(
            ((weekend_average - weekday_average)
             / weekday_average * 100)
            if weekday_average else 0,
            2
        )
    }


def generate_goal_recommendations():
    """Compare recent spending against active spending limits."""

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=30)

    records = list(transactions.find({
        "date": {"$gte": start, "$lt": now}
    }))

    total_spending = sum(
        float(item["amount"]) for item in records
    )

    active_goals = list(goals.find({
        "type": "spending_limit",
        "start_date": {"$lt": now},
        "end_date": {"$gte": now}
    }))

    recommendations = []

    for goal in active_goals:
        target = float(goal["target"])

        if total_spending > target:
            recommendations.append({
                "goal": goal["name"],
                "target": target,
                "recent_spending": round(total_spending, 2),
                "message": (
                    "Your recent 30-day spending exceeds "
                    "this goal's target. Review your spending "
                    "and check whether the goal uses a "
                    "30-day budget period."
                )
            })

    if not recommendations:
        recommendations.append({
            "message": (
                "No spending-limit goal was identified as "
                "exceeded by the recent 30-day total."
            )
        })

    return recommendations
