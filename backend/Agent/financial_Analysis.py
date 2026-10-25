
"""
financial_analysis.py
Runs periodic financial analysis and updates long-term memories.
"""

from datetime import datetime, timedelta, timezone

from database.finance import (
    get_total_spending,
    get_category_totals,
)
from database.database import (
    get_goals,
    mark_analysis_success,
    mark_analysis_failure,
)
from Agent.memory_engine import upsert_memory


def run_financial_analysis(user_id: str) -> dict:
    """Analyze recent spending and save supported financial memories."""

    try:
        today = datetime.now(timezone.utc).date()
        start_date = (today - timedelta(days=30)).isoformat()
        end_date = today.isoformat()

        total = float(get_total_spending(start_date, end_date))
        category_totals = get_category_totals(start_date, end_date)
        goals = get_goals(limit=100)

        categories = [
            {
                "category": str(category),
                "amount": round(float(amount), 2),
                "percentage": round(
                    float(amount) / total * 100, 2
                ) if total > 0 else 0.0,
            }
            for category, amount in category_totals.items()
        ]

        categories.sort(
            key=lambda item: item["amount"],
            reverse=True,
        )

        candidates = []

        # Save a supported observation about the largest category.
        if categories and total > 0:
            largest = categories[0]

            candidates.append({
                "type": "observed_pattern",
                "condition": "largest spending category in the last 30 days",
                "value": (
                    f"{largest['category']} accounted for "
                    f"{largest['percentage']}% of spending "
                    f"(₹{largest['amount']:.2f})"
                ),
                "source": "financial_analysis",
                "confidence": 0.95,
            })

        # Save the spending summary only when there is spending.
        if total > 0:
            candidates.append({
                "type": "observed_pattern",
                "condition": "total spending in the last 30 days",
                "value": f"₹{total:.2f}",
                "source": "financial_analysis",
                "confidence": 1.0,
            })

        saved_memories = [
            upsert_memory(candidate)
            for candidate in candidates
        ]

        # Mark success only after calculations and memory updates finish.
        mark_analysis_success(user_id)

        return {
            "period_start": start_date,
            "period_end_exclusive": end_date,
            "total_spending": round(total, 2),
            "category_breakdown": categories,
            "largest_category": (
                categories[0]["category"] if categories else None
            ),
            "goals": goals,
            "memories_updated": len(saved_memories),
        }

    except Exception:
        mark_analysis_failure(user_id)
        raise
