# receipt_logger.py
# Velvet Receipts — Append-Only Logger with Chain Verification
# GPLv3 — aligned with Velvet core infrastructure

import hashlib
import json
import os
import threading

_lock = threading.Lock()

GENESIS_HASH = "0" * 64


class ReceiptLogger:
    """
    Append-only receipt logger with hash-chain integrity.

    On each log() call:
      - reads the last receipt to obtain its hash
      - injects that hash as previous_hash into the new receipt
      - computes the new receipt's hash from its canonical payload
      - appends the finalized receipt as a single JSON line

    On verify_chain() call:
      - recomputes every receipt hash from stored canonical payload
      - confirms each stored hash matches
      - confirms each previous_hash matches the actual prior receipt hash

    Thread safety: log() is protected by a module-level lock.
    Write durability: each entry is flushed and fsynced on write.
    """

    def __init__(self, filepath="receipts.log"):
        self.filepath = filepath

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_entries(self):
        """Return all stored receipt dicts as a list, oldest first."""
        entries = []
        try:
            with open(self.filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except FileNotFoundError:
            pass
        return entries

    def get_last_hash(self):
        """Return the hash of the most recently logged receipt, or GENESIS_HASH."""
        entries = self._load_entries()
        if not entries:
            return GENESIS_HASH
        return entries[-1].get("hash", GENESIS_HASH)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def log(self, receipt):
        """
        Finalize and append a receipt to the chain.

        Sets previous_hash, computes hash, writes JSONL entry.
        The receipt object is mutated in place so the caller can
        inspect the finalized state after logging.

        Thread-safe: the full read-hash / compute / write sequence
        is protected by a module-level lock.
        Write-durable: each entry is flushed and fsynced before returning.
        """
        with _lock:
            receipt.previous_hash = self.get_last_hash()
            receipt.hash = receipt.compute_hash()

            with open(self.filepath, "a") as f:
                f.write(json.dumps(receipt.to_dict(), sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())

        return receipt

    def verify_chain(self):
        """
        Verify the integrity of the full receipt chain.

        For each receipt:
          1. Recomputes hash from stored canonical payload fields
          2. Confirms stored hash matches
          3. Confirms previous_hash matches the prior receipt's hash

        Returns:
            (bool, list[str]) — (chain_is_valid, list of error messages)

        An empty error list means the chain is intact.
        """
        entries = self._load_entries()
        errors = []

        if not entries:
            return True, []

        CANONICAL_FIELDS = [
            "receipt_id", "timestamp", "event", "decision", "result",
            "policy", "authorized_by", "context", "constraints",
            "previous_hash",
        ]
        OPTIONAL_FIELDS = ["notes", "confidence", "domain"]

        prev_hash = GENESIS_HASH

        for i, entry in enumerate(entries):
            label = f"Receipt {i} ({entry.get('receipt_id', '?')[:8]}...)"

            # Reconstruct canonical payload from stored entry
            payload = {k: entry[k] for k in CANONICAL_FIELDS if k in entry}
            for k in OPTIONAL_FIELDS:
                if k in entry:
                    payload[k] = entry[k]

            payload_string = json.dumps(
                payload, sort_keys=True, separators=(",", ":")
            )
            recomputed = hashlib.sha256(payload_string.encode()).hexdigest()

            stored_hash = entry.get("hash", "")
            if stored_hash != recomputed:
                errors.append(
                    f"{label}: hash mismatch — stored={stored_hash[:12]}... "
                    f"recomputed={recomputed[:12]}..."
                )

            stored_prev = entry.get("previous_hash", "")
            if stored_prev != prev_hash:
                errors.append(
                    f"{label}: previous_hash mismatch — "
                    f"stored={stored_prev[:12]}... expected={prev_hash[:12]}..."
                )

            prev_hash = stored_hash

        valid = len(errors) == 0
        return valid, errors
