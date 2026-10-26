"""Tracer: one authority store admits assignment, then revoke survives restart."""
from pathlib import Path

import pytest

from hmt_rnd.host_admission import admit
from hmt_rnd.host_models import Assignment, Clock, Grant, Identity, Request
from hmt_rnd.host_store import HostStore


def fixture_store(path: Path) -> tuple[HostStore, Identity, Request]:
    store = HostStore.create(path, "policy-1")
    identity = Identity(principal="alice", role="builder", lane="Build", stage="B3",
                        credential="local-build")
    request = Request(task_id="task-1", revision=1, operation="inspect",
                      root=str(path.parent), destination="local")
    store.assign(Assignment(task_id="task-1", principal="alice", revision=1))
    store.grant(Grant(principal="alice", role="builder", lane="Build", stage="B3",
                      credential="local-build", task_id="task-1", operation="inspect",
                      root=str(path.parent), destination="local", policy="policy-1",
                      epoch=1, not_before=1.0, expires=100.0, evidence_expires=90.0))
    return store, identity, request


def test_assign_admit_revoke_restart(tmp_path: Path) -> None:
    store, identity, request = fixture_store(tmp_path / "authority.sqlite")
    decision = admit(store, identity, request, Clock(now=10.0))
    assert decision.task_revision == 1
    assert decision.effect_authority == "NONE"
    store.revoke("alice")
    restarted = HostStore(store.path)
    with pytest.raises(PermissionError, match="HOST_GRANT_DENIED"):
        admit(restarted, identity, request, Clock(now=11.0))
