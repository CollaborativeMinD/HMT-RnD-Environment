"""Retain baseline candidate IDs and refuse unbound mechanism extensions."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from hmt_rnd.verification_ledger import create_ledger
from hmt_rnd.verification_models import Dimensions, Invariant


class IdentityTests(unittest.TestCase):
    def test_baseline_candidate_identity(self) -> None:
        invariant = Invariant(requirement_id="HMT-F01", gate_id="G-ARCH",
                              mechanisms=("control",), acceptance="Pinned contract")
        dimensions = Dimensions(invariants=(invariant,), mechanisms=("control",),
                                gates=("G-ARCH",))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite"
            create_ledger(path, dimensions)
            with sqlite3.connect(path) as database:
                identity = database.execute("SELECT candidate_id FROM candidates").fetchone()[0]
            self.assertEqual(identity, "I-F01__M00__G-ARCH")

    def test_unknown_mechanism_does_not_create_file(self) -> None:
        invariant = Invariant(requirement_id="HMT-F01", gate_id="G-ARCH",
                              mechanisms=("new",), acceptance="Pinned contract")
        dimensions = Dimensions(invariants=(invariant,), mechanisms=("new",),
                                gates=("G-ARCH",))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite"
            with self.assertRaisesRegex(ValueError, "MECHANISM_IDENTITY_UNBOUND"):
                create_ledger(path, dimensions)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
