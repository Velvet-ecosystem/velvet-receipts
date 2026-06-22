import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from runtime_receipts import runtime_receipt_from_envelope


class TestRuntimeReceipts(unittest.TestCase):
    def envelope(self, event_type, state="completed"):
        return {
            "event_type": event_type,
            "source": "velvet-runtime",
            "subject_id": "owner",
            "payload": {
                "state": state,
                "intent_id": "intent-1",
                "token_id": "token-1",
                "capability": "runtime.observe",
                "target": "runtime",
            },
        }

    def test_court_authorization_classification(self):
        receipt = runtime_receipt_from_envelope(self.envelope("COURT_AUTHORIZED", "authorized"))
        self.assertEqual(receipt.decision, "allow")
        self.assertEqual(receipt.authorized_by, "Court")
        self.assertEqual(receipt.domain, "authorization")

    def test_execution_completion_requires_executor_and_safety_constraints(self):
        receipt = runtime_receipt_from_envelope(self.envelope("EXECUTION_COMPLETED"))
        self.assertEqual(receipt.decision, "complete")
        self.assertEqual(receipt.authorized_by, "ApprovedExecutor")
        self.assertTrue(receipt.constraints["token_required"])
        self.assertTrue(receipt.constraints["safety_gate_required"])
        self.assertTrue(receipt.constraints["approved_executor_required"])
        self.assertTrue(receipt.constraints["receipt_is_evidence_not_authority"])

    def test_safety_failure_classification(self):
        receipt = runtime_receipt_from_envelope(self.envelope("SAFETY_FAILED", "sensor_unavailable"))
        self.assertEqual(receipt.decision, "deny_conditions")
        self.assertEqual(receipt.authorized_by, "SafetyGate")
        self.assertEqual(receipt.domain, "safety")

    def test_unknown_runtime_event_is_rejected(self):
        with self.assertRaises(ValueError):
            runtime_receipt_from_envelope(self.envelope("SHELL_EXECUTED"))

    def test_missing_state_is_rejected_when_empty(self):
        envelope = self.envelope("EXECUTION_FAILED")
        envelope["payload"]["state"] = ""
        with self.assertRaises(ValueError):
            runtime_receipt_from_envelope(envelope)


if __name__ == "__main__":
    unittest.main()
