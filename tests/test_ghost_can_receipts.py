import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ghost_can_receipts import (
    GHOST_CAN_OBSERVATION_EVENT,
    GHOST_CAN_RECEIPT_SCHEMA,
    ghost_can_receipt_from_envelope,
)
from runtime_receipts import runtime_receipt_from_envelope


class TestGhostCanReceipts(unittest.TestCase):
    def envelope(self, **overrides):
        payload = {
            "state": "completed",
            "route_id": "can-ghost",
            "target": "vehicle-can-ghost",
            "frame_index": 1,
            "read_only": True,
            "synthetic_fixture": True,
            "physical_bus_opened": False,
            "can_transmission_attempted": False,
            "actuation_performed": False,
            "authority_granted": False,
            "decoded_signals": {
                "vehicle_speed_kmh": 0,
                "engine_rpm": 812,
                "o2_fault": True,
            },
        }
        payload.update(overrides)
        return {
            "event_type": GHOST_CAN_OBSERVATION_EVENT,
            "source": "velvet-runtime",
            "subject_id": "owner",
            "payload": payload,
        }

    def test_builds_public_safe_ghost_can_receipt(self):
        receipt = ghost_can_receipt_from_envelope(self.envelope())
        self.assertEqual(receipt.event, GHOST_CAN_OBSERVATION_EVENT)
        self.assertEqual(receipt.decision, "record_observation")
        self.assertEqual(receipt.authorized_by, "RuntimeReadOnlyPath")
        self.assertEqual(receipt.policy, "PublicGhostCanReceiptContract")
        self.assertEqual(receipt.domain, "vehicle-can-ghost")
        self.assertEqual(receipt.context["schema"], GHOST_CAN_RECEIPT_SCHEMA)
        self.assertTrue(receipt.constraints["observation_only"])
        self.assertTrue(receipt.constraints["no_can_transmission"])
        self.assertTrue(receipt.constraints["no_actuation"])
        self.assertTrue(receipt.constraints["receipt_is_evidence_not_authority"])

    def test_runtime_receipt_router_accepts_ghost_can_event(self):
        receipt = runtime_receipt_from_envelope(self.envelope())
        self.assertEqual(receipt.event, GHOST_CAN_OBSERVATION_EVENT)
        self.assertEqual(receipt.domain, "vehicle-can-ghost")

    def test_rejects_missing_read_only_flag(self):
        with self.assertRaises(ValueError):
            ghost_can_receipt_from_envelope(self.envelope(read_only=False))

    def test_rejects_physical_bus_opened(self):
        with self.assertRaises(ValueError):
            ghost_can_receipt_from_envelope(self.envelope(physical_bus_opened=True))

    def test_rejects_can_transmission_attempt(self):
        with self.assertRaises(ValueError):
            ghost_can_receipt_from_envelope(self.envelope(can_transmission_attempted=True))

    def test_rejects_actuation(self):
        with self.assertRaises(ValueError):
            ghost_can_receipt_from_envelope(self.envelope(actuation_performed=True))

    def test_rejects_authority_grant(self):
        with self.assertRaises(ValueError):
            ghost_can_receipt_from_envelope(self.envelope(authority_granted=True))


if __name__ == "__main__":
    unittest.main()
