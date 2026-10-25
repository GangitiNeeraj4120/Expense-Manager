
"""
database_tools.py
Exposes safe, read-only financial and memory queries
as tools that the SpendSense LLM can call.
"""

from langchain_core.tools import tool
from .pattern_analysis import (detect_recurring_expenses,
                              spending_trends,
                              detect_spending_anomalies,
                              detect_behavioural_patterns,
                              generate_goal_recommendations
                              )
from database.database import (
    get_transactions,
    get_memories,
    get_goals,
    add_transaction,
    save_goal,
)
from database.finance import get_total_spending, get_category_totals
from database.finance import (
    get_total_spending,
    get_category_totals,
    get_budget_summary,
)

@tool
def fetch_spending_insights(start_date : str="",
                           end_date : str="",)->dict:
    """Analyze spending for a date range. Returns total spending,
    category amounts, percentages, and the largest spending category.
    Use this for questions about spending habits, category comparisons,
    and where the user spends the most."""

    start = start_date or None
    end = end_date or None

    total = float(get_total_spending(start, end))
    category_totals = get_category_totals(start, end)

    breakdown = []
    for category, amount in category_totals.items():
        amount = float(amount)
        percentage = (amount / total * 100) if total > 0 else 0.0

        breakdown.append({
            "category": category,
            "amount": round(amount, 2),
            "percentage": round(percentage, 2),
        })

    breakdown.sort(key=lambda item: item["amount"], reverse=True)

    return {
        "start_date": start_date or None,
        "end_date": end_date or None,
        "total_spending": round(total, 2),
        "category_breakdown": breakdown,
        "largest_category": (
            breakdown[0]["category"] if breakdown else None
        ),
    }
@tool
def fetch_transactions(
    start_date: str = "",
    end_date: str = "",
    category: str = "",
    limit: int = 50,
) -> list[dict]:
    """Retrieve transactions, optionally filtered by dates and category.

    Dates should be ISO-formatted, such as 2026-10-01.
    The end date is exclusive.
    """
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    return get_transactions(
        start_date=start_date or None,
        end_date=end_date or None,
        category=category or None,
        limit=limit,
    )


@tool
def fetch_total_spending(
    start_date: str = "",
    end_date: str = "",
) -> dict:
    """Calculate total spending over an optional date range."""
    total = get_total_spending(
        start_date=start_date or None,
        end_date=end_date or None,
    )
    return {"total_spending": total, "currency": "INR"}


@tool
def fetch_category_totals(
    start_date: str = "",
    end_date: str = "",
) -> dict:
    """Calculate spending totals grouped by category."""
    totals = get_category_totals(
        start_date=start_date or None,
        end_date=end_date or None,
    )
    return {
        "category_totals": totals,
        "currency": "INR",
    }


@tool
def fetch_goals(
    goal_type: str = "",
    start_date: str = "",
    end_date: str = "",
    limit: int = 50,
) -> list[dict]:
    """Retrieve savings targets or spending-limit goals."""
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    return get_goals(
        goal_type=goal_type or None,
        start_date=start_date or None,
        end_date=end_date or None,
        limit=limit,
    )


@tool
def fetch_budget_summary(
    start_date: str,
    end_date: str,
) -> dict:
    """Summarize spending against spending-limit goals for a period."""
    return get_budget_summary(
        start_date=start_date,
        end_date=end_date,
    )


@tool
def fetch_memories(
    memory_type: str = "",
    status: str = "active",
    limit: int = 50,
) -> list[dict]:
    """Retrieve stored memories filtered by type and status."""
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    return get_memories(
        type=memory_type or None,
        status=status or None,
        limit=limit,
    )

@tool
def record_expense(
    amount: float,
    merchant: str,
    category: str,
    date: str,
    context: str = "",
) -> dict:
    """Record a new expense in INR.

    Use this when the user says they spent or paid money.
    Required: amount, merchant, category, and date in ISO format.
    Ask the user for missing essential information rather than inventing it.
    """
    try:
        saved = add_transaction(
            amount=amount,
            merchant=merchant,
            category=category,
            date=date,
            context=context,
        )
        return {
            "success": True,
            "message": "Expense saved successfully.",
            "transaction": saved,
        }
    except (ValueError, TypeError) as exc:
        return {
            "success": False,
            "message": str(exc),
        }

@tool
def fetch_spending_trends() -> dict:
    """Compare category spending over the latest 30 days
    with the preceding 30 days."""
    return {"trends": spending_trends()}


@tool
def fetch_recurring_expenses() -> dict:
    """Identify potential monthly recurring expenses."""
    return {"recurring_expenses": detect_recurring_expenses()}


@tool
def fetch_spending_anomalies() -> dict:
    """Find unusually large transactions relative to
    historical spending in their categories."""
    return {"anomalies": detect_spending_anomalies()}


@tool
def fetch_behavioural_patterns() -> dict:
    """Compare average daily spending on weekdays and weekends."""
    return detect_behavioural_patterns()


@tool
def fetch_goal_recommendations() -> dict:
    """Compare recent spending with spending-limit goals."""
    return {
        "recommendations": generate_goal_recommendations()
    }
@tool
def record_goal(
    Name:str,
    Goal_type:str,
    Target:float,
    start_date:str,
    end_date:str
    )-> dict:
    """Create a new financial goal and save it to the database.

    Args:
        name: Name of the goal.
        target: Target spending limit or savings amount.
        goal_type: Type of financial goal.
        start_date: Goal start date in YYYY-MM-DD format.
        end_date: Goal end date in YYYY-MM-DD format.

    Returns:
        The saved goal document or an error message.
    """
    try:
        saved = save_goal({
            "name": Name,
            "type": Goal_type,
            "target": Target,
            "start_date": start_date,
            "end_date": end_date,
        })
        return {
            "success": True,
            "message": "Goal created successfully.",
            "goal": saved,
        }
    except (ValueError, TypeError) as exc:
        return {"success": False, 
                "message": str(exc),
            }
    
      



# All read-only tools available to the agent.
FINANCIAL_TOOLS = [
    fetch_transactions,
    fetch_total_spending,
    fetch_category_totals,
    fetch_goals,
    fetch_budget_summary,
    fetch_memories,
    fetch_spending_insights,
    record_expense,
    fetch_spending_trends,
    fetch_recurring_expenses,
    fetch_spending_anomalies,
    fetch_behavioural_patterns,
    fetch_goal_recommendations,
    record_goal,
]
