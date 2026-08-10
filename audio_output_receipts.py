# SPDX-License-Identifier: GPL-3.0-only
"""Canonical evidence receipts for Velvet Audio Studio output activity."""

from __future__ import annotations

from typing import Any, Mapping, Set

from receipt import Receipt

AUDIO_OUTPUT_BOOKED = "audio.output.booked"
AUDIO_OUTPUT_STARTED = "audio.output.started"
AUDIO_OUTPUT_COMPLETED = "audio.output.completed"
AUDIO_OUTPUT_PREEMPTED = "audio.output.preempted"
AUDIO_OUTPUT_FAILED = "audio.output.failed"
AUDIO_OUTPUT_RECOVERED = "audio.output.recovered"

AUDIO_OUTPUT_RECEIPT_EVENTS = {
    AUDIO_OUTPUT_BOOKED,
    AUDIO_OUTPUT_STARTED,
    AUDIO_OUTPUT_COMPLETED,
    AUDIO_OUTPUT_PREEMPTED,
    AUDIO_OUTPUT_FAILED,
    AUDIO_OUTPUT_RECOVERED,
}
AUDIO_OUTPUT_EVENT_CONTRACT = "velvet.audio-output-evidence.v1"
AUDIO_OUTPUT_RECEIPT_SCHEMA = "velvet.receipts.audio-output.v1"

_REQUIRED_FLAGS = {
    "evidence_only": True,
    "authority": "none",
    "grants_authority": False,
    "grants_execution": False,
    "grants_actuation": False,
    "audio_output_only": True,
}
_FORBIDDEN_KEYS = {
    "text",
    "transcript",
    "pcm_bytes",
    "raw_audio",
    "alsa_device",
    "model_path",
    "config_path",
    "capability",
    "capability_token",
    "command",
    "court_token",
    "execution_token",
    "executor",
    "hardware_handle",
    "hardware_target",
    "authorization",
    "authorized",
    "authorized_by",
    "actuation",
    "actuate",
}


class AudioOutputReceiptError(ValueError):
    """Raised when Audio Studio output evidence violates its receipt boundary."""


def audio_output_receipt_from_envelope(envelope: Mapping[str, Any]) -> Receipt:
    """Normalize one validated Audio Studio output event into a canonical receipt.

    The receipt records evidence only. It never grants speech, execution,
    actuation, channel ownership, or hardware authority.
    """
    if not isinstance(envelope, Mapping):
        raise TypeError("audio output receipt envelope must be a mapping")

    event_type = _required_text(envelope, "event_type")
    if event_type not in AUDIO_OUTPUT_RECEIPT_EVENTS:
        raise AudioOutputReceiptError(
            "unsupported audio output receipt event_type: %s" % event_type
        )

    source = _source(envelope)
    payload_value = envelope.get("payload")
    if not isinstance(payload_value, Mapping):
        raise AudioOutputReceiptError("audio output receipt payload must be a mapping")
    payload = dict(payload_value)
    _validate_payload(event_type, payload)

    request_id = _required_payload_text(payload, "request_id")
    decision, result = _classification(event_type, payload)
    context = {
        "schema": AUDIO_OUTPUT_RECEIPT_SCHEMA,
        "source": source,
        "subject_id": request_id,
        "event_contract": AUDIO_OUTPUT_EVENT_CONTRACT,
        **payload,
    }
    constraints = {
        "local_only": True,
        "verified_event_contract_required": True,
        "spoken_text_not_copied": True,
        "raw_audio_not_copied": True,
        "audio_route_is_evidence_not_authority": True,
        "receipt_is_evidence_not_authority": True,
        "no_command_authority": True,
        "no_actuation_authority": True,
    }

    return Receipt(
        event=event_type,
        decision=decision,
        result=result,
        policy="AudioOutputEvidenceContract",
        authorized_by="AudioStudioEvidencePath",
        context=context,
        constraints=constraints,
        domain="audio-output",
        notes=(
            "Audio output evidence. The recorder identity in authorized_by names "
            "the evidence path and does not grant speech, execution, or actuation authority."
        ),
    )


def _classification(event_type: str, payload: Mapping[str, Any]) -> tuple[str, str]:
    if event_type == AUDIO_OUTPUT_BOOKED:
        return "record_booking", "booked"
    if event_type == AUDIO_OUTPUT_STARTED:
        return "record_start", "started"
    if event_type == AUDIO_OUTPUT_COMPLETED:
        return "record_completion", "completed"
    if event_type == AUDIO_OUTPUT_PREEMPTED:
        return "record_preemption", "preempted"
    if event_type == AUDIO_OUTPUT_FAILED:
        return "record_failure", _required_payload_text(payload, "failure_stage")
    if event_type == AUDIO_OUTPUT_RECOVERED:
        return "record_recovery", "recovered"
    raise AudioOutputReceiptError("unsupported audio output receipt classification")


def _validate_payload(event_type: str, payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != "1.0":
        raise AudioOutputReceiptError("audio output payload schema mismatch")
    for key in ("output_event_id", "request_id", "node_id"):
        _required_payload_text(payload, key)
    priority = payload.get("priority")
    if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 100:
        raise AudioOutputReceiptError("audio output priority must be an integer from 0 to 100")
    channels = payload.get("output_channels")
    if not isinstance(channels, (list, tuple)):
        raise AudioOutputReceiptError("output_channels must be a list")
    if len(set(channels)) != len(channels):
        raise AudioOutputReceiptError("output_channels must be unique")
    if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in channels):
        raise AudioOutputReceiptError("output_channels must contain non-negative integers")

    for key, expected in _REQUIRED_FLAGS.items():
        if payload.get(key) != expected:
            raise AudioOutputReceiptError(
                "audio output payload %s must be %r" % (key, expected)
            )
    forbidden = _find_forbidden(payload)
    if forbidden:
        raise AudioOutputReceiptError(
            "audio output receipt contains forbidden fields: %s" % sorted(forbidden)
        )

    if event_type == AUDIO_OUTPUT_BOOKED and not channels:
        raise AudioOutputReceiptError("booked audio output requires output channels")
    if event_type == AUDIO_OUTPUT_STARTED:
        if not channels:
            raise AudioOutputReceiptError("started audio output requires output channels")
        _positive_int(payload, "source_sample_rate_hz")
        _positive_int(payload, "playback_sample_rate_hz")
        _nonnegative_int(payload, "source_frames")
    if event_type in {AUDIO_OUTPUT_COMPLETED, AUDIO_OUTPUT_PREEMPTED}:
        if not channels:
            raise AudioOutputReceiptError("finished audio output requires output channels")
        _positive_int(payload, "playback_sample_rate_hz")
        _nonnegative_int(payload, "frames_written")
        _nonnegative_number(payload, "playback_duration_ms")
    if event_type == AUDIO_OUTPUT_PREEMPTED:
        _required_payload_text(payload, "preempted_by_request_id")
    if event_type == AUDIO_OUTPUT_FAILED:
        stage = _required_payload_text(payload, "failure_stage")
        if stage not in {"synthesis", "booking", "playback"}:
            raise AudioOutputReceiptError("invalid audio output failure stage")
        _required_payload_text(payload, "error_class")
        _required_payload_text(payload, "reason")
        if payload.get("recovery_required") is not True:
            raise AudioOutputReceiptError("audio output failure must require recovery")
    if event_type == AUDIO_OUTPUT_RECOVERED:
        _required_payload_text(payload, "recovered_from_event_id")
        _required_payload_text(payload, "recovered_from_stage")


def _source(envelope: Mapping[str, Any]) -> str:
    for key in ("source", "source_id"):
        value = envelope.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise AudioOutputReceiptError("audio output receipt source must be a non-empty string")


def _required_text(document: Mapping[str, Any], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AudioOutputReceiptError("%s must be a non-empty string" % key)
    return value.strip()


def _required_payload_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AudioOutputReceiptError("%s must be a non-empty string" % key)
    return value.strip()


def _positive_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise AudioOutputReceiptError("%s must be a positive integer" % key)
    return value


def _nonnegative_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AudioOutputReceiptError("%s must be a non-negative integer" % key)
    return value


def _nonnegative_number(payload: Mapping[str, Any], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise AudioOutputReceiptError("%s must be a non-negative number" % key)
    return float(value)


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
