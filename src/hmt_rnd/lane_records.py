"""Immutable receipt insertion shares the artifact/host transaction."""
import json
import sqlite3

from .host_models import Identity, Request
from .lane_models import Candidate, GateResult, Receipt
from .lane_queries import receipt_digest


def record(db: sqlite3.Connection, identity: Identity, request: Request,
           candidate: Candidate, result: GateResult, issued_at: float) -> Receipt:
    body = dict(candidate=candidate.model_dump(mode="json"), gate=result.model_dump(mode="json"),
                principal=identity.principal, task_id=request.task_id,
                task_revision=request.revision, issued_at=issued_at)
    sealed = {**body, "receipt_sha256": receipt_digest(body)}
    receipt = Receipt.model_validate_json(json.dumps(sealed))
    db.execute("INSERT INTO lane_candidates VALUES(?,?,?,?,?)", (candidate.candidate_id,
               candidate.lineage_id, candidate.stage, receipt.model_dump_json(),
               receipt.receipt_sha256))
    if candidate.reopen_id:
        db.execute("INSERT INTO lane_closures VALUES(?,?,?)", (candidate.reopen_id,
                   candidate.candidate_id, receipt.receipt_sha256))
    return receipt
