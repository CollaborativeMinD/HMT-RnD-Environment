"""Common direct/MCP admission boundary; no target dispatch or executable grant."""
import sqlite3

from .host_checks import authorize
from .host_models import Clock, Decision, Identity, Request
from .host_store import HostStore


def admit(store: HostStore, identity: Identity, request: Request, clock: Clock) -> Decision:
    identity = Identity.model_validate_json(identity.model_dump_json())
    request = Request.model_validate_json(request.model_dump_json())
    clock = Clock.model_validate_json(clock.model_dump_json())
    with store.transaction() as connection:
        return authorize_and_checkpoint(connection, identity, request, clock)


def authorize_and_checkpoint(connection: sqlite3.Connection, identity: Identity,
                             request: Request, clock: Clock) -> Decision:
    """Caller owns IMMEDIATE transaction; this host helper checkpoints host time."""
    decision = authorize(connection, identity, request, clock)
    connection.execute("UPDATE host_meta SET last_clock=? WHERE id=1", (clock.now,))
    return decision


def admit_wire(store: HostStore, identity: Identity, payload: str, clock: Clock) -> Decision:
    if len(payload.encode()) > 65536:
        raise ValueError("HOST_INPUT_BOUND")
    return admit(store, identity, Request.model_validate_json(payload), clock)
