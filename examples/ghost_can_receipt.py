# SPDX-License-Identifier: GPL-3.0-only
"""Build and print a public-safe ghost CAN observation receipt."""

import json

from ghost_can_receipts import GHOST_CAN_OBSERVATION_EVENT, ghost_can_receipt_from_envelope
from receipt_logger import ReceiptLogger


def main() -> int:
    envelope = {
        "event_type": GHOST_CAN_OBSERVATION_EVENT,
        "source": "velvet-runtime",
        "subject_id": "owner",
        "payload": {
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
                "driver_door": "closed",
                "o2_fault": True,
            },
        },
    }

    receipt = ghost_can_receipt_from_envelope(envelope)
    logger = ReceiptLogger(filepath="ghost_can_receipts.log")
    logger.log(receipt)
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
