"""Read immutable lifecycle receipts and validate current predecessor chain."""
import hashlib
import json
import sqlite3
from pathlib import Path

from .lane_evidence import verify_receipt_artifacts
from .lane_models import Candidate, Receipt
from .lane_stages import predecessor


def receipt_digest(body: dict[str, object]) -> str:
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def read_receipt(db: sqlite3.Connection, candidate_id: str) -> Receipt:
    row = db.execute("SELECT body,digest FROM lane_candidates WHERE id=?",
                     (candidate_id,)).fetchone()
    if row is None:
        raise PermissionError("LANE_PREDECESSOR_MISSING")
    receipt = Receipt.model_validate_json(row[0])
    if receipt.candidate.candidate_id != candidate_id:
        raise PermissionError("LANE_RECEIPT_IDENTITY_DRIFT")
    body = receipt.model_dump(mode="json", exclude={"receipt_sha256"})
    if receipt.receipt_sha256 != row[1] or receipt_digest(body) != row[1]:
        raise PermissionError("LANE_RECEIPT_INTEGRITY")
    return receipt


def check_parent(db: sqlite3.Connection, candidate: Candidate, root: Path,
                 policy: str, epoch: int) -> str | None:
    expected = predecessor(candidate.stage)
    if expected is None:
        if candidate.predecessor_id is not None:
            raise PermissionError("LANE_INITIAL_PREDECESSOR_FORBIDDEN")
        return None
    if candidate.predecessor_id is None:
        raise PermissionError("LANE_PREDECESSOR_REQUIRED")
    cursor, expected_stage = candidate.predecessor_id, expected
    immediate = None
    for _ in range(26):
        receipt = read_receipt(db, cursor)
        parent = receipt.candidate
        invalid = db.execute("SELECT 1 FROM lane_invalidations WHERE candidate=?",
                             (cursor,)).fetchone()
        if invalid or receipt.gate.outcome != "SEALED":
            raise PermissionError("LANE_PREDECESSOR_NOT_CURRENT")
        if parent.lineage_id != candidate.lineage_id or parent.stage != expected_stage:
            raise PermissionError("LANE_PREDECESSOR_ORDER")
        if (receipt.gate.policy, receipt.gate.epoch) != (policy, epoch):
            raise PermissionError("LANE_PREDECESSOR_POLICY_STALE")
        verify_receipt_artifacts(receipt, root)
        immediate = immediate or receipt.receipt_sha256
        expected_stage = predecessor(parent.stage)
        if expected_stage is None:
            return immediate
        if parent.predecessor_id is None:
            raise PermissionError("LANE_ANCESTOR_MISSING")
        cursor = parent.predecessor_id
    raise PermissionError("LANE_PREDECESSOR_BOUND")
