# SPDX-License-Identifier: GPL-3.0-only

import unittest

from distributed_work_receipts import (
    DISTRIBUTED_WORK_RECEIPT_SCHEMA,
    NODE_ADVERTISEMENT_PUBLISHED,
    WORK_ACCEPTED,
    WORK_COMPLETED,
    WORK_DEGRADED,
    WORK_HANDOFF_REQUESTED,
    WORK_OFFERED,
    WORK_RECOVERY_REASSIGNED,
    WORK_REFUSED,
    DistributedWorkReceiptError,
    distributed_work_receipt_from_envelope,
)
from runtime_receipts import runtime_receipt_from_envelope


TRANSPORT_FLAGS = {
    "transport_only": True,
    "canonical": False,
    "authority": "none",
    "grants_authority": False,
    "grants_execution": False,
    "grants_actuation": False,
}


class DistributedWorkReceiptTests(unittest.TestCase):
    def work_envelope(self, event_type, **payload_overrides):
        payload = {
            "work_id": "work-001",
            "work_class": "logging",
            "required_capabilities": ["logging"],
            "fallback_options": [],
            "important_result": False,
            "escalate_to_queen": True,
            "court_authorization_required": False,
            **TRANSPORT_FLAGS,
        }
        payload.update(payload_overrides)
        return {
            "event_type": event_type,
            "source": "velvet-runtime",
            "subject_id": "work-001",
            "payload": payload,
        }

    def node_envelope(self, **payload_overrides):
        payload = {
            "node_id": "velour-01",
            "body_id": "velvet-founder",
            "organ": "velour",
            "tier": "specialist_linux",
            "capabilities": ["logging", "receipt-indexing"],
            "current_load": 0.25,
            "health": 0.96,
            "availability": "available",
            "last_heartbeat": 100.0,
            "max_concurrent_tasks": 3,
            "current_tasks": 1,
            "accepted_work_classes": ["logging"],
            "refused_work_classes": [],
            "overflow_capabilities": ["sensor-filtering"],
            "temporary_absorption_capabilities": ["security-log"],
            "fallback_options": ["queen"],
            "body_verified": True,
            "continuity_verified": True,
            **TRANSPORT_FLAGS,
        }
        payload.update(payload_overrides)
        return {
            "event_type": NODE_ADVERTISEMENT_PUBLISHED,
            "source": "velvet-runtime",
            "subject_id": "velour-01",
            "payload": payload,
        }

    def test_records_node_advertisement_as_evidence(self):
        receipt = distributed_work_receipt_from_envelope(self.node_envelope())
        self.assertEqual(receipt.event, NODE_ADVERTISEMENT_PUBLISHED)
        self.assertEqual(receipt.decision, "record_advertisement")
        self.assertEqual(receipt.result, "available")
        self.assertEqual(receipt.domain, "distributed-node")
        self.assertEqual(receipt.context["schema"], DISTRIBUTED_WORK_RECEIPT_SCHEMA)
        self.assertTrue(receipt.constraints["receipt_is_evidence_not_authority"])

    def test_node_subject_must_match_advertised_node(self):
        envelope = self.node_envelope()
        envelope["subject_id"] = "queen-01"
        with self.assertRaisesRegex(DistributedWorkReceiptError, "must match node_id"):
            distributed_work_receipt_from_envelope(envelope)

    def test_records_work_offer(self):
        receipt = distributed_work_receipt_from_envelope(
            self.work_envelope(WORK_OFFERED)
        )
        self.assertEqual(receipt.decision, "record_offer")
        self.assertEqual(receipt.result, "offered")
        self.assertFalse(receipt.context["grants_execution"])

    def test_records_runtime_lease_without_authorizing_execution(self):
        receipt = distributed_work_receipt_from_envelope(
            self.work_envelope(
                WORK_ACCEPTED,
                node_id="velour-01",
                organ="velour",
                placement_mode="primary",
                lease_id="work-001:velour-01",
                lease_expires_at=160.0,
                court_authorization_required=True,
            )
        )
        self.assertEqual(receipt.decision, "record_lease")
        self.assertEqual(receipt.result, "primary")
        self.assertTrue(receipt.context["court_authorization_required"])
        self.assertTrue(receipt.constraints["court_remains_independent"])
        self.assertFalse(receipt.context["grants_execution"])

    def test_records_refusal_as_bounded_behavior(self):
        receipt = distributed_work_receipt_from_envelope(
            self.work_envelope(
                WORK_REFUSED,
                node_id="audio-01",
                organ="audio",
                reason="task-limit-reached",
            )
        )
        self.assertEqual(receipt.decision, "record_refusal")
        self.assertEqual(receipt.result, "refused")

    def test_handoff_transfers_no_authority(self):
        receipt = distributed_work_receipt_from_envelope(
            self.work_envelope(
                WORK_HANDOFF_REQUESTED,
                from_node_id="audio-01",
                reason="overloaded",
                fallback_options=["audio-02", "queen"],
            )
        )
        self.assertEqual(receipt.decision, "record_handoff")
        self.assertTrue(receipt.constraints["handoff_transfers_no_authority"])
        self.assertTrue(receipt.constraints["court_remains_independent"])

    def test_records_important_completion_for_queen_awareness(self):
        receipt = distributed_work_receipt_from_envelope(
            self.work_envelope(
                WORK_COMPLETED,
                node_id="security-01",
                organ="security",
                result_status="completed",
                important_result=True,
            )
        )
        self.assertEqual(receipt.decision, "record_result")
        self.assertEqual(receipt.result, "completed")
        self.assertTrue(receipt.context["important_result"])
        self.assertTrue(receipt.context["escalate_to_queen"])

    def test_records_explicit_degradation(self):
        receipt = distributed_work_receipt_from_envelope(
            self.work_envelope(
                WORK_DEGRADED,
                degradation_mode="observe_only",
                reason="full-audio-pipeline-unavailable",
                fallback_options=["push-to-talk"],
            )
        )
        self.assertEqual(receipt.decision, "record_degradation")
        self.assertEqual(receipt.result, "observe_only")

    def test_records_recovery_reassignment_without_lineage_claim(self):
        receipt = distributed_work_receipt_from_envelope(
            self.work_envelope(
                WORK_RECOVERY_REASSIGNED,
                from_node_id="velour-01",
                to_node_id="queen-01",
                placement_mode="queen_fallback",
                lease_id="work-001:queen-01",
                lease_expires_at=240.0,
                reason="stale-heartbeat",
            )
        )
        self.assertEqual(receipt.decision, "record_recovery")
        self.assertEqual(receipt.result, "reassigned")
        self.assertTrue(
            receipt.constraints["ordinary_load_balancing_is_not_lineage"]
        )

    def test_rejects_nested_authority_fields(self):
        envelope = self.work_envelope(WORK_OFFERED)
        envelope["payload"]["fallback_options"] = [
            {"capability_token": "forbidden"}
        ]
        with self.assertRaisesRegex(
            DistributedWorkReceiptError, "forbidden authority fields"
        ):
            distributed_work_receipt_from_envelope(envelope)

    def test_rejects_event_that_grants_execution(self):
        envelope = self.work_envelope(WORK_OFFERED)
        envelope["payload"]["grants_execution"] = True
        with self.assertRaisesRegex(DistributedWorkReceiptError, "grants_execution"):
            distributed_work_receipt_from_envelope(envelope)

    def test_work_subject_must_match_work_id(self):
        envelope = self.work_envelope(WORK_OFFERED)
        envelope["subject_id"] = "work-999"
        with self.assertRaisesRegex(DistributedWorkReceiptError, "must match work_id"):
            distributed_work_receipt_from_envelope(envelope)

    def test_runtime_receipt_gateway_dispatches_distributed_work(self):
        receipt = runtime_receipt_from_envelope(
            self.work_envelope(
                WORK_ACCEPTED,
                node_id="velour-01",
                organ="velour",
                placement_mode="overflow",
                lease_id="work-001:velour-01",
                lease_expires_at=160.0,
            )
        )
        self.assertEqual(receipt.event, WORK_ACCEPTED)
        self.assertEqual(receipt.policy, "DistributedWorkEvidenceContract")

    def test_same_envelope_produces_same_semantic_payload(self):
        envelope = self.work_envelope(
            WORK_ACCEPTED,
            node_id="velour-01",
            organ="velour",
            placement_mode="primary",
            lease_id="work-001:velour-01",
            lease_expires_at=160.0,
        )
        first = distributed_work_receipt_from_envelope(envelope)
        second = distributed_work_receipt_from_envelope(envelope)
        self.assertEqual(first.event, second.event)
        self.assertEqual(first.decision, second.decision)
        self.assertEqual(first.result, second.result)
        self.assertEqual(first.context, second.context)
        self.assertEqual(first.constraints, second.constraints)


if __name__ == "__main__":
    unittest.main()
