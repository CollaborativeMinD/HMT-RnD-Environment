"""Trusted provisioning mutations; no wire adapter exposes these functions."""
import sqlite3

from .host_models import Assignment, Grant


def assign(connection: sqlite3.Connection, task: Assignment) -> None:
    task = Assignment.model_validate_json(task.model_dump_json())
    previous = connection.execute(
        "SELECT revision FROM host_tasks WHERE task_id=?", (task.task_id,)
    ).fetchone()
    if previous and task.revision <= previous[0]:
        raise PermissionError("HOST_REVISION_NOT_ADVANCED")
    connection.execute("INSERT OR REPLACE INTO host_tasks VALUES(?,?,?)",
                       (task.task_id, task.principal, task.revision))


def grant(connection: sqlite3.Connection, authority: Grant) -> None:
    authority = Grant.model_validate_json(authority.model_dump_json())
    if authority.not_before >= min(authority.expires, authority.evidence_expires):
        raise PermissionError("HOST_GRANT_INTERVAL")
    connection.execute("INSERT OR REPLACE INTO host_grants VALUES(?,?,?,?,0)",
                       (authority.principal, authority.task_id, authority.operation,
                        authority.model_dump_json()))
