import unittest

from memory_link import validate_memory_link


class MemoryLinkPrivateFieldTests(unittest.TestCase):
    def test_private_payload_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_memory_link({
                "memory_event_id": "memory-1",
                "memory_kind": "fact",
                "authority_status": "accepted",
                "payload": {"private": True},
            })


if __name__ == "__main__":
    unittest.main()
