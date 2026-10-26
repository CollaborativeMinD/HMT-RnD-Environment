"""Only a typed reopening lineage can regenerate invalidated descendants."""
import sqlite3

from .lane_queries import read_receipt


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
