# SPDX-License-Identifier: GPL-3.0-only
"""Validation helpers for receipt references to Velvet vault objects.

A vault reference is evidence context only. It does not make the referenced
bytes trusted, authorize retrieval, or grant filesystem access.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any, Dict, Mapping

_SCHEMA = "velvet.vault.object_ref.v1"
_RETENTION = {"CACHE", "ROLLING", "STANDARD", "PROTECTED", "PERMANENT"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def validate_vault_object_ref(value: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("vault object reference must be a mapping")

    allowed = {
        "schema",
        "object_id",
        "path",
        "kind",
        "sha256",
        "retention",
    }
    extra = set(value) - allowed
    if extra:
        raise ValueError("unexpected vault reference fields: {}".format(", ".join(sorted(extra))))

    if value.get("schema") != _SCHEMA:
        raise ValueError("unsupported vault object reference schema")

    object_id = _text(value.get("object_id"), "object_id")
    kind = _text(value.get("kind"), "kind")
    digest = _text(value.get("sha256"), "sha256").lower()
    if not _SHA256.fullmatch(digest):
        raise ValueError("sha256 must be 64 lowercase hexadecimal characters")

    retention = _text(value.get("retention"), "retention").upper()
    if retention not in _RETENTION:
        raise ValueError("unknown vault retention class")

    raw_path = _text(value.get("path"), "path").replace("\\", "/")
    path = PurePosixPath(raw_path)
    if path.is_absolute() or ".." in path.parts or raw_path.startswith("~"):
        raise ValueError("vault path must be relative and remain inside the vault")
    if "." in path.parts:
        raise ValueError("vault path may not contain dot segments")

    return {
        "schema": _SCHEMA,
        "object_id": object_id,
        "path": path.as_posix(),
        "kind": kind,
        "sha256": digest,
        "retention": retention,
    }


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))
    return value.strip()
