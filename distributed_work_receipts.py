# SPDX-License-Identifier: GPL-3.0-only
"""Canonical evidence receipts for distributed-node workload cooperation.

These receipts preserve Runtime placement, refusal, handoff, completion,
recovery, and degradation evidence. They never create workload leases, grant
Court authority, select executors, or authorize actuation.
"""

from __future__ import annotations

from typing import Any, Mapping, Set

from receipt import Receipt


NODE_ADVERTISEMENT_PUBLISHED = "NODE_ADVERTISEMENT_PUBLISHED"
WORK_OFFERED = "WORK_OFFERED"
WORK_ACCEPTED = "WORK_ACCEPTED"
WORK_REFUSED = "WORK_REFUSED"
WORK_HANDOFF_REQUESTED = "WORK_HANDOFF_REQUESTED"
WORK_COMPLETED = "WORK_COMPLETED"
WORK_DEGRADED = "WORK_DEGRADED"
WORK_RECOVERY_REASSIGNED = "WORK_RECOVERY_REASSIGNED"

DISTRIBUTED_WORK_RECEIPT_SCHEMA = "velvet.receipts.distributed-work.v1"
DISTRIBUTED_WORK_RECEIPT_EVENTS = {
    NODE_ADVERTISEMENT_PUBLISHED,
    WORK_OFFERED,
    WORK_ACCEPTED,
    WORK_REFUSED,
    WORK_HANDOFF_REQUESTED,
    WORK_COMPLETED,
    WORK_DEGRADED,
    WORK_RECOVERY_REASSIGNED,
}

_FORBIDDEN_AUTHORITY_KEYS = {
    "action",
    "actuate",
    "actuation",
    "authorized_by",
    "capability_token",
    "command",
    "court_token",
    "execution_token",
    "executor",
    "executor_name",
    "hardware_handle",
    "hardware_target",
    "permit",
    "shell",
    "token",
}

_REQUIRED_TRANSPORT_FLAGS = {
    "transport_only": True,
    "canonical": False,
    "authority": "none",
    "grants_authority": False,
    "grants_execution": False,
    "grants_actuation": False,
}


class DistributedWorkReceiptError(ValueError):
    """Raised when distributed-work evidence violates its receipt contract."""


def distributed_work_receipt_from_envelope(envelope: Mapping[str, Any]) -> Receipt:
    """Build one canonical receipt from a validated distributed-work event.

    The caller supplies evidence emitted through trusted Runtime/Event Protocol
    wiring. This function validates the authority boundary and normalizes that
    evidence into the shared Receipt model.
    """

    if not isinstance(envelope, Mapping):
        raise TypeError("distributed-work receipt envelope must be a mapping")

    event_type = _required_text(envelope, "event_type")
    if event_type not in DISTRIBUTED_WORK_RECEIPT_EVENTS:
        raise DistributedWorkReceiptError(
            f"unsupported distributed-work receipt event_type: {event_type}"
        )

    source = _required_text(envelope, "source")
    subject_id = _required_text(envelope, "subject_id")
    payload_value = envelope.get("payload")
    if not isinstance(payload_value, Mapping):
        raise DistributedWorkReceiptError(
            "distributed-work receipt payload must be a mapping"
        )
    payload = dict(payload_value)

    _validate_transport_boundary(payload)
    forbidden = _find_forbidden_keys(payload)
    if forbidden:
        raise DistributedWorkReceiptError(
            "distributed-work receipt contains forbidden authority fields: "
            f"{sorted(forbidden)}"
        )
    _validate_event_payload(event_type, subject_id, payload)

    decision, result, recorder, domain = _classification(event_type, payload)
    context = {
        "schema": DISTRIBUTED_WORK_RECEIPT_SCHEMA,
        "source": source,
        "subject_id": subject_id,
        "event_contract": "velvet.distributed-work-events.v1",
        **payload,
    }
    constraints = {
        "local_only": True,
        "verified_event_contract_required": True,
        "runtime_placement_required": True,
        "handoff_transfers_no_authority": True,
        "court_remains_independent": True,
        "executor_contract_remains_independent": True,
        "ordinary_load_balancing_is_not_lineage": True,
        "receipt_is_evidence_not_authority": True,
        "no_actuation_authority": True,
    }

    return Receipt(
        event=event_type,
        decision=decision,
        result=result,
        policy="DistributedWorkEvidenceContract",
        authorized_by=recorder,
        context=context,
        constraints=constraints,
        domain=domain,
        notes=(
            "Distributed workload evidence. This receipt records what Runtime "
            "reported and does not grant placement, execution, Court, or "
            "actuation authority."
        ),
    )


def _classification(
    event_type: str, payload: Mapping[str, Any]
) -> tuple[str, str, str, str]:
    if event_type == NODE_ADVERTISEMENT_PUBLISHED:
        return (
            "record_advertisement",
            _required_payload_text(payload, "availability"),
            "RuntimeNodeRegistry",
            "distributed-node",
        )
    if event_type == WORK_OFFERED:
        return "record_offer", "offered", "RuntimePlacement", "distributed-work"
    if event_type == WORK_ACCEPTED:
        return (
            "record_lease",
            _required_payload_text(payload, "placement_mode"),
            "RuntimePlacement",
            "distributed-work",
        )
    if event_type == WORK_REFUSED:
        return "record_refusal", "refused", "RuntimePlacement", "distributed-work"
    if event_type == WORK_HANDOFF_REQUESTED:
        return (
            "record_handoff",
            "handoff_requested",
            "RuntimePlacement",
            "distributed-work",
        )
    if event_type == WORK_COMPLETED:
        return (
            "record_result",
            _required_payload_text(payload, "result_status"),
            "RuntimeEvidencePath",
            "distributed-work",
        )
    if event_type == WORK_DEGRADED:
        return (
            "record_degradation",
            _required_payload_text(payload, "degradation_mode"),
            "RuntimePlacement",
            "distributed-work",
        )
    return (
        "record_recovery",
        "reassigned",
        "RuntimePlacement",
        "distributed-work",
    )


def _validate_transport_boundary(payload: Mapping[str, Any]) -> None:
    for key, expected in _REQUIRED_TRANSPORT_FLAGS.items():
        if payload.get(key) != expected:
            raise DistributedWorkReceiptError(
                f"distributed-work payload {key} must be {expected!r}"
            )


def _validate_event_payload(
    event_type: str, subject_id: str, payload: Mapping[str, Any]
) -> None:
    if event_type == NODE_ADVERTISEMENT_PUBLISHED:
        node_id = _required_payload_text(payload, "node_id")
        if subject_id != node_id:
            raise DistributedWorkReceiptError(
                "node advertisement subject_id must match node_id"
            )
        for key in ("body_id", "organ", "tier", "availability"):
            _required_payload_text(payload, key)
        _required_text_list(payload, "capabilities", allow_empty=False)
        _required_ratio(payload, "current_load")
        _required_ratio(payload, "health")
        _required_non_negative_number(payload, "last_heartbeat")
        _required_task_limits(payload)
        return

    work_id = _required_payload_text(payload, "work_id")
    if subject_id != work_id:
        raise DistributedWorkReceiptError(
            "work receipt subject_id must match work_id"
        )
    _required_payload_text(payload, "work_class")
    _required_text_list(payload, "required_capabilities", allow_empty=True)

    if event_type == WORK_OFFERED:
        _required_text_list(payload, "required_capabilities", allow_empty=False)
    elif event_type == WORK_ACCEPTED:
        for key in ("node_id", "organ", "placement_mode", "lease_id"):
            _required_payload_text(payload, key)
        _required_non_negative_number(payload, "lease_expires_at")
    elif event_type == WORK_REFUSED:
        for key in ("node_id", "organ", "reason"):
            _required_payload_text(payload, key)
    elif event_type == WORK_HANDOFF_REQUESTED:
        if not _optional_text(payload, "from_node_id") and not _optional_text(
            payload, "node_id"
        ):
            raise DistributedWorkReceiptError(
                "handoff receipt requires a source node"
            )
        _required_payload_text(payload, "reason")
    elif event_type == WORK_COMPLETED:
        for key in ("node_id", "organ", "result_status"):
            _required_payload_text(payload, key)
    elif event_type == WORK_DEGRADED:
        _required_payload_text(payload, "degradation_mode")
        _required_payload_text(payload, "reason")
    elif event_type == WORK_RECOVERY_REASSIGNED:
        for key in (
            "from_node_id",
            "to_node_id",
            "placement_mode",
            "lease_id",
            "reason",
        ):
            _required_payload_text(payload, key)
        _required_non_negative_number(payload, "lease_expires_at")


def _required_task_limits(payload: Mapping[str, Any]) -> None:
    maximum = payload.get("max_concurrent_tasks")
    current = payload.get("current_tasks")
    if isinstance(maximum, bool) or not isinstance(maximum, int) or maximum < 1:
        raise DistributedWorkReceiptError(
            "max_concurrent_tasks must be a positive integer"
        )
    if isinstance(current, bool) or not isinstance(current, int):
        raise DistributedWorkReceiptError("current_tasks must be an integer")
    if not 0 <= current <= maximum:
        raise DistributedWorkReceiptError(
            "current_tasks must fit the declared task limit"
        )


def _required_ratio(payload: Mapping[str, Any], key: str) -> float:
    value = _required_number(payload, key)
    if not 0.0 <= value <= 1.0:
        raise DistributedWorkReceiptError(f"{key} must be between 0 and 1")
    return value


def _required_non_negative_number(
    payload: Mapping[str, Any], key: str
) -> float:
    value = _required_number(payload, key)
    if value < 0.0:
        raise DistributedWorkReceiptError(f"{key} cannot be negative")
    return value


def _required_number(payload: Mapping[str, Any], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DistributedWorkReceiptError(f"{key} must be numeric")
    return float(value)


def _required_text_list(
    payload: Mapping[str, Any], key: str, *, allow_empty: bool
) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, (list, tuple)):
        raise DistributedWorkReceiptError(f"{key} must be a list")
    if not allow_empty and not value:
        raise DistributedWorkReceiptError(f"{key} cannot be empty")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise DistributedWorkReceiptError(
            f"{key} must contain non-empty strings"
        )
    return list(value)


def _optional_text(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise DistributedWorkReceiptError(
            f"{key} must be a non-empty string when present"
        )
    return value.strip()


def _required_payload_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DistributedWorkReceiptError(f"{key} must be a non-empty string")
    return value.strip()


def _required_text(document: Mapping[str, Any], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DistributedWorkReceiptError(f"{key} must be a non-empty string")
    return value.strip()


def _find_forbidden_keys(value: Any, path: str = "payload") -> Set[str]:
    found: Set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in _FORBIDDEN_AUTHORITY_KEYS:
                found.add(f"{path}.{key}")
            found.update(_find_forbidden_keys(child, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found.update(_find_forbidden_keys(child, f"{path}[{index}]"))
    return found
