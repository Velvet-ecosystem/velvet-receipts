# SPDX-License-Identifier: GPL-3.0-only
"""Public-safe ghost CAN observation receipt construction.

This module records synthetic/read-only CAN observations for the public
Velvet ghost system. It validates that the evidence describes a jarred-car
observation path only. It does not authorize real CAN, open hardware buses,
transmit frames, or grant actuation.
"""

from __future__ import annotations

from typing import Any, Mapping

from receipt import Receipt

GHOST_CAN_OBSERVATION_EVENT = "vehicle.can.ghost_observation"
GHOST_CAN_RECEIPT_SCHEMA = "velvet.receipts.vehicle_can_ghost.v1"


def ghost_can_receipt_from_envelope(envelope: Mapping[str, Any]) -> Receipt:
    """Create a canonical receipt for a public ghost CAN observation.

    The receipt is evidence, not permission. Any missing or unsafe flag is
    rejected so public demos cannot quietly turn into hardware authority.
    """

    if not isinstance(envelope, Mapping):
        raise TypeError("ghost CAN receipt envelope must be a mapping")

    event_type = _required_text(envelope, "event_type")
    if event_type != GHOST_CAN_OBSERVATION_EVENT:
        raise ValueError(f"unsupported ghost CAN receipt event_type: {event_type}")

    source = _required_text(envelope, "source")
    subject_id = _required_text(envelope, "subject_id")
    payload = envelope.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("ghost CAN receipt payload must be a mapping")
    payload = dict(payload)

    state = _required_payload_text(payload, "state")
    _require_payload_text_value(payload, "route_id", "can-ghost")
    _require_payload_text_value(payload, "target", "vehicle-can-ghost")

    required_flags = {
        "read_only": True,
        "synthetic_fixture": True,
        "physical_bus_opened": False,
        "can_transmission_attempted": False,
        "actuation_performed": False,
        "authority_granted": False,
    }
    for key, expected in required_flags.items():
        if payload.get(key) is not expected:
            raise ValueError(f"ghost CAN payload {key} must be {expected!r}")

    decoded_signals = payload.get("decoded_signals", {})
    if decoded_signals is not None and not isinstance(decoded_signals, Mapping):
        raise ValueError("ghost CAN payload decoded_signals must be a mapping when present")

    context = {
        "schema": GHOST_CAN_RECEIPT_SCHEMA,
        "source": source,
        "subject_id": subject_id,
        **payload,
    }

    constraints = {
        "local_only": True,
        "observation_only": True,
        "synthetic_fixture_required": True,
        "no_physical_bus": True,
        "no_can_transmission": True,
        "no_actuation": True,
        "no_authority_granted": True,
        "receipt_is_evidence_not_authority": True,
    }

    return Receipt(
        event=GHOST_CAN_OBSERVATION_EVENT,
        decision="record_observation",
        result=state,
        policy="PublicGhostCanReceiptContract",
        authorized_by="RuntimeReadOnlyPath",
        context=context,
        constraints=constraints,
        domain="vehicle-can-ghost",
        notes=(
            "Synthetic/read-only CAN observation evidence. This receipt records "
            "a public ghost-system demo path and does not grant vehicle authority."
        ),
    )


def _required_text(document: Mapping[str, Any], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _required_payload_text(payload: Mapping[str, Any], key: str) -> str:
    return _required_text(payload, key)


def _require_payload_text_value(payload: Mapping[str, Any], key: str, expected: str) -> None:
    value = _required_payload_text(payload, key)
    if value != expected:
        raise ValueError(f"ghost CAN payload {key} must be {expected!r}")
