# SPDX-License-Identifier: GPL-3.0-only
"""Canonical evidence receipts for Learning Mode session lifecycle activity."""

from __future__ import annotations

from typing import Any, Mapping, Set

from receipt import Receipt

SESSION_PROPOSED = "learning.session.proposed"
ELIGIBILITY_CHECKED = "learning.session.eligibility_checked"
SESSION_OPENED = "learning.session.opened"
SESSION_STUDYING = "learning.session.studying"
REVIEW_PENDING = "learning.session.review_pending"
SESSION_PAUSED = "learning.session.paused"
SESSION_DEGRADED = "learning.session.degraded"
INSUFFICIENT_EVIDENCE = "learning.session.insufficient_evidence"
SESSION_COMPLETED = "learning.session.completed"
SESSION_ABORTED = "learning.session.aborted"

LEARNING_SESSION_RECEIPT_EVENTS = {
    SESSION_PROPOSED,
    ELIGIBILITY_CHECKED,
    SESSION_OPENED,
    SESSION_STUDYING,
    REVIEW_PENDING,
    SESSION_PAUSED,
    SESSION_DEGRADED,
    INSUFFICIENT_EVIDENCE,
    SESSION_COMPLETED,
    SESSION_ABORTED,
}

LEARNING_SESSION_EVENT_CONTRACT = "velvet.learning-session-events.v1"
LEARNING_SESSION_RECEIPT_SCHEMA = "velvet.receipts.learning-session.v1"

_EVENT_STATE = {
    SESSION_PROPOSED: "PROPOSED",
    ELIGIBILITY_CHECKED: "ELIGIBILITY_CHECK",
    SESSION_OPENED: "OPEN",
    SESSION_STUDYING: "STUDYING",
    REVIEW_PENDING: "REVIEW_PENDING",
    SESSION_PAUSED: "PAUSED",
    SESSION_DEGRADED: "DEGRADED",
    INSUFFICIENT_EVIDENCE: "INSUFFICIENT_EVIDENCE",
    SESSION_COMPLETED: "COMPLETED",
    SESSION_ABORTED: "ABORTED",
}

_REQUIRED_FLAGS = {
    "transport_only": True,
    "canonical": False,
    "learning_evidence_only": True,
    "authority": "none",
    "grants_authority": False,
    "grants_memory_write": False,
    "grants_runtime_placement": False,
    "grants_execution": False,
    "grants_actuation": False,
    "applies_learning_change": False,
}

_FORBIDDEN_KEYS = {
    "objective",
    "prompt",
    "query",
    "content",
    "text",
    "transcript",
    "raw_content",
    "raw_document",
    "raw_audio",
    "raw_image",
    "web_page",
    "url",
    "network_request",
    "capability",
    "capability_token",
    "command",
    "court_decision",
    "court_token",
    "execution_token",
    "executor",
    "executor_handle",
    "hardware_handle",
    "hardware_target",
    "authorization",
    "authorized",
    "authorized_by",
    "policy_override",
    "safety_override",
    "actuation",
    "actuate",
    "shell",
}


class LearningSessionReceiptError(ValueError):
    """Raised when Learning Mode lifecycle evidence violates receipt boundaries."""


def learning_session_receipt_from_envelope(envelope: Mapping[str, Any]) -> Receipt:
    """Normalize one Learning Mode lifecycle event into canonical evidence."""
    if not isinstance(envelope, Mapping):
        raise TypeError("learning session receipt envelope must be a mapping")

    event_type = _required_text(envelope, "event_type")
    if event_type not in LEARNING_SESSION_RECEIPT_EVENTS:
        raise LearningSessionReceiptError(
            "unsupported learning session receipt event_type: %s" % event_type
        )

    source = _source(envelope)
    payload_value = envelope.get("payload")
    if not isinstance(payload_value, Mapping):
        raise LearningSessionReceiptError("learning session receipt payload must be a mapping")
    payload = dict(payload_value)
    _validate_payload(event_type, payload)

    session_id = _required_payload_text(payload, "session_id")
    decision, result = _classification(event_type)
    context = {
        "schema": LEARNING_SESSION_RECEIPT_SCHEMA,
        "source": source,
        "subject_id": session_id,
        "event_contract": LEARNING_SESSION_EVENT_CONTRACT,
        **payload,
    }
    constraints = {
        "local_only": True,
        "verified_event_contract_required": True,
        "raw_study_material_not_copied": True,
        "simulation_provenance_preserved": True,
        "learning_session_cannot_promote_memory": True,
        "learning_session_cannot_place_runtime_work": True,
        "learning_session_cannot_apply_changes": True,
        "receipt_is_evidence_not_authority": True,
        "no_command_authority": True,
        "no_actuation_authority": True,
    }

    return Receipt(
        event=event_type,
        decision=decision,
        result=result,
        policy="LearningSessionEvidenceContract",
        authorized_by="LearningSessionEvidencePath",
        context=context,
        constraints=constraints,
        domain="learning-session",
        notes=(
            "Learning Mode lifecycle evidence. The recorder identity in authorized_by "
            "names the evidence path and does not grant learning, memory, execution, or actuation authority."
        ),
    )


def _classification(event_type: str) -> tuple[str, str]:
    state = _EVENT_STATE[event_type]
    if event_type == SESSION_PROPOSED:
        return "record_proposal", state
    if event_type == ELIGIBILITY_CHECKED:
        return "record_eligibility", state
    if event_type == SESSION_OPENED:
        return "record_open", state
    if event_type == SESSION_STUDYING:
        return "record_study_progress", state
    if event_type == REVIEW_PENDING:
        return "record_review_pending", state
    if event_type == SESSION_PAUSED:
        return "record_pause", state
    if event_type == SESSION_DEGRADED:
        return "record_degraded", state
    if event_type == INSUFFICIENT_EVIDENCE:
        return "record_insufficient_evidence", state
    if event_type == SESSION_COMPLETED:
        return "record_completion", state
    if event_type == SESSION_ABORTED:
        return "record_abort", state
    raise LearningSessionReceiptError("unsupported learning session classification")


def _validate_payload(event_type: str, payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != "1.0":
        raise LearningSessionReceiptError("learning session payload schema mismatch")
    for key in ("session_id", "body_id", "node_id", "subject_ref"):
        _required_payload_text(payload, key)
    state = payload.get("state")
    if state != _EVENT_STATE[event_type]:
        raise LearningSessionReceiptError("learning session payload state mismatch")

    evidence = _text_sequence(payload, "evidence_refs", required=True)
    _text_sequence(payload, "eligibility_refs")
    _text_sequence(payload, "workspace_refs")
    _text_sequence(payload, "distributed_work_refs")
    _text_sequence(payload, "candidate_refs")
    simulated = _text_sequence(payload, "simulated_evidence_refs")
    _text_sequence(payload, "degraded_reasons")
    if not set(simulated).issubset(set(evidence)):
        raise LearningSessionReceiptError(
            "simulated evidence refs must also be session evidence refs"
        )

    steps = payload.get("steps_used")
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise LearningSessionReceiptError("steps_used must be a non-negative integer")
    reason_code = _required_payload_text(payload, "reason_code")
    if len(reason_code) > 96 or any(character.isspace() for character in reason_code):
        raise LearningSessionReceiptError("reason_code must be a compact non-whitespace code")

    for key, expected in _REQUIRED_FLAGS.items():
        if payload.get(key) != expected:
            raise LearningSessionReceiptError(
                "learning session payload %s must be %r" % (key, expected)
            )
    forbidden = _find_forbidden(payload)
    if forbidden:
        raise LearningSessionReceiptError(
            "learning session receipt contains forbidden fields: %s" % sorted(forbidden)
        )


def _source(envelope: Mapping[str, Any]) -> str:
    for key in ("source", "source_id"):
        value = envelope.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise LearningSessionReceiptError("learning session receipt source must be a non-empty string")


def _required_text(document: Mapping[str, Any], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LearningSessionReceiptError("%s must be a non-empty string" % key)
    return value.strip()


def _required_payload_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LearningSessionReceiptError("%s must be a non-empty string" % key)
    return value.strip()


def _text_sequence(payload: Mapping[str, Any], key: str, required: bool = False) -> tuple[str, ...]:
    value = payload.get(key, [])
    if not isinstance(value, (list, tuple)):
        raise LearningSessionReceiptError("%s must be a list" % key)
    normalized = tuple(_required_text({key: item}, key) for item in value)
    if required and not normalized:
        raise LearningSessionReceiptError("%s must not be empty" % key)
    if len(set(normalized)) != len(normalized):
        raise LearningSessionReceiptError("%s must not contain duplicates" % key)
    return normalized


def _find_forbidden(value: Any, path: str = "payload") -> Set[str]:
    found: Set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text in _FORBIDDEN_KEYS:
                found.add("%s.%s" % (path, key_text))
            found.update(_find_forbidden(child, "%s.%s" % (path, key_text)))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found.update(_find_forbidden(child, "%s[%s]" % (path, index)))
    return found
