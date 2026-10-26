"""Read-only host intersection, suitable inside an existing custody transaction."""
import sqlite3
from pathlib import Path

from .host_models import Clock, Decision, Grant, Identity, Request


def authorize(connection: sqlite3.Connection, identity: Identity,
              request: Request, clock: Clock) -> Decision:
    meta = connection.execute("SELECT policy,epoch,last_clock FROM host_meta WHERE id=1").fetchone()
    task = connection.execute("SELECT principal,revision FROM host_tasks WHERE task_id=?",
                              (request.task_id,)).fetchone()
    row = connection.execute(
        "SELECT body,revoked FROM host_grants WHERE principal=? AND task_id=? AND operation=?",
        (identity.principal, request.task_id, request.operation),
    ).fetchone()
    if not meta or not task or not row or row[1]:
        raise PermissionError("HOST_GRANT_DENIED")
    authority = Grant.model_validate_json(row[0])
    if tuple(task) != (identity.principal, request.revision) or authority.revision != task[1]:
        raise PermissionError("HOST_TASK_REVISION_DENIED")
    expected = {k: getattr(authority, k) for k in Identity.model_fields}
    if identity.model_dump() != expected:
        raise PermissionError("HOST_IDENTITY_SCOPE_DENIED")
    if (authority.policy, authority.epoch) != meta[:2]:
        raise PermissionError("HOST_POLICY_STALE")
    if clock.now < meta[2]:
        raise PermissionError("HOST_CLOCK_ROLLBACK")
    if clock.now - clock.uncertainty < authority.not_before:
        raise PermissionError("HOST_LEASE_NOT_STARTED")
    if clock.now + clock.uncertainty >= min(authority.expires, authority.evidence_expires):
        raise PermissionError("HOST_LEASE_OR_EVIDENCE_EXPIRED")
    if not Path(request.root).resolve().is_relative_to(Path(authority.root).resolve()):
        raise PermissionError("HOST_ROOT_DENIED")
    if request.destination != authority.destination:
        raise PermissionError("HOST_EGRESS_DENIED")
    return Decision(principal=identity.principal, task_id=request.task_id,
                    task_revision=request.revision, operation=request.operation,
                    policy=authority.policy, epoch=authority.epoch)
