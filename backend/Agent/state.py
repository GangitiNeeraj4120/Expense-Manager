
"""
state.py
Defines the shared state for the SpendSense LangGraph workflow.
"""

from typing import Any, TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    # User and conversation
    user_id: str
    message: str
    messages : Annotated[list[AnyMessage],add_messages]
    # Data retrieved from MongoDB
    transactions: list[dict[str, Any]]

    # Relevant long-term memories retrieved for this request
    relevant_memories: list[dict[str, Any]]

    # Patterns discovered from financial data
    insights: list[dict[str, Any]]

    # Follow-up question workflow
    question: str | None
    user_response: str | None

    # Proposed changes to long-term memory
    proposed_memory_updates: list[dict[str, Any]]

    # Final response returned to the user
    answer: str

    analysis_refresh_status: str
    analysis_refresh_message: str
    financial_analysis: dict[str, Any]
