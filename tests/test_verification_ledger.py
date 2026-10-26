"""Retain full product; mutations and accidental overwrite fail loudly."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from hmt_rnd.verification_ledger import create_ledger, verify_seal
from hmt_rnd.verification_models import Dimensions, Invariant


def dimensions() -> Dimensions:
    invariant = Invariant(requirement_id="R-1", gate_id="G-1",
                          mechanisms=("control",), acceptance="Observed A must equal B")
    return Dimensions(invariants=(invariant,), mechanisms=("control", "crash"),
                      gates=("G-1", "G-2"))


class LedgerTests(unittest.TestCase):
    def test_product_and_retained_exclusions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite"
            seal = create_ledger(path, dimensions())
            verify_seal(path, seal)
            with sqlite3.connect(path) as database:
                rows = database.execute("SELECT * FROM candidates").fetchall()
                self.assertEqual(len(rows), 4)
                self.assertEqual(sum(r[4] == "APPLICABLE" for r in rows), 1)
                self.assertEqual(sum(bool(r[5]) for r in rows), 3)
                self.assertEqual({r[6] for r in rows}, {"NOT_APPLICABLE", "NOT_EXECUTED"})

    def test_delete_update_and_fabricated_pass_mutants(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite"
            create_ledger(path, dimensions())
            with sqlite3.connect(path) as database:
                for sql in ("DELETE FROM candidates", "UPDATE candidates SET violated_predicate=''",
                            "UPDATE candidates SET evidence_status='PASS'"):
                    with self.assertRaisesRegex(sqlite3.IntegrityError, "SEALED_LEDGER"):
                        database.execute(sql)

    def test_existing_destination_is_never_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite"
            seal = create_ledger(path, dimensions())
            with self.assertRaises(FileExistsError):
                create_ledger(path, dimensions())
            verify_seal(path, seal)

    def test_tampered_bytes_break_integrity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite"
            seal = create_ledger(path, dimensions())
            path.write_bytes(path.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "LEDGER_INTEGRITY_MISMATCH"):
                verify_seal(path, seal)

    def test_product_budget_is_checked_before_creation(self) -> None:
        with self.assertRaisesRegex(ValidationError, "CANDIDATE_SPACE_LIMIT_EXCEEDED"):
            Dimensions(**{**dimensions().model_dump(), "maximum_rows": 3})


if __name__ == "__main__":
    unittest.main()
