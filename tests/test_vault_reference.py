# SPDX-License-Identifier: GPL-3.0-only

import unittest

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


class VaultReferenceTests(unittest.TestCase):
    def test_accepts_minimal_vault_object_reference(self):
        result = validate_vault_object_ref(_ref())
        self.assertEqual(result["path"], "media/video/retained/incident.mp4")
        self.assertEqual(result["retention"], "PROTECTED")

    def test_rejects_absolute_or_escaping_paths(self):
        for path in (
            "/srv/velvet/media/video/a.mp4",
            "../outside.mp4",
            "media/../outside.mp4",
            "~/secret.mp4",
        ):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    validate_vault_object_ref(_ref(path=path))

    def test_rejects_invalid_sha256(self):
        with self.assertRaisesRegex(ValueError, "sha256"):
            validate_vault_object_ref(_ref(sha256="not-a-digest"))

    def test_rejects_unknown_fields_to_keep_receipts_minimal(self):
        with self.assertRaisesRegex(ValueError, "unexpected"):
            validate_vault_object_ref(_ref(raw_video_bytes="forbidden"))

    def test_rejects_unknown_retention_class(self):
        with self.assertRaisesRegex(ValueError, "retention"):
            validate_vault_object_ref(_ref(retention="DELETE_WHEN_BORED"))


if __name__ == "__main__":
    unittest.main()
