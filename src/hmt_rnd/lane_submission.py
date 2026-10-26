"""Atomic stage progression requires current host admission and bound gate evidence."""
import sqlite3
from collections.abc import Callable
from pathlib import Path

from .host_admission import authorize_and_checkpoint
from .host_models import Clock, Identity, Request
from .lane_artifacts import preserve
from .lane_evidence import verify_artifact, verify_result
from .lane_models import Candidate, GateContext, GateResult, Receipt
from .lane_queries import check_parent
from .lane_records import record
from .lane_stages import ROLE_CEILINGS
from .lane_successor import check_pending

Evaluator = Callable[[GateContext], GateResult]
ClockProvider = Callable[[], Clock]


def check_stage(identity: Identity, request: Request, stage: str, operation: str) -> None:
    if request.operation != operation or identity.stage != stage:
        raise PermissionError("LANE_STAGE_OR_OPERATION_DENIED")
    role = identity.role.lower().replace("_", "").replace("-", "")
    if role in ROLE_CEILINGS:
        raise PermissionError("LANE_EVALUATOR_ROLE_CANNOT_PROGRESS")
    if identity.lane != ("Build" if stage.startswith("B") else stage.rstrip("123")):
        raise PermissionError("LANE_OWNER_DENIED")


def check_successor(db: sqlite3.Connection, candidate: Candidate) -> None:
    check_pending(db, candidate)
    current = db.execute("SELECT id FROM lane_candidates WHERE lineage=? AND stage=? "
                         "AND id NOT IN(SELECT candidate FROM lane_invalidations)",
                         (candidate.lineage_id, candidate.stage)).fetchall()
    if current:
        raise PermissionError("LANE_TYPED_REOPEN_REQUIRED")
    previous = db.execute("SELECT id FROM lane_candidates WHERE lineage=? AND stage=?",
                          (candidate.lineage_id, candidate.stage)).fetchall()
    if previous and candidate.reopen_id is None:
        from .lane_successor import has_reopen_ancestor
        if not has_reopen_ancestor(db, candidate.predecessor_id):
            raise PermissionError("LANE_TYPED_SUCCESSOR_REQUIRED")
    if candidate.reopen_id is not None:
        row = db.execute("SELECT stage,successor FROM lane_reopens WHERE id=? AND lineage=?",
                         (candidate.reopen_id, candidate.lineage_id)).fetchone()
        if row is None or tuple(row) != (candidate.stage, candidate.candidate_id):
            raise PermissionError("LANE_SUCCESSOR_BINDING")


def submit(db: sqlite3.Connection, identity: Identity, request: Request, candidate: Candidate,
           clock: ClockProvider, evaluator: Evaluator | None) -> Receipt:
    candidate = Candidate.model_validate_json(candidate.model_dump_json())
    if evaluator is None:
        raise PermissionError("LANE_EVALUATOR_UNBOUND")
    check_stage(identity, request, candidate.stage, "lane.seal")
    authority = authorize_and_checkpoint(db, identity, request, clock())
    check_successor(db, candidate)
    root = Path(request.root)
    verify_artifact(candidate, root)
    parent = check_parent(db, candidate, root, authority.policy, authority.epoch)
    context = GateContext(candidate=candidate, predecessor_sha256=parent,
                          policy=authority.policy, epoch=authority.epoch,
                          principal=identity.principal, task_id=request.task_id,
                          task_revision=request.revision)
    result = GateResult.model_validate_json(evaluator(context).model_dump_json())
    verify_artifact(candidate, root)
    verify_result(context, result, root)
    check_parent(db, candidate, root, authority.policy, authority.epoch)
    preserve(db, candidate, result, root)
    final_clock = clock()
    authorize_and_checkpoint(db, identity, request, final_clock)
    return record(db, identity, request, candidate, result, final_clock.now)
