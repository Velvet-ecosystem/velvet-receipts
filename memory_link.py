# SPDX-License-Identifier: GPL-3.0-only
"""Public-safe memory references for receipt context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

_FORBIDDEN_KEYS = {
    "payload",
    "raw_memory",
    "conversation",
    "biometric_data",
    "embedding",
    "executor",
    "capability_token",
}


@dataclass(frozen=True)
class MemoryLink:
    memory_event_id: str
    memory_kind: str
    authority_status: str
    confidence: Optional[float] = None
    source_receipt_id: Optional[str] = None

    def to_context(self) -> Dict[str, Any]:
        _text(self.memory_event_id, "memory_event_id")
        _text(self.memory_kind, "memory_kind")
        _text(self.authority_status, "authority_status")
        if self.confidence is not None:
            _unit(self.confidence, "confidence")
        if self.source_receipt_id is not None:
            _text(self.source_receipt_id, "source_receipt_id")

        context: Dict[str, Any] = {
            "memory_event_id": self.memory_event_id,
            "memory_kind": self.memory_kind,
            "authority_status": self.authority_status,
        }
        if self.confidence is not None:
            context["confidence"] = float(self.confidence)
        if self.source_receipt_id is not None:
            context["source_receipt_id"] = self.source_receipt_id
        return context


def validate_memory_link(document: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(document, Mapping):
        raise ValueError("memory link must be a mapping")
    forbidden = _FORBIDDEN_KEYS.intersection(document)
    if forbidden:
        raise ValueError("memory link contains forbidden private fields")
    allowed = {
        "memory_event_id",
        "memory_kind",
        "authority_status",
        "confidence",
        "source_receipt_id",
    }
    unknown = set(document) - allowed
    if unknown:
        raise ValueError("memory link contains unsupported fields")
    return MemoryLink(
        memory_event_id=document.get("memory_event_id"),
        memory_kind=document.get("memory_kind"),
        authority_status=document.get("authority_status"),
        confidence=document.get("confidence"),
        source_receipt_id=document.get("source_receipt_id"),
    ).to_context()


def _unit(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("{} must be numeric".format(name))
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError("{} must be between 0 and 1".format(name))


def _text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))
