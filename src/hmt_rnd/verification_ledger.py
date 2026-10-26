"""Exclusive creation and integrity seal for a finite, complete candidate ledger."""
import hashlib
import os
import sqlite3
from pathlib import Path

from .verification_models import Dimensions
from .verification_sql import MECHANISM_IDS, PRODUCT, SCHEMA, seal_sql


def create_ledger(path: Path, dimensions: Dimensions) -> str:
    if not set(dimensions.mechanisms).issubset(MECHANISM_IDS):
        raise ValueError("MECHANISM_IDENTITY_UNBOUND")
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    with sqlite3.connect(path) as database:
        database.executescript(SCHEMA)
        database.executemany("INSERT INTO invariants VALUES (?,?,?)", (
            (i.requirement_id, i.gate_id, i.acceptance) for i in dimensions.invariants
        ))
        database.executemany("INSERT INTO mechanisms VALUES (?,?)", (
            (value, MECHANISM_IDS[value]) for value in dimensions.mechanisms
        ))
        database.executemany("INSERT INTO gates VALUES (?)", (
            (value,) for value in dimensions.gates
        ))
        database.executemany("INSERT INTO applicable VALUES (?,?)", (
            (i.requirement_id, m) for i in dimensions.invariants for m in i.mechanisms
        ))
        digest = hashlib.sha256(dimensions.model_dump_json().encode()).hexdigest()
        database.execute("INSERT INTO metadata VALUES ('dimension_sha256',?)", (digest,))
        database.commit()
        database.executescript(PRODUCT)
        expected = len(dimensions.invariants) * len(dimensions.mechanisms) * len(dimensions.gates)
        actual = database.execute("SELECT count(*) FROM candidates").fetchone()[0]
        if actual != expected:
            raise ValueError("CANDIDATE_SPACE_CARDINALITY_MISMATCH")
        database.executescript(seal_sql())
    if path.stat().st_size > 67108864:
        raise ValueError("CANDIDATE_OUTPUT_LIMIT_EXCEEDED")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_seal(path: Path, expected_sha256: str) -> None:
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError("LEDGER_INTEGRITY_MISMATCH")
