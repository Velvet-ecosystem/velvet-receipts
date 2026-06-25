import unittest

from memory_link import MemoryLink


class MemoryLinkContextTests(unittest.TestCase):
    def test_minimal_context(self):
        context = MemoryLink("memory-1", "fact", "accepted", 0.9, "receipt-1").to_context()
        self.assertEqual(context["memory_event_id"], "memory-1")
        self.assertEqual(context["memory_kind"], "fact")
        self.assertEqual(context["authority_status"], "accepted")


if __name__ == "__main__":
    unittest.main()
