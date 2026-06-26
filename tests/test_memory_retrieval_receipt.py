# SPDX-License-Identifier: GPL-3.0-only

import unittest

from memory_retrieval_receipt import memory_retrieval_receipt_from_envelope


class MemoryRetrievalReceiptTests(unittest.TestCase):
    def envelope(self):
        return {
            "event_type": "EXECUTION_COMPLETED",
            "source": "velvet-runtime",
            "subject_id": "owner",
            "payload": {
                "state": "completed",
                "intent_id": "memory-recall-1",
                "token_id": "token-1",
                "capability": "observe.memory",
                "target": "memory",
                "executor_name": "memory-recall",
                "query_event_id": "query-1",
                "result_count": 1,
                "results": [{"event_id": "memory-1", "raw_memory": "hidden"}],
            },
        }

    def links(self):
        return [{
            "memory_event_id": "memory-1",
            "memory_kind": "fact",
            "authority_status": "accepted",
            "confidence": 0.9,
        }]

    def test_builds_minimal_receipt_context(self):
        receipt = memory_retrieval_receipt_from_envelope(self.envelope(), self.links())

        self.assertEqual(receipt.context["schema"], "velvet.runtime.receipt.v1")
        self.assertEqual(receipt.context["query_event_id"], "query-1")
        self.assertEqual(receipt.context["result_count"], 1)
        self.assertEqual(receipt.context["memory_links"][0]["memory_event_id"], "memory-1")
        self.assertNotIn("results", receipt.context)
        self.assertFalse(receipt.context["private_memory_included"])
        self.assertTrue(receipt.constraints["memory_payload_forbidden"])
        self.assertTrue(receipt.constraints["memory_links_are_context_not_authority"])

    def test_rejects_link_count_mismatch(self):
        with self.assertRaises(ValueError):
            memory_retrieval_receipt_from_envelope(self.envelope(), [])

    def test_rejects_private_fields_in_links(self):
        links = self.links()
        links[0]["raw_memory"] = "hidden"
        with self.assertRaises(ValueError):
            memory_retrieval_receipt_from_envelope(self.envelope(), links)


if __name__ == "__main__":
    unittest.main()
