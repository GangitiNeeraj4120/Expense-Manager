
"""
agent.py
Terminal entry point for the SpendSense AI agent.
"""

from uuid import uuid4

from .graph import build_graph


def main():
    # A unique ID identifies this conversation.
    thread_id = str(uuid4())

    # Replace this with the authenticated user's ID
    # when integrating with the actual application.
    user_id = input("Enter user ID: ").strip()

    if not user_id:
        print("User ID cannot be empty.")
        return

    # Build the LangGraph application.
    graph = build_graph()

    # Configuration is passed to LangGraph's checkpointer.
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id,
        }
    }

    print("\nSpendSense Agent")
    print("Type 'exit' to quit.")
    print(f"Conversation ID: {thread_id}\n")

    while True:
        message = input("You: ").strip()

        if message.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not message:
            continue

        try:
            result = graph.invoke(
                {
                    "user_id": user_id,
                    "message": message,
                },
                config=config,
            )

            answer = result.get(
                "answer",
                "I couldn't generate a response."
            )

            print(f"\nSpendSense: {answer}\n")

        except Exception as exc:
            print(f"\nError running the agent: {exc}\n")


if __name__ == "__main__":
    main()
