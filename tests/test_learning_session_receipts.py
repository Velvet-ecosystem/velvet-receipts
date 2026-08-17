# SPDX-License-Identifier: GPL-3.0-only

import unittest

from learning_session_receipts import (
    ELIGIBILITY_CHECKED,
    INSUFFICIENT_EVIDENCE,
    REVIEW_PENDING,
    SESSION_ABORTED,
    SESSION_COMPLETED,
    SESSION_DEGRADED,
    SESSION_OPENED,
    SESSION_PAUSED,
    SESSION_PROPOSED,
    SESSION_STUDYING,
    LEARNING_SESSION_RECEIPT_SCHEMA,
    LearningSessionReceiptError,
    learning_session_receipt_from_envelope,
)
from runtime_receipts import runtime_receipt_from_envelope


FLAGS = {
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

EVENT_STATE = {
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


class LearningSessionReceiptTests(unittest.TestCase):
    def envelope(self, event_type, **overrides):
        payload = {
            "schema_version": "1.0",
            "session_id": "learning-session-001",
            "body_id": "founder",
            "node_id": "velvet-founder",
            "subject_ref": "study-subject-001",
            "state": EVENT_STATE[event_type],
            "evidence_refs": ["evidence-001"],
            "eligibility_refs": [],
            "workspace_refs": [],
            "distributed_work_refs": [],
            "candidate_refs": [],
            "simulated_evidence_refs": [],
            "degraded_reasons": [],
            "steps_used": 1,
            "reason_code": "lifecycle_transition",
            **FLAGS,
        }
        payload.update(overrides)
        return {
            "event_type": event_type,
            "source_id": "velvet-ai-core",
            "sequence": 1,
            "occurred_at_monotonic_ns": 100,
            "payload": payload,
        }

    def test_records_proposal_as_evidence_not_authority(self):
        receipt = learning_session_receipt_from_envelope(
            self.envelope(SESSION_PROPOSED)
        )
        self.assertEqual(receipt.decision, "record_proposal")
        self.assertEqual(receipt.result, "PROPOSED")
        self.assertEqual(receipt.domain, "learning-session")
        self.assertEqual(receipt.context["schema"], LEARNING_SESSION_RECEIPT_SCHEMA)
        self.assertTrue(receipt.constraints["receipt_is_evidence_not_authority"])
        self.assertTrue(receipt.constraints["learning_session_cannot_promote_memory"])
        self.assertTrue(receipt.constraints["learning_session_cannot_apply_changes"])

    def test_runtime_gateway_dispatches_learning_session_family(self):
        receipt = runtime_receipt_from_envelope(self.envelope(SESSION_STUDYING))
        self.assertEqual(receipt.policy, "LearningSessionEvidenceContract")
        self.assertEqual(receipt.event, SESSION_STUDYING)

    def test_simulated_vehicle_evidence_remains_explicit(self):
        receipt = learning_session_receipt_from_envelope(
            self.envelope(
                SESSION_STUDYING,
                evidence_refs=["ghost-can-001", "manual-001"],
                simulated_evidence_refs=["ghost-can-001"],
                workspace_refs=["cog-001"],
            )
        )
        self.assertEqual(receipt.context["simulated_evidence_refs"], ["ghost-can-001"])
        self.assertTrue(receipt.constraints["simulation_provenance_preserved"])

    def test_rejects_lost_simulation_provenance(self):
        with self.assertRaisesRegex(LearningSessionReceiptError, "simulated evidence refs"):
            learning_session_receipt_from_envelope(
                self.envelope(
                    SESSION_STUDYING,
                    simulated_evidence_refs=["ghost-can-missing"],
                )
            )

    def test_rejects_raw_study_material_and_authority_fields(self):
        for key, value in (
            ("objective", "study this manual"),
            ("prompt", "summarize"),
            ("content", "raw library material"),
            ("url", "https://example.invalid"),
            ("capability_token", "forbidden"),
            ("executor", "forbidden"),
        ):
            with self.assertRaisesRegex(LearningSessionReceiptError, "forbidden"):
                learning_session_receipt_from_envelope(
                    self.envelope(SESSION_PROPOSED, **{key: value})
                )

    def test_rejects_state_event_mismatch(self):
        with self.assertRaisesRegex(LearningSessionReceiptError, "state mismatch"):
            learning_session_receipt_from_envelope(
                self.envelope(SESSION_COMPLETED, state="STUDYING")
            )

    def test_all_lifecycle_events_normalize(self):
        for event_type, state in EVENT_STATE.items():
            with self.subTest(event_type=event_type):
                receipt = learning_session_receipt_from_envelope(
                    self.envelope(event_type)
                )
                self.assertEqual(receipt.result, state)


if __name__ == "__main__":
    unittest.main()
