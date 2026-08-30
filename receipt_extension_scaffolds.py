# SPDX-License-Identifier: GPL-3.0-only
"""Receipt extension scaffolds for newer Velvet contracts.

These helpers create evidence receipts for AI cost, event evidence, credential
lifecycle, node commissioning, and telemetry reconciliation. Receipts record
truth. They do not grant authority or make unsafe work safe.
"""

from __future__ import annotations

from typing import Any, Mapping

from receipt import Receipt

INFERENCE_COST_EVENT = "ai.inference.cost"
EVENT_EVIDENCE_EVENT = "event.evidence.capture"
CREDENTIAL_LIFECYCLE_EVENT = "security.credential.lifecycle"
NODE_COMMISSIONING_EVENT = "node.commissioning"
TELEMETRY_RECONCILIATION_EVENT = "telemetry.reconciliation"

INFERENCE_COST_SCHEMA = "velvet.receipts.inference_cost.v1"
EVENT_EVIDENCE_SCHEMA = "velvet.receipts.event_evidence.v1"
CREDENTIAL_LIFECYCLE_SCHEMA = "velvet.receipts.credential_lifecycle.v1"
NODE_COMMISSIONING_SCHEMA = "velvet.receipts.node_commissioning.v1"
TELEMETRY_RECONCILIATION_SCHEMA = "velvet.receipts.telemetry_reconciliation.v1"


def inference_cost_receipt(envelope: Mapping[str, Any]) -> Receipt:
    payload = _payload(envelope)
    capability = _required_payload_text(payload, "capability_requested")
    provider = _required_payload_text(payload, "model_provider")
    model = _required_payload_text(payload, "model_name_or_local_id")
    execution_location = _required_payload_text(payload, "execution_location")
    processor_class = _required_payload_text(payload, "processor_class")
    runtime_ms = _required_payload_non_negative_number(payload, "runtime_ms")
    fallback_invoked = _required_payload_bool(payload, "fallback_invoked")
    authority_level = _required_payload_text(payload, "authority_level")

    context = {
        "schema": INFERENCE_COST_SCHEMA,
        "capability_requested": capability,
        "model_provider": provider,
        "model_name_or_local_id": model,
        "execution_location": execution_location,
        "processor_class": processor_class,
        "runtime_ms": runtime_ms,
        "fallback_invoked": fallback_invoked,
        "authority_level": authority_level,
        "input_units": payload.get("input_units"),
        "output_units": payload.get("output_units"),
        "cache_hit": payload.get("cache_hit"),
        "estimated_energy_j": payload.get("estimated_energy_j"),
        "estimated_heat_class": payload.get("estimated_heat_class", "unknown"),
        "memory_peak_mb": payload.get("memory_peak_mb"),
        "fallback_reason": payload.get("fallback_reason"),
        "larger_model_reason": payload.get("larger_model_reason"),
    }

    return Receipt(
        event=INFERENCE_COST_EVENT,
        decision="record_inference_cost",
        result="recorded",
        policy="InferenceCostReceiptContract",
        authorized_by="ReceiptRecorder",
        context=context,
        constraints={
            "receipt_is_evidence_not_authority": True,
            "model_provider_gets_no_physical_authority": True,
            "execution_location_does_not_change_court_authority": True,
        },
        domain="ai-cost",
        confidence=payload.get("result_confidence"),
    )


def event_evidence_receipt(envelope: Mapping[str, Any]) -> Receipt:
    payload = _payload(envelope)
    trigger_condition = _required_payload_text(payload, "trigger_condition")
    trigger_confidence = _required_payload_confidence(payload, "trigger_confidence")
    pre_buffer_ms = _required_payload_non_negative_int(payload, "pre_buffer_ms")
    post_buffer_ms = _required_payload_non_negative_int(payload, "post_buffer_ms")
    capture_result = _required_payload_text(payload, "capture_result")
    privacy_class = _required_payload_text(payload, "privacy_class")

    context = {
        "schema": EVENT_EVIDENCE_SCHEMA,
        "trigger_condition": trigger_condition,
        "trigger_confidence": trigger_confidence,
        "pre_buffer_ms": pre_buffer_ms,
        "post_buffer_ms": post_buffer_ms,
        "raw_sources_retained": _payload_list(payload, "raw_sources_retained"),
        "derived_state_retained": _payload_list(payload, "derived_state_retained"),
        "reason_captured": payload.get("reason_captured"),
        "storage_budget_bytes": payload.get("storage_budget_bytes"),
        "privacy_class": privacy_class,
        "capture_result": capture_result,
    }

    return Receipt(
        event=EVENT_EVIDENCE_EVENT,
        decision="record_evidence_capture",
        result=capture_result,
        policy="EventEvidenceReceiptContract",
        authorized_by="ReceiptRecorder",
        context=context,
        constraints={
            "bounded_capture_required": True,
            "privacy_class_recorded": True,
            "receipt_is_evidence_not_authority": True,
        },
        domain="event-evidence",
        confidence=trigger_confidence,
    )


def credential_lifecycle_receipt(envelope: Mapping[str, Any]) -> Receipt:
    payload = _payload(envelope)
    credential_class = _required_payload_text(payload, "credential_class")
    blast_radius_class = _required_payload_text(payload, "blast_radius_class")
    blocked_before_commit = _required_payload_bool(payload, "blocked_before_commit")
    replacement_issued = _required_payload_bool(payload, "replacement_issued")

    context = {
        "schema": CREDENTIAL_LIFECYCLE_SCHEMA,
        "credential_class": credential_class,
        "detected_at": payload.get("detected_at"),
        "blocked_before_commit": blocked_before_commit,
        "owner": payload.get("owner"),
        "permitted_caller": payload.get("permitted_caller"),
        "permitted_destination": payload.get("permitted_destination"),
        "expiry": payload.get("expiry"),
        "revoked_at": payload.get("revoked_at"),
        "replacement_issued": replacement_issued,
        "affected_modules_checked": _payload_list(payload, "affected_modules_checked"),
        "blast_radius_class": blast_radius_class,
    }

    return Receipt(
        event=CREDENTIAL_LIFECYCLE_EVENT,
        decision="record_credential_lifecycle",
        result="recorded",
        policy="CredentialLifecycleReceiptContract",
        authorized_by="ReceiptRecorder",
        context=context,
        constraints={
            "permitted_destination_recorded": True,
            "blast_radius_recorded": True,
            "receipt_is_evidence_not_secret_storage": True,
        },
        domain="credential-lifecycle",
    )


def node_commissioning_receipt(envelope: Mapping[str, Any]) -> Receipt:
    payload = _payload(envelope)
    node_id = _required_payload_text(payload, "node_id")
    hardware_model = _required_payload_text(payload, "hardware_model")
    firmware_version = _required_payload_text(payload, "firmware_version")
    firmware_hash = _required_payload_text(payload, "firmware_hash")
    keys_installed = _required_payload_bool(payload, "keys_installed")
    commissioned_by = _required_payload_text(payload, "commissioned_by")

    context = {
        "schema": NODE_COMMISSIONING_SCHEMA,
        "node_id": node_id,
        "hardware_model": hardware_model,
        "hardware_revision": payload.get("hardware_revision"),
        "firmware_version": firmware_version,
        "firmware_hash": firmware_hash,
        "keys_installed": keys_installed,
        "electrical_test_result": payload.get("electrical_test_result", "skipped"),
        "network_test_result": payload.get("network_test_result", "skipped"),
        "health_baseline_id": payload.get("health_baseline_id"),
        "authority_assigned": _payload_list(payload, "authority_assigned"),
        "installed_location": payload.get("installed_location"),
        "commissioned_by": commissioned_by,
        "commissioned_at": payload.get("commissioned_at"),
    }

    return Receipt(
        event=NODE_COMMISSIONING_EVENT,
        decision="record_node_commissioning",
        result="commissioned" if keys_installed else "incomplete",
        policy="NodeCommissioningReceiptContract",
        authorized_by="ProvisioningFixture",
        context=context,
        constraints={
            "booting_is_not_trust": True,
            "firmware_hash_recorded": True,
            "authority_assignment_recorded": True,
            "receipt_is_evidence_not_authority": True,
        },
        domain="node-commissioning",
    )


def telemetry_reconciliation_receipt(envelope: Mapping[str, Any]) -> Receipt:
    payload = _payload(envelope)
    contradiction_detected = _required_payload_bool(payload, "contradiction_detected")
    confidence = _required_payload_confidence(payload, "confidence")
    reconciliation_id = _required_payload_text(payload, "reconciliation_id")

    context = {
        "schema": TELEMETRY_RECONCILIATION_SCHEMA,
        "reconciliation_id": reconciliation_id,
        "expected_relation": _required_payload_text(payload, "expected_relation"),
        "left_measurement": _required_payload_text(payload, "left_measurement"),
        "right_measurement": _required_payload_text(payload, "right_measurement"),
        "observed_left": payload.get("observed_left"),
        "observed_right": payload.get("observed_right"),
        "tolerance": payload.get("tolerance"),
        "contradiction_detected": contradiction_detected,
        "likely_fault_domain": payload.get("likely_fault_domain", "unknown"),
        "confidence": confidence,
    }

    return Receipt(
        event=TELEMETRY_RECONCILIATION_EVENT,
        decision="record_telemetry_reconciliation",
        result="contradiction" if contradiction_detected else "consistent",
        policy="TelemetryReconciliationReceiptContract",
        authorized_by="ReceiptRecorder",
        context=context,
        constraints={
            "contradiction_is_evidence": True,
            "receipt_is_evidence_not_authority": True,
        },
        domain="telemetry-reconciliation",
        confidence=confidence,
    )


def _payload(envelope: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(envelope, Mapping):
        raise TypeError("receipt envelope must be a mapping")
    payload = envelope.get("payload", envelope)
    if not isinstance(payload, Mapping):
        raise ValueError("receipt payload must be a mapping")
    return payload


def _required_payload_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _required_payload_bool(payload: Mapping[str, Any], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def _required_payload_non_negative_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    if value < 0:
        raise ValueError(f"{key} cannot be negative")
    return value


def _required_payload_non_negative_number(payload: Mapping[str, Any], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be numeric")
    if float(value) < 0:
        raise ValueError(f"{key} cannot be negative")
    return float(value)


def _required_payload_confidence(payload: Mapping[str, Any], key: str) -> float:
    value = _required_payload_non_negative_number(payload, key)
    if value > 1.0:
        raise ValueError(f"{key} must be between 0 and 1")
    return value


def _payload_list(payload: Mapping[str, Any], key: str) -> list[str]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key} must contain non-empty strings")
    return [item.strip() for item in value]
