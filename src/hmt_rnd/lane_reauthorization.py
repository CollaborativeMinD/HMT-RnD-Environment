"""Explicit, host-admitted architect recovery for an immutable pending event."""
import sqlite3

from .host_admission import authorize_and_checkpoint
from .host_models import Identity, Request
from .lane_authorization_models import Reauthorization
from .lane_event_authority import bound_fields, read_event, validate_origin
from .lane_submission import ClockProvider, check_stage


def reauthorize(db: sqlite3.Connection, identity: Identity, request: Request, event_id: str,
                clock: ClockProvider) -> Reauthorization:
    now = clock()
    authority = authorize_and_checkpoint(db, identity, request, now)
    event, digest = read_event(db, event_id)
    check_stage(identity, request, event.required_stage, "lane.reauthorize")
    validate_origin(db, event, request)
    if identity.role != "human_architect":
        raise PermissionError("LANE_REAUTHORIZATION_REQUIRES_ARCHITECT")
    if db.execute("SELECT 1 FROM lane_closures WHERE event=?", (event_id,)).fetchone():
        raise PermissionError("LANE_REAUTHORIZATION_CLOSED")
    fields = bound_fields(event, digest, authority)
    approval = Reauthorization(**fields, issued_by=identity.principal, issued_at=now.now)
    final = authorize_and_checkpoint(db, identity, request, clock())
    if (final.policy, final.epoch) != (authority.policy, authority.epoch):
        raise PermissionError("LANE_REOPEN_AUTHORITY_STALE")
    prior = db.execute("SELECT body FROM lane_reauthorizations WHERE event=? AND policy=? "
                       "AND epoch=?", (event_id, authority.policy, authority.epoch)).fetchone()
    if prior:
        existing = Reauthorization.model_validate_json(prior[0])
        if any(existing.model_dump()[key] != value for key, value in fields.items()):
            raise PermissionError("LANE_REAUTHORIZATION_BINDING")
        return existing
    db.execute("INSERT INTO lane_reauthorizations VALUES(?,?,?,?)", (event_id, authority.policy,
               authority.epoch, approval.model_dump_json()))
    return approval
