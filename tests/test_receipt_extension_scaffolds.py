import pytest

from receipt_extension_scaffolds import (
    CREDENTIAL_LIFECYCLE_SCHEMA,
    EVENT_EVIDENCE_SCHEMA,
    INFERENCE_COST_SCHEMA,
    NODE_COMMISSIONING_SCHEMA,
    TELEMETRY_RECONCILIATION_SCHEMA,
    credential_lifecycle_receipt,
    event_evidence_receipt,
    inference_cost_receipt,
    node_commissioning_receipt,
    telemetry_reconciliation_receipt,
)


def test_inference_cost_receipt_records_model_cost_without_authority():
    receipt = inference_cost_receipt(
        {
            "payload": {
                "capability_requested": "vision-local",
                "model_provider": "local",
                "model_name_or_local_id": "tiny-detector-v1",
                "execution_location": "queen-up2",
                "processor_class": "cpu",
                "runtime_ms": 18,
                "fallback_invoked": False,
                "authority_level": "classify",
                "memory_peak_mb": 256,
            }
        }
    )

    assert receipt.context["schema"] == INFERENCE_COST_SCHEMA
    assert receipt.constraints["model_provider_gets_no_physical_authority"] is True
    assert receipt.decision == "record_inference_cost"


def test_event_evidence_receipt_records_bounded_capture():
    receipt = event_evidence_receipt(
        {
            "payload": {
                "trigger_condition": "camera frame stall",
                "trigger_confidence": 0.9,
                "pre_buffer_ms": 5000,
                "post_buffer_ms": 5000,
                "raw_sources_retained": ["front-camera"],
                "derived_state_retained": ["vision-health"],
                "privacy_class": "internal",
                "capture_result": "complete",
            }
        }
    )

    assert receipt.context["schema"] == EVENT_EVIDENCE_SCHEMA
    assert receipt.constraints["bounded_capture_required"] is True
    assert receipt.confidence == 0.9


def test_credential_lifecycle_receipt_records_destination_and_blast_radius():
    receipt = credential_lifecycle_receipt(
        {
            "payload": {
                "credential_class": "app_token",
                "blocked_before_commit": True,
                "replacement_issued": False,
                "blast_radius_class": "single_token",
                "permitted_caller": "velour-sync",
                "permitted_destination": "github.com",
                "affected_modules_checked": ["velour-sync"],
            }
        }
    )

    assert receipt.context["schema"] == CREDENTIAL_LIFECYCLE_SCHEMA
    assert receipt.context["permitted_destination"] == "github.com"
    assert receipt.constraints["receipt_is_evidence_not_secret_storage"] is True


def test_node_commissioning_receipt_marks_booting_as_not_trust():
    receipt = node_commissioning_receipt(
        {
            "payload": {
                "node_id": "handmaiden-01",
                "hardware_model": "luckfox-lyra-ultra",
                "firmware_version": "0.1.0",
                "firmware_hash": "abc123",
                "keys_installed": True,
                "commissioned_by": "fixture-alpha",
                "authority_assigned": ["observe"],
            }
        }
    )

    assert receipt.context["schema"] == NODE_COMMISSIONING_SCHEMA
    assert receipt.result == "commissioned"
    assert receipt.constraints["booting_is_not_trust"] is True


def test_telemetry_reconciliation_receipt_records_contradictions():
    receipt = telemetry_reconciliation_receipt(
        {
            "payload": {
                "reconciliation_id": "frames-produced-processed",
                "expected_relation": "equals",
                "left_measurement": "frames_produced",
                "right_measurement": "frames_processed",
                "observed_left": 120,
                "observed_right": 80,
                "tolerance": 0,
                "contradiction_detected": True,
                "likely_fault_domain": "software",
                "confidence": 0.8,
            }
        }
    )

    assert receipt.context["schema"] == TELEMETRY_RECONCILIATION_SCHEMA
    assert receipt.result == "contradiction"
    assert receipt.constraints["contradiction_is_evidence"] is True


def test_receipt_scaffold_rejects_bad_confidence():
    with pytest.raises(ValueError, match="trigger_confidence"):
        event_evidence_receipt(
            {
                "payload": {
                    "trigger_condition": "bad",
                    "trigger_confidence": 2.0,
                    "pre_buffer_ms": 0,
                    "post_buffer_ms": 0,
                    "privacy_class": "internal",
                    "capture_result": "failed",
                }
            }
        )


def test_receipt_scaffold_rejects_non_list_authority_assignment():
    with pytest.raises(ValueError, match="authority_assigned"):
        node_commissioning_receipt(
            {
                "payload": {
                    "node_id": "node",
                    "hardware_model": "board",
                    "firmware_version": "0.1",
                    "firmware_hash": "hash",
                    "keys_installed": True,
                    "commissioned_by": "fixture",
                    "authority_assigned": "observe",
                }
            }
        )
