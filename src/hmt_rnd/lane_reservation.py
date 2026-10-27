"""Successor IDs are reserved globally for one exact event, lineage and stage."""
import sqlite3

from .lane_models import Candidate


def check_reservation(db: sqlite3.Connection, candidate: Candidate) -> None:
    row = db.execute("SELECT id,lineage,stage FROM lane_reopens WHERE successor=?",
                     (candidate.candidate_id,)).fetchone()
    expected = (candidate.reopen_id, candidate.lineage_id, candidate.stage)
    if row is not None and tuple(row) != expected:
        raise PermissionError("LANE_RESERVED_SUCCESSOR_BINDING")


def require_available(db: sqlite3.Connection, successor: str) -> None:
    if db.execute("SELECT 1 FROM lane_candidates WHERE id=?", (successor,)).fetchone():
        raise PermissionError("LANE_SUCCESSOR_ALREADY_EXISTS")
    if db.execute("SELECT 1 FROM lane_reopens WHERE successor=?", (successor,)).fetchone():
        raise PermissionError("LANE_SUCCESSOR_ALREADY_RESERVED")
