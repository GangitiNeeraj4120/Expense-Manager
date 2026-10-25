
"""
memory_engine.py

Memory operations for SpendSense.
Uses the existing MongoDB persistence functions.
"""

from datetime import datetime, timezone
from typing import Any


from database.database import (
    get_memories,
    save_memory,
    memories,
    serialize_document,
)

VALID_MEMORY_TYPES = {
    "semantic",
    "observed_pattern",
    "user_confirmed",
    "preference",
}


def retrieve_memories(
    memory_type: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Retrieve active memories from MongoDB."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    if memory_type is not None and memory_type not in VALID_MEMORY_TYPES:
        raise ValueError(f"Unsupported memory type: {memory_type}")

    return get_memories(
        type=memory_type,
        status="active",
        limit=limit,
    )


def save_memories(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Validate and save proposed memories.

    This initial version inserts records. Deduplication and
    updating existing memories will be added in the next stage.
    """
    saved = []
    return [upsert_memory(candidate) for candidate in candidates]


def upsert_memory(candidate: dict) -> dict:
    """
    Insert a new memory or update an existing memory
    with the same type and condition.

    Explicit user corrections take priority over
    automatically inferred patterns.
    """
    memory_type = candidate.get("type")
    condition = candidate.get("condition", "").strip()
    value = candidate.get("value", "").strip()
    source = candidate.get("source", "financial_analysis")
    confidence = candidate.get("confidence", 0.5)

    if memory_type not in VALID_MEMORY_TYPES:
        raise ValueError(f"Unsupported memory type: {memory_type}")

    if not condition or not value:
        raise ValueError("Memory condition and value are required")

    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")

    # Find an existing active memory with the same meaning.
    existing = memories.find_one({
        "type": memory_type,
        "condition": condition,
        "status": "active",
    })

    now = datetime.now(timezone.utc)

    if existing:
        old_source = existing.get("source", "")
        old_confidence = existing.get("confidence", 0.0)

        # Don't replace an explicit correction with an inference.
        if (
            old_source == "user_correction"
            and source != "user_correction"
        ):
            return serialize_document(existing)

        # Keep stronger existing information unless the user
        # explicitly corrects it.
        if (
            source != "user_correction"
            and confidence < old_confidence
        ):
            return serialize_document(existing)

        memories.update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "value": value,
                    "source": source,
                    "confidence": float(confidence),
                    "updated_at": now,
                }
            },
        )

        updated = memories.find_one({"_id": existing["_id"]})
        return serialize_document(updated)

    new_memory = {
        "type": memory_type,
        "condition": condition,
        "value": value,
        "source": source,
        "confidence": float(confidence),
        "status": candidate.get("status", "active"),
        "created_at": now,
    }

    return save_memory(new_memory)


def get_context(
    memory_type: str | None = None,
    limit: int = 20,
) -> str:
    """Format stored memories into context suitable for an LLM prompt."""
    memories = retrieve_memories(
        memory_type=memory_type,
        limit=limit,
    )

    if not memories:
        return "No stored memories are available."

    lines = []

    for memory in memories:
        lines.append(
            f"- Type: {memory.get('type', 'unknown')}; "
            f"Condition: {memory.get('condition', '')}; "
            f"Value: {memory.get('value', '')}; "
            f"Source: {memory.get('source', 'unknown')}; "
            f"Confidence: {memory.get('confidence', 0.5)}"
        )

    return "\n".join(lines)
