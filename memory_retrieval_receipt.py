# SPDX-License-Identifier: GPL-3.0-only
"""Receipt builder for completed memory retrieval."""

from typing import Any, Iterable, Mapping

from memory_link import validate_memory_link
from runtime_receipts import runtime_receipt_from_envelope


def memory_retrieval_receipt_from_envelope(
    envelope: Mapping[str, Any],
    memory_links: Iterable[Mapping[str, Any]],
):
    if not isinstance(envelope, Mapping):
        raise TypeError("envelope must be a mapping")
    if envelope.get("event_type") != "EXECUTION_COMPLETED":
        raise ValueError("event_type must be EXECUTION_COMPLETED")

    payload = envelope.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be a mapping")
    if payload.get("capability") != "observe.memory":
        raise ValueError("capability must be observe.memory")
    if payload.get("target") != "memory":
        raise ValueError("target must be memory")
    if payload.get("executor_name") != "memory-recall":
        raise ValueError("executor_name must be memory-recall")

    query_event_id = _text(payload.get("query_event_id"), "query_event_id")
    result_count = payload.get("result_count")
    if isinstance(result_count, bool) or not isinstance(result_count, int) or result_count < 0:
        raise ValueError("result_count must be a non-negative integer")

    links = [validate_memory_link(item) for item in memory_links]
    if len(links) != result_count:
        raise ValueError("memory link count must match result_count")

    normalized = dict(envelope)
    normalized["payload"] = {
        "state": payload.get("state", "completed"),
        "intent_id": payload.get("intent_id"),
        "token_id": payload.get("token_id"),
        "capability": "observe.memory",
        "target": "memory",
        "executor_name": "memory-recall",
        "query_event_id": query_event_id,
        "result_count": result_count,
        "memory_links": links,
        "private_memory_included": False,
    }
    receipt = runtime_receipt_from_envelope(normalized)
    receipt.constraints["memory_payload_forbidden"] = True
    receipt.constraints["memory_links_are_context_not_authority"] = True
    return receipt


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))
    return value.strip()
