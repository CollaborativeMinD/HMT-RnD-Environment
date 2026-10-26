"""Only a typed reopening lineage can regenerate invalidated descendants."""
import sqlite3

from .lane_models import Candidate
from .lane_queries import read_receipt
from .lane_reservation import check_reservation


def check_pending(db: sqlite3.Connection, candidate: Candidate) -> None:
    check_reservation(db, candidate)
    rows = db.execute("SELECT id,successor FROM lane_reopens WHERE lineage=? AND stage=? "
                       "AND id NOT IN(SELECT event FROM lane_closures)",
                       (candidate.lineage_id, candidate.stage)).fetchall()
    if rows and (len(rows) != 1 or tuple(rows[0]) != (candidate.reopen_id,
                                                    candidate.candidate_id)):
        raise PermissionError("LANE_TYPED_SUCCESSOR_REQUIRED")


def has_reopen_ancestor(db: sqlite3.Connection, candidate_id: str | None) -> bool:
    for _ in range(26):
        if candidate_id is None:
            return False
        receipt = read_receipt(db, candidate_id)
        if receipt.candidate.reopen_id is not None:
            return db.execute("SELECT 1 FROM lane_closures WHERE event=? AND candidate=?",
                              (receipt.candidate.reopen_id, candidate_id)).fetchone() is not None
        candidate_id = receipt.candidate.predecessor_id
    return False
