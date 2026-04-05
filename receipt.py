# receipt.py
# Velvet Receipts — Core Receipt Model
# GPLv3 — aligned with Velvet core infrastructure

import time
import hashlib
import json
import uuid


class Receipt:
    """
    A single accountability record for a Velvet system decision.

    Captures what happened, what result followed, under what policy
    authority it was sanctioned, and how it links to the prior receipt.

    Hash is derived from canonical payload only.
    previous_hash is injected by the logger before finalization.
    """

    def __init__(
        self,
        event,
        decision,
        result,
        policy,
        authorized_by,
        context=None,
        constraints=None,
        notes=None,
        confidence=None,
        domain=None,
        receipt_id=None,
        timestamp=None,
    ):
        self.receipt_id = receipt_id or str(uuid.uuid4())
        self.timestamp = timestamp or time.time()
        self.event = event
        self.decision = decision
        self.result = result
        self.policy = policy
        self.authorized_by = authorized_by
        self.context = context or {}
        self.constraints = constraints or {}
        self.notes = notes
        self.confidence = confidence
        self.domain = domain

        # Injected by ReceiptLogger before finalization
        self.previous_hash = None
        self.hash = None

    def canonical_payload(self):
        """
        Deterministic dict used as the basis for hash computation.
        hash itself is excluded. All optional fields included only if set.
        """
        payload = {
            "receipt_id": self.receipt_id,
            "timestamp": self.timestamp,
            "event": self.event,
            "decision": self.decision,
            "result": self.result,
            "policy": self.policy,
            "authorized_by": self.authorized_by,
            "context": self.context,
            "constraints": self.constraints,
            "previous_hash": self.previous_hash,
        }
        if self.notes is not None:
            payload["notes"] = self.notes
        if self.confidence is not None:
            payload["confidence"] = self.confidence
        if self.domain is not None:
            payload["domain"] = self.domain
        return payload

    def compute_hash(self):
        """
        SHA-256 of the canonical payload serialized as compact sorted JSON.
        Requires previous_hash to be set first.
        """
        if self.previous_hash is None:
            raise ValueError(
                "previous_hash must be set before computing hash. "
                "Use ReceiptLogger.log() to finalize receipts."
            )
        payload_string = json.dumps(
            self.canonical_payload(), sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(payload_string.encode()).hexdigest()

    def to_dict(self):
        """
        Full receipt as a dict, including hash.
        Only valid after finalization via ReceiptLogger.
        """
        d = self.canonical_payload()
        d["hash"] = self.hash
        return d
