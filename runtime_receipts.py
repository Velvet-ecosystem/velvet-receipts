# SPDX-License-Identifier: GPL-3.0-only
"""Canonical Court, safety, execution, and integration receipt construction."""

from __future__ import annotations

from typing import Any, Mapping

from receipt import Receipt
from ghost_can_receipts import (
    GHOST_CAN_OBSERVATION_EVENT,
    ghost_can_receipt_from_envelope,
)
from distributed_work_receipts import (
    DISTRIBUTED_WORK_RECEIPT_EVENTS,
    distributed_work_receipt_from_envelope,
)

COURT_EVENTS = {
    "COURT_AUTHORIZED",
    "COURT_DENIED",
}

SAFETY_EVENTS = {
    "SAFETY_APPROVED",
    "SAFETY_DENIED",
    "SAFETY_FAILED",
}

EXECUTION_EVENTS = {
    "EXECUTION_STARTED",
    "EXECUTION_COMPLETED",
    "EXECUTION_FAILED",
    "EXECUTION_DENIED",
}

GHOST_OBSERVATION_EVENTS = {GHOST_CAN_OBSERVATION_EVENT}

CAPABILITY_EVENTS = {
    "CAPABILITY_AVAILABLE",
    "CAPABILITY_REFUSED",
}

RESOURCE_EVENTS = {
    "RESOURCE_POSTURE_OBSERVED",
}

PRESENCE_EVENTS = {
    "PRESENCE_FUSION_ACCEPTED",
    "PRESENCE_FUSION_REJECTED",
}

RUNTIME_RECEIPT_EVENTS = (
    COURT_EVENTS
    | SAFETY_EVENTS
    | EXECUTION_EVENTS
    | GHOST_OBSERVATION_EVENTS
    | DISTRIBUTED_WORK_RECEIPT_EVENTS
    | CAPABILITY_EVENTS
    | RESOURCE_EVENTS
    | PRESENCE_EVENTS
)


def runtime_receipt_from_envelope(envelope: Mapping[str, Any]) -> Receipt:
    """Create one canonical Runtime accountability receipt.

    The envelope is evidence input from trusted Runtime wiring. This function
    validates and normalizes it into the stable Velvet Receipt model. It does
    not authorize, execute, publish, place, lease, or unlock anything.
    """
    if not isinstance(envelope, Mapping):
        raise TypeError("runtime receipt envelope must be a mapping")

    event_type = _required_text(envelope, "event_type")
    if event_type not in RUNTIME_RECEIPT_EVENTS:
        raise ValueError(
            "unsupported runtime receipt event_type: %s" % event_type
        )

    if event_type == GHOST_CAN_OBSERVATION_EVENT:
        return ghost_can_receipt_from_envelope(envelope)
    if event_type in DISTRIBUTED_WORK_RECEIPT_EVENTS:
        return distributed_work_receipt_from_envelope(envelope)

    source = _required_text(envelope, "source")
    subject_id = _required_text(envelope, "subject_id")
    payload = envelope.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("runtime receipt payload must be a mapping")
    payload = dict(payload)

    decision, authority, domain = _classification(event_type)
    state = payload.get("state", "unknown")
    if not isinstance(state, str) or not state.strip():
        raise ValueError(
            "runtime receipt payload state must be a non-empty string"
        )

    context = {
        "schema": "velvet.runtime.receipt.v1",
        "source": source,
        "subject_id": subject_id,
        **payload,
    }

    constraints = {
        "local_only": True,
        "court_required": event_type not in SAFETY_EVENTS,
        "token_required": (
            event_type in SAFETY_EVENTS or event_type in EXECUTION_EVENTS
        ),
        "safety_gate_required": event_type in EXECUTION_EVENTS,
        "approved_executor_required": event_type in EXECUTION_EVENTS,
        "receipt_is_evidence_not_authority": True,
    }

    return Receipt(
        event=event_type,
        decision=decision,
        result=state.strip(),
        policy=_policy(event_type),
        authorized_by=authority,
        context=context,
        constraints=constraints,
        domain=domain,
        notes=(
            "Runtime-path evidence. This receipt does not independently "
            "grant authority."
        ),
    )


def _policy(event_type: str) -> str:
    if event_type in CAPABILITY_EVENTS:
        return "RuntimeCapabilityRegistry"
    if event_type in RESOURCE_EVENTS:
        return "RuntimeResourceGuard"
    if event_type in PRESENCE_EVENTS:
        return "PresenceFusionEvidence"
    return "RuntimeExecutionContract"


def _classification(event_type: str):
    if event_type == "COURT_AUTHORIZED":
        return "allow", "Court", "authorization"
    if event_type == "COURT_DENIED":
        return "deny", "Court", "authorization"
    if event_type == "SAFETY_APPROVED":
        return "approve_conditions", "SafetyGate", "safety"
    if event_type in {"SAFETY_DENIED", "SAFETY_FAILED"}:
        return "deny_conditions", "SafetyGate", "safety"
    if event_type == "EXECUTION_STARTED":
        return "begin", "ApprovedExecutor", "execution"
    if event_type == "EXECUTION_COMPLETED":
        return "complete", "ApprovedExecutor", "execution"
    if event_type == "EXECUTION_FAILED":
        return "fail", "ApprovedExecutor", "execution"
    if event_type == "EXECUTION_DENIED":
        return "deny", "ApprovedExecutor", "execution"
    if event_type == "CAPABILITY_AVAILABLE":
        return (
            "observe_available",
            "RuntimeCapabilityRegistry",
            "capability",
        )
    if event_type == "CAPABILITY_REFUSED":
        return "refuse", "RuntimeCapabilityRegistry", "capability"
    if event_type == "RESOURCE_POSTURE_OBSERVED":
        return "observe_posture", "RuntimeResourceGuard", "resource"
    if event_type == "PRESENCE_FUSION_ACCEPTED":
        return "accept_evidence", "PresenceFusion", "presence"
    if event_type == "PRESENCE_FUSION_REJECTED":
        return "reject_evidence", "PresenceFusion", "presence"
    raise ValueError(
        "unsupported runtime receipt classification: %s" % event_type
    )


def _required_text(document: Mapping[str, Any], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be a non-empty string" % key)
    return value.strip()
