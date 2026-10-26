"""Fault actual SQL product and output size; no success seal may be returned."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hmt_rnd import verification_ledger
from hmt_rnd.verification_models import Dimensions, Invariant


def dimensions() -> Dimensions:
    item = Invariant(requirement_id="HMT-F01", gate_id="G-ARCH",
                     mechanisms=("control",), acceptance="Pinned")
    return Dimensions(invariants=(item,), mechanisms=("control",), gates=("G-ARCH",))


class OutputBoundaryTests(unittest.TestCase):
    def test_missing_product_row_mutation_is_rejected_before_seal(self) -> None:
        sql = verification_ledger.PRODUCT + "DELETE FROM candidates;"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "incomplete.sqlite"
            with patch.object(verification_ledger, "PRODUCT", sql):
                with self.assertRaisesRegex(ValueError, "CANDIDATE_SPACE_CARDINALITY_MISMATCH"):
                    verification_ledger.create_ledger(path, dimensions())
            self.assertTrue(path.exists(), "Failed artifact remains available for investigation")

    def test_actual_oversized_output_is_rejected(self) -> None:
        sql = verification_ledger.PRODUCT + (
            "CREATE TABLE padding AS SELECT zeroblob(67108864) AS bytes;"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized.sqlite"
            with patch.object(verification_ledger, "PRODUCT", sql):
                with self.assertRaisesRegex(ValueError, "CANDIDATE_OUTPUT_LIMIT_EXCEEDED"):
                    verification_ledger.create_ledger(path, dimensions())
            self.assertGreater(path.stat().st_size, 67108864)


if __name__ == "__main__":
    unittest.main()
