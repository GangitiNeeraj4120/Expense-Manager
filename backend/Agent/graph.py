
"""
graph.py
Defines the LangGraph workflow for the SpendSense AI agent.
"""
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from .state import AgentState
from langchain_core.messages import HumanMessage,SystemMessage
from .memory_engine import retrieve_memories
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode, tools_condition
from .database_tools import FINANCIAL_TOOLS
load_dotenv()
from .analysis_state import needs_analysis_refresh
from .financial_Analysis import run_financial_analysis
from .memory_engine import retrieve_memories
from langgraph.checkpoint.memory import InMemorySaver

PROMPT = """
You are SpendSense, a personal finance assistant.

Help users understand their spending, financial goals, and habits.

Rules:
-When the user reports a new expense, use the record_expense tool
 to save it. Never claim an expense was saved unless the tool
 returns success. Do not invent missing transaction details.
- Use financial tools when the user asks for information that requires
  actual financial records.
- Never invent transaction totals, budgets, goals, or memories.
- If a required tool fails because the database is unavailable,
  explain that the financial data could not be retrieved.
- Distinguish observed spending patterns from explanations confirmed
  by the user.
- Do not claim that you have saved a memory or goal unless a tool
  actually performed that operation.
- Be clear and concise.
- Financial amounts are in INR unless stated otherwise.

TOOLS:-
- Use fetch_spending_trends when comparing spending across periods.
- Use fetch_recurring_expenses to investigate repeated payments.
- Use fetch_spending_anomalies to identify unusual transactions.
- Use fetch_behavioural_patterns to compare weekday and weekend spending.
- Use fetch_goal_recommendations when evaluating spending against goals.
- Explain insights using the actual tool results.
- Do not describe a transaction as fraudulent or unnecessary
  merely because it is unusual.
- Treat recurring expenses as potential recurring payments,
  not confirmed subscriptions.
-For creating a new financial goal, use create_goal
"""


def build_graph():
    """Build and compile the SpendSense workflow."""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        api_key=api_key,
    )

    # Bind the database tools to the LLM.
    llm_with_tools = llm.bind_tools(FINANCIAL_TOOLS)
    def retrieve_memory_node(state: AgentState) -> dict:
        """Retrieve active long-term memories for the current request."""
        try:
            memories = retrieve_memories(limit=20)
        except Exception:
            # Memory retrieval should not prevent the agent from responding.
            memories = []

        return {"relevant_memories": memories}
    
    def call_llm(state: AgentState) -> dict:
       
        """Ask the LLM to answer or request a financial tool."""

        memories = state.get("relevant_memories", [])

        if memories:

            memory_context = "\n".join(
               (
                   f"- Type: {memory.get('type', 'unknown')}; "
                   f"Condition: {memory.get('condition', '')}; "
                   f"Value: {memory.get('value', '')}; "
                   f"Source: {memory.get('source', 'unknown')}; "
                   f"Confidence: {memory.get('confidence', 'unknown')}"
               )   
               for memory in memories
            )
        else:
            memory_context = "No stored memories are available."
        refresh_status = state.get("analysis_refresh_status", "unknown")
        refresh_message = state.get("analysis_refresh_message", "")

        refresh_context = (
             f"\nFinancial analysis refresh status: {refresh_status}."
        )

        if refresh_message:
            refresh_context += f"\nRefresh details: {refresh_message}"

        system_prompt = PROMPT + refresh_context
        system_prompt = (
            PROMPT
            + "\n\nRelevant long-term memory context:\n"
            + memory_context
            + "\n\nUse these memories as context, not as a substitute "
            "for current financial records. If a memory conflicts with "
            "current records, distinguish the two. Do not invent memories "
            "or claim that a memory was saved unless a tool performed "
            "that operation."
        )

        # Preserve the actual conversation and tool-call history.
        messages = [
            SystemMessage(content=system_prompt),
            *state.get("messages", []),
        ]   

        response = llm_with_tools.invoke(messages)

        return {"messages": [response]}
    
    def refresh_analysis_node(state: AgentState) -> dict:
        """Refresh financial analysis when the seven-day interval expires."""
        user_id = state.get("user_id")

        if not user_id:
            return {
               "analysis_refresh_status": "skipped",
               "analysis_refresh_message": "No user ID was supplied.",
            }
        try:
            if not needs_analysis_refresh(user_id):
                return {"analysis_refresh_status": "not_due"}

            summary = run_financial_analysis(user_id)

            return {
                "analysis_refresh_status": "success",
                "financial_analysis": summary,
            }

        except Exception as exc:
            # Keep the regular chat available if analysis fails.
            return {
               "analysis_refresh_status": "failed",
               "analysis_refresh_message": str(exc),
            }
    def prepare_message(state: AgentState) -> dict:
        message = state.get("message", "").strip()
        if not message:
            return {"answer": "Please enter a message."}

        # Start this invocation with a fresh message history.
        return {"messages": [HumanMessage(content=message)]}
    
    def generate_answer(state: AgentState) -> dict:
        """Generate a final response after tool execution."""
        messages = state.get("messages", [])
        if not messages:
            return {"answer": "I couldn't generate a response."}

        last_message = messages[-1]
        return {
            "answer": str(last_message.content)
            if last_message.content
            else "I couldn't generate a response."
        }


    builder = StateGraph(AgentState)

    builder.add_node("prepare_message", prepare_message)
    builder.add_node("refresh_analysis", refresh_analysis_node)
    builder.add_node("retrieve_memory", retrieve_memory_node)
    builder.add_node("call_llm", call_llm)
    builder.add_node("tools", ToolNode(FINANCIAL_TOOLS))
    builder.add_node("generate_answer", generate_answer)

    builder.add_edge(START, "prepare_message")
    builder.add_edge("prepare_message","refresh_analysis")
    builder.add_edge("refresh_analysis", "retrieve_memory")
    builder.add_edge("retrieve_memory","call_llm")

    builder.add_conditional_edges(
        "call_llm",
        tools_condition,
        {
            "tools": "tools",
            END: "generate_answer",
        },
    )

    builder.add_edge("tools", "call_llm")
    builder.add_edge("generate_answer", END)

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)

