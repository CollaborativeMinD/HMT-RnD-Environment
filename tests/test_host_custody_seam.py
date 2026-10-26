"""Cross-worker witness: one SQLite authority/custody fence and trusted clock."""
import sqlite3

import pytest

from hmt_rnd.custody_adapter import CustodyStore
from hmt_rnd.custody_endpoint import Endpoint
from hmt_rnd.custody_models import Intent
from hmt_rnd.host_admission import authorize_and_checkpoint
from hmt_rnd.host_models import Assignment, Clock, Grant, Identity, Request
from hmt_rnd.host_store import HostStore


def compose(tmp_path):
    host = HostStore.create(tmp_path / "domain.sqlite", "p1")
    identity = Identity(principal="alice", role="builder", lane="Build", stage="B3",
                        credential="cred1")
    host.assign(Assignment(task_id="task1", principal="alice", revision=1))
    operations = ("custody.stage", "custody.reserve", "custody.reconcile", "custody.inspect")
    for operation in operations:
        host.grant(Grant(**identity.model_dump(), task_id="task1", operation=operation,
                         root=str(tmp_path), destination="local", policy="p1", epoch=1,
                         not_before=1.0, expires=100.0, evidence_expires=90.0))
    now = [10.0]

    def authority(connection, operation, principal, effect_id):
        assert principal == identity.principal and effect_id == "effect1"
        request = Request(task_id="task1", revision=1, operation=operation,
                          root=str(tmp_path), destination="local")
        authorize_and_checkpoint(connection, identity, request, Clock(now=now[0]))

    key = b"fixture-only-endpoint-key-32bytes!"
    custody = CustodyStore(host.path, authority, {"endpoint1": key})
    endpoint = Endpoint(tmp_path / "endpoint.sqlite", "endpoint1", key,
                        lambda *args: None)
    intent = Intent(endpoint_id="endpoint1", principal="alice", effect_id="effect1",
                    payload_digest="a" * 64)
    return host, custody, endpoint, intent, now


def test_revoke_preserves_uncertainty_and_blocks_reconcile(tmp_path):
    host, custody, endpoint, intent, _ = compose(tmp_path)
    custody.stage(intent)
    reservation = custody.reserve("alice", "effect1")
    proof = endpoint.apply(reservation)
    host.revoke("alice")
    with pytest.raises(PermissionError, match="HOST_GRANT_DENIED"):
        custody.reconcile(proof)
    with sqlite3.connect(host.path) as connection:
        status = connection.execute("SELECT status FROM custody_intents").fetchone()[0]
        assert status == "OUTCOME_UNCERTAIN"
        assert connection.execute("SELECT last_clock FROM host_meta").fetchone()[0] == 10.0


def test_custody_checks_host_clock_in_same_transaction(tmp_path):
    host, custody, _, intent, now = compose(tmp_path)
    custody.stage(intent)
    now[0] = 9.0
    with pytest.raises(PermissionError, match="HOST_CLOCK_ROLLBACK"):
        custody.reserve("alice", "effect1")
    with sqlite3.connect(host.path) as connection:
        assert connection.execute("SELECT status FROM custody_intents").fetchone()[0] == "STAGED"
