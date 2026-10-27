"""R-VERIFY-ID-001: canonical collisions reject before destination creation."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from hmt_rnd.verification_ledger import create_ledger
from hmt_rnd.verification_models import Dimensions, Invariant


def invariant(identity: str) -> Invariant:
    return Invariant(requirement_id=identity, gate_id="G-ARCH",
                     mechanisms=("control",), acceptance="Pinned predicate")


class CanonicalIdentityTests(unittest.TestCase):
    def test_collision_rejected_before_destination_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite"
            with self.assertRaisesRegex(ValidationError, "NORMALIZED_INVARIANT_COLLISION"):
                dimensions = Dimensions(invariants=(invariant("HMT-F01"), invariant("I-F01")),
                                        mechanisms=("control",), gates=("G-ARCH",))
                create_ledger(path, dimensions)
            self.assertFalse(path.exists())

    def test_controls_preserve_complete_product_and_existing_ids(self) -> None:
        dimensions = Dimensions(invariants=(invariant("HMT-F01"), invariant("I-F02"),
                                            invariant("HMTX-F01")),
                                mechanisms=("control", "crash"), gates=("G-ARCH", "G-OTHER"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite"
            create_ledger(path, dimensions)
            with sqlite3.connect(path) as database:
                rows = database.execute("SELECT * FROM candidates").fetchall()
            self.assertEqual(len(rows), 12)
            self.assertEqual(len({row[0] for row in rows}), 12)
            self.assertIn("I-F01__M00__G-ARCH", {row[0] for row in rows})
            self.assertIn("I-F02__M00__G-ARCH", {row[0] for row in rows})
            self.assertIn("HMTX-F01__M00__G-ARCH", {row[0] for row in rows})
            self.assertEqual(sum(row[4] == "NOT_APPLICABLE" for row in rows), 9)
            self.assertTrue(all(row[5] for row in rows if row[4] == "NOT_APPLICABLE"))


if __name__ == "__main__":
    unittest.main()
