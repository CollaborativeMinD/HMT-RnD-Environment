"""Bounded current-lineage discovery prevents omitted earlier authority drift."""
import sqlite3
from pathlib import Path

from .lane_evidence import digest_file
from .lane_models import Receipt, Reopen
from .lane_queries import read_receipt


def discover_changes(db: sqlite3.Connection, event: Reopen, root: Path,
                     policy: str, epoch: int) -> list[Receipt]:
    current = db.execute("SELECT id FROM lane_candidates WHERE lineage=? "
                         "AND id NOT IN(SELECT candidate FROM lane_invalidations) LIMIT 27",
                         (event.lineage_id,)).fetchall()
    if len(current) > 26:
        raise PermissionError("LANE_CURRENT_LINEAGE_BOUND")
    changed = []
    for row in current:
        receipt = read_receipt(db, row[0])
        if event.reason == "ARTIFACT_DRIFT":
            altered = digest_file(receipt.candidate.artifact, root)
            mismatch = altered != receipt.candidate.artifact_sha256
        elif event.reason == "POLICY_DRIFT":
            mismatch = (receipt.gate.policy, receipt.gate.epoch) != (policy, epoch)
        else:
            mismatch = receipt.gate.outcome == "DENIED"
        if mismatch:
            changed.append(receipt)
    return changed
