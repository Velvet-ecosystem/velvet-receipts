import unittest

from runtime_receipts import runtime_receipt_from_envelope


class IntegrationReceiptTests(unittest.TestCase):
    def envelope(self, event_type, state):
        return {
            "event_type": event_type,
            "source": "integration-test",
            "subject_id": "driver-seat",
            "payload": {
                "state": state,
                "authority_granted": False,
            },
        }

    def test_capability_refusal_receipt(self):
        receipt = runtime_receipt_from_envelope(
            self.envelope("CAPABILITY_REFUSED", "refused")
        )
        self.assertEqual(receipt.decision, "refuse")
        self.assertEqual(
            receipt.authorized_by,
            "RuntimeCapabilityRegistry",
        )
        self.assertEqual(receipt.domain, "capability")
        self.assertTrue(
            receipt.constraints["receipt_is_evidence_not_authority"]
        )

    def test_resource_posture_receipt(self):
        receipt = runtime_receipt_from_envelope(
            self.envelope("RESOURCE_POSTURE_OBSERVED", "degraded")
        )
        self.assertEqual(receipt.policy, "RuntimeResourceGuard")
        self.assertEqual(receipt.domain, "resource")

    def test_presence_fusion_receipt(self):
        receipt = runtime_receipt_from_envelope(
            self.envelope("PRESENCE_FUSION_ACCEPTED", "accepted")
        )
        self.assertEqual(receipt.decision, "accept_evidence")
        self.assertEqual(receipt.authorized_by, "PresenceFusion")
        self.assertFalse(receipt.context["authority_granted"])


if __name__ == "__main__":
    unittest.main()
