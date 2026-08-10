# SPDX-License-Identifier: GPL-3.0-only
"""Public package surface for Velvet Receipts."""

from receipt import Receipt
from receipt_logger import GENESIS_HASH, ReceiptLogger
from runtime_receipts import runtime_receipt_from_envelope
from audio_output_receipts import (
    AUDIO_OUTPUT_EVENT_CONTRACT,
    AUDIO_OUTPUT_RECEIPT_EVENTS,
    AUDIO_OUTPUT_RECEIPT_SCHEMA,
    AudioOutputReceiptError,
    audio_output_receipt_from_envelope,
)
from ghost_can_receipts import (
    GHOST_CAN_OBSERVATION_EVENT,
    GHOST_CAN_RECEIPT_SCHEMA,
    ghost_can_receipt_from_envelope,
)
from distributed_work_receipts import (
    DISTRIBUTED_WORK_RECEIPT_EVENTS,
    DISTRIBUTED_WORK_RECEIPT_SCHEMA,
    DistributedWorkReceiptError,
    distributed_work_receipt_from_envelope,
)

__all__ = [
    "GENESIS_HASH",
    "Receipt",
    "ReceiptLogger",
    "AUDIO_OUTPUT_EVENT_CONTRACT",
    "AUDIO_OUTPUT_RECEIPT_EVENTS",
    "AUDIO_OUTPUT_RECEIPT_SCHEMA",
    "AudioOutputReceiptError",
    "audio_output_receipt_from_envelope",
    "GHOST_CAN_OBSERVATION_EVENT",
    "GHOST_CAN_RECEIPT_SCHEMA",
    "ghost_can_receipt_from_envelope",
    "DISTRIBUTED_WORK_RECEIPT_EVENTS",
    "DISTRIBUTED_WORK_RECEIPT_SCHEMA",
    "DistributedWorkReceiptError",
    "distributed_work_receipt_from_envelope",
    "runtime_receipt_from_envelope",
]
