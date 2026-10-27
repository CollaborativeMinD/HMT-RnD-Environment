"""Typed append-only successor event routes to earliest changed stage owner."""
import sqlite3
from pathlib import Path

from .host_admission import authorize_and_checkpoint
from .host_models import Identity, Request
from .lane_discovery import discover_changes
from .lane_drift import artifact_changed
from .lane_models import Receipt, Reopen, ReopenEvent
from .lane_queries import check_parent, read_receipt
from .lane_reservation import require_available
from .lane_stages import STAGES, lane
from .lane_submission import ClockProvider, check_stage


def changed(db: sqlite3.Connection, event: Reopen, root: Path,
            policy: str, epoch: int) -> list[Receipt]:
    rows = [read_receipt(db, value) for value in event.changed_candidates]
    if len(set(event.changed_candidates)) != len(rows):
        raise PermissionError("LANE_DUPLICATE_CHANGE_REFERENCE")
    for receipt in rows:
        if receipt.candidate.lineage_id != event.lineage_id:
            raise PermissionError("LANE_REOPEN_LINEAGE_MISMATCH")
        invalidated = db.execute("SELECT 1 FROM lane_invalidations WHERE candidate=?",
                                 (receipt.candidate.candidate_id,)).fetchone()
        if invalidated:
            raise PermissionError("LANE_REOPEN_NOT_CURRENT")
        if event.reason == "ARTIFACT_DRIFT":
            if not artifact_changed(receipt, root):
                raise PermissionError("LANE_REOPEN_WITHOUT_ARTIFACT_CHANGE")
        elif event.reason == "POLICY_DRIFT":
            if (receipt.gate.policy, receipt.gate.epoch) == (policy, epoch):
                raise PermissionError("LANE_REOPEN_WITHOUT_POLICY_CHANGE")
        elif receipt.gate.outcome != "DENIED":
            raise PermissionError("LANE_REOPEN_WITHOUT_DENIAL")
    return rows


def reopen_candidate(db: sqlite3.Connection, identity: Identity, request: Request,
                     event: Reopen, clock: ClockProvider) -> ReopenEvent:
    event = Reopen.model_validate_json(event.model_dump_json())
    now = clock()
    authority = authorize_and_checkpoint(db, identity, request, now)
    rows = changed(db, event, Path(request.root), authority.policy, authority.epoch)
    rows += discover_changes(db, event, Path(request.root), authority.policy, authority.epoch)
    earliest = min(rows, key=lambda row: STAGES.index(row.candidate.stage))
    stage = earliest.candidate.stage
    check_stage(identity, request, stage, "lane.reopen")
    if request.task_id != earliest.task_id:
        raise PermissionError("LANE_REOPEN_TASK_MISMATCH")
    if request.revision != earliest.task_revision:
        raise PermissionError("LANE_REOPEN_REVISION_MISMATCH")
    policy_drift = any((row.gate.policy, row.gate.epoch) != (authority.policy, authority.epoch)
                       for row in rows)
    if policy_drift and identity.role != "human_architect":
        raise PermissionError("LANE_POLICY_REOPEN_REQUIRES_ARCHITECT")
    require_available(db, event.successor_candidate_id)
    scope = db.execute("SELECT id,stage FROM lane_candidates WHERE lineage=?",
                       (event.lineage_id,)).fetchall()
    invalidated = tuple(row[0] for row in scope if STAGES.index(row[1]) >= STAGES.index(stage))
    result = ReopenEvent(request=event, required_stage=stage, required_lane=lane(stage),
                         origin_receipt_sha256=earliest.receipt_sha256,
                         invalidated_candidates=invalidated, issued_by=identity.principal,
                         issued_at=now.now, policy=authority.policy, epoch=authority.epoch,
                         task_id=request.task_id, task_revision=request.revision)
    authorize_and_checkpoint(db, identity, request, clock())
    check_parent(db, earliest.candidate, Path(request.root), authority.policy, authority.epoch)
    db.execute("INSERT INTO lane_reopens VALUES(?,?,?,?,?)", (event.event_id,
               event.lineage_id, stage, event.successor_candidate_id, result.model_dump_json()))
    db.executemany("INSERT INTO lane_invalidations VALUES(?,?)",
                   [(event.event_id, value) for value in invalidated])
    return result
