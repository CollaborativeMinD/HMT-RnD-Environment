"""Test-only independently authorized host and resource domains."""
import sqlite3
from pathlib import Path

from hmt_rnd.custody_adapter import CustodyStore
from hmt_rnd.custody_endpoint import Endpoint
from hmt_rnd.custody_models import Intent
from hmt_rnd.host_admission import authorize_and_checkpoint
from hmt_rnd.host_models import Assignment, Clock, Grant, Identity, Request
from hmt_rnd.host_store import HostStore

KEY = b"p1-fixture-endpoint-secret-32bytes!"
LOCAL = ("custody.stage", "custody.reserve", "custody.inspect", "custody.reconcile")
REMOTE = ("endpoint.apply", "endpoint.cancel")


def identity() -> Identity:
    return Identity(principal="alice", role="builder", lane="Build", stage="B3",
                    credential="fixture-credential")


def provision(path: Path, root: Path, operations: tuple[str, ...]) -> HostStore:
    store = HostStore.create(path, "p1")
    store.assign(Assignment(task_id="task1", principal="alice", revision=1))
    for operation in operations:
        store.grant(Grant(**identity().model_dump(), task_id="task1", operation=operation,
                          root=str(root), destination="local", policy="p1", epoch=1,
                          not_before=1.0, expires=100.0, evidence_expires=90.0))
    return store


def guard(root: Path, *, delete_reserve: bool = False, delete_all: bool = False,
          sham: bool = False):
    def authorize(db: sqlite3.Connection, operation: str, principal: str, effect: str) -> None:
        assert principal == "alice" and effect == "effect1"
        if sham:
            db.execute("SELECT 1").fetchone()
        if delete_all or (delete_reserve and operation == "custody.reserve"):
            return
        request = Request(task_id="task1", revision=1, operation=operation,
                          root=str(root), destination="local")
        authorize_and_checkpoint(db, identity(), request, Clock(now=10.0))
    return authorize


def open_domains(root: Path, **local_options):
    local = CustodyStore(root / "local.sqlite", guard(root, **local_options), {"endpoint": KEY})
    remote = Endpoint(root / "endpoint.sqlite", "endpoint", KEY, guard(root))
    intent = Intent(endpoint_id="endpoint", principal="alice", effect_id="effect1",
                    payload_digest="a" * 64)
    return local, remote, intent


def prepare(root: Path):
    provision(root / "local.sqlite", root, LOCAL)
    provision(root / "endpoint.sqlite", root, REMOTE)
    return open_domains(root)


def renew_local(root: Path) -> None:
    host = HostStore(root / "local.sqlite")
    for operation in LOCAL:
        host.grant(Grant(**identity().model_dump(), task_id="task1", operation=operation,
                         root=str(root), destination="local", policy="p1", epoch=1,
                         not_before=1.0, expires=100.0, evidence_expires=90.0))


def observed(root: Path) -> tuple[str, int]:
    with sqlite3.connect(root / "local.sqlite") as local:
        status = local.execute("SELECT status FROM custody_intents").fetchone()[0]
    with sqlite3.connect(root / "endpoint.sqlite") as endpoint:
        count = endpoint.execute("SELECT count(*) FROM custody_endpoint_effects").fetchone()[0]
    return status, count
