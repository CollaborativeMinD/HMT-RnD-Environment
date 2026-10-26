"""Event policy authority is checked separately from the current worker grant."""
import hashlib
import sqlite3

from pydantic import ValidationError

from .host_models import Decision, Request
from .lane_authorization_models import Reauthorization
from .lane_models import Candidate, ReopenEvent
from .lane_queries import read_receipt


def read_event(db: sqlite3.Connection, event_id: str) -> tuple[ReopenEvent, str]:
    row = db.execute("SELECT lineage,stage,successor,body FROM lane_reopens WHERE id=?",
                     (event_id,)).fetchone()
    if row is None:
        raise PermissionError("LANE_REOPEN_UNKNOWN")
    try:
        event = ReopenEvent.model_validate_json(row[3])
    except ValidationError as error:
        raise PermissionError("LANE_REOPEN_BINDING_MISSING") from error
    expected = (event.request.lineage_id, event.required_stage,
                event.request.successor_candidate_id)
    if event.request.event_id != event_id or tuple(row[:3]) != expected:
        raise PermissionError("LANE_REOPEN_BINDING_MISMATCH")
    return event, hashlib.sha256(row[3].encode()).hexdigest()


def validate_origin(db: sqlite3.Connection, event: ReopenEvent, request: Request) -> None:
    row = db.execute("SELECT id FROM lane_candidates WHERE digest=?",
                     (event.origin_receipt_sha256,)).fetchone()
    if row is None:
        raise PermissionError("LANE_REOPEN_ORIGIN_MISSING")
    origin = read_receipt(db, row[0])
    actual = (origin.task_id, origin.task_revision, origin.candidate.lineage_id,
              origin.candidate.stage)
    expected = (event.task_id, event.task_revision, event.request.lineage_id, event.required_stage)
    if actual != expected or (request.task_id, request.revision) != expected[:2]:
        raise PermissionError("LANE_REOPEN_TASK_BINDING")


def bound_fields(event: ReopenEvent, digest: str, authority: Decision) -> dict:
    return dict(event_id=event.request.event_id, event_sha256=digest,
                origin_receipt_sha256=event.origin_receipt_sha256,
                lineage_id=event.request.lineage_id, stage=event.required_stage,
                task_id=event.task_id, task_revision=event.task_revision,
                policy=authority.policy, epoch=authority.epoch)


def check_event_authority(db: sqlite3.Connection, candidate: Candidate, request: Request,
                          authority: Decision) -> None:
    if candidate.reopen_id is None:
        return
    event, digest = read_event(db, candidate.reopen_id)
    validate_origin(db, event, request)
    if (event.policy, event.epoch) == (authority.policy, authority.epoch):
        return
    row = db.execute("SELECT body FROM lane_reauthorizations WHERE event=? AND policy=? "
                     "AND epoch=?", (candidate.reopen_id, authority.policy,
                                     authority.epoch)).fetchone()
    if row is None:
        raise PermissionError("LANE_REOPEN_AUTHORITY_STALE")
    approval = Reauthorization.model_validate_json(row[0]).model_dump()
    if any(approval[key] != value for key, value in bound_fields(event, digest, authority).items()):
        raise PermissionError("LANE_REAUTHORIZATION_BINDING")
