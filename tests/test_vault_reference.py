# SPDX-License-Identifier: GPL-3.0-only

import pytest

from vault_reference import validate_vault_object_ref


def _ref(**overrides):
    value = {
        "schema": "velvet.vault.object_ref.v1",
        "object_id": "obj-123",
        "path": "media/video/retained/incident.mp4",
        "kind": "video",
        "sha256": "a" * 64,
        "retention": "PROTECTED",
    }
    value.update(overrides)
    return value


def test_accepts_minimal_vault_object_reference():
    result = validate_vault_object_ref(_ref())
    assert result["path"] == "media/video/retained/incident.mp4"
    assert result["retention"] == "PROTECTED"


@pytest.mark.parametrize(
    "path",
    (
        "/srv/velvet/media/video/a.mp4",
        "../outside.mp4",
        "media/../outside.mp4",
        "~/secret.mp4",
    ),
)
def test_rejects_absolute_or_escaping_paths(path):
    with pytest.raises(ValueError):
        validate_vault_object_ref(_ref(path=path))


def test_rejects_invalid_sha256():
    with pytest.raises(ValueError, match="sha256"):
        validate_vault_object_ref(_ref(sha256="not-a-digest"))


def test_rejects_unknown_fields_to_keep_receipts_minimal():
    with pytest.raises(ValueError, match="unexpected"):
        validate_vault_object_ref(_ref(raw_video_bytes="forbidden"))


def test_rejects_unknown_retention_class():
    with pytest.raises(ValueError, match="retention"):
        validate_vault_object_ref(_ref(retention="DELETE_WHEN_BORED"))
