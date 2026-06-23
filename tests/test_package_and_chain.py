# SPDX-License-Identifier: GPL-3.0-only

import tempfile
import unittest
from pathlib import Path

from velvet_receipts import GENESIS_HASH, Receipt, ReceiptLogger


class ReceiptsPackageTests(unittest.TestCase):
    def test_public_package_imports(self):
        self.assertEqual(GENESIS_HASH, "0" * 64)

    def test_two_receipts_form_valid_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipts.log"
            logger = ReceiptLogger(str(path))

            first = logger.log(
                Receipt(
                    event="boot",
                    decision="allow",
                    result="ready",
                    policy="BootPolicy",
                    authorized_by="Court",
                )
            )
            second = logger.log(
                Receipt(
                    event="observe",
                    decision="record",
                    result="stored",
                    policy="ObservationPolicy",
                    authorized_by="Court",
                )
            )

            self.assertEqual(first.previous_hash, GENESIS_HASH)
            self.assertEqual(second.previous_hash, first.hash)
            self.assertEqual(logger.verify_chain(), (True, []))


if __name__ == "__main__":
    unittest.main()
