"""RC-LANE-06: explicit architect recovery preserves history and exact binding."""
import hashlib
import sqlite3

import pytest
from test_oob_lane_support import current_grant, reopened, seal_successor

from hmt_rnd.host_models import Clock
from hmt_rnd.host_store import HostStore
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("policy", ["policy-2", "policy-1"])
def test_architect_reauthorizes_exact_event_and_survives_restart(tmp_path, policy):
    host, actor, request, store, opened = reopened(tmp_path)
    with host.transaction() as db:
        original = db.execute("SELECT body FROM lane_reopens WHERE id='repair'").fetchone()[0]
    host.set_policy(policy)
    current_grant(host, actor, request, policy, 2, "lane.seal")
    architect = actor.model_copy(update={"role": "human_architect"})
    scoped = current_grant(host, architect, request, policy, 2, "lane.reauthorize")
    approval = store.reauthorize(architect, scoped, "repair", lambda: Clock(now=12.0))
    assert approval.event_sha256 == hashlib.sha256(original.encode()).hexdigest()
    assert approval.origin_receipt_sha256 == opened.origin_receipt_sha256
    assert (approval.policy, approval.epoch) == (policy, 2)
    assert approval == store.reauthorize(architect, scoped, "repair", lambda: Clock(now=13.0))
    with host.transaction() as db:
        body = db.execute("SELECT body FROM lane_reopens WHERE id='repair'").fetchone()[0]
        assert body == original
        with pytest.raises(sqlite3.IntegrityError, match="IMMUTABLE_LIFECYCLE"):
            db.execute("UPDATE lane_reauthorizations SET body='changed'")
    restarted = LaneStore(HostStore(host.path))
    assert seal_successor(tmp_path, restarted, actor, request).gate.policy == policy
    with pytest.raises(PermissionError, match="LANE_REAUTHORIZATION_CLOSED"):
        restarted.reauthorize(architect, scoped, "repair", lambda: Clock(now=16.0))


def test_approval_expires_on_next_epoch_even_with_fresh_grants(tmp_path):
    host, actor, request, store, opened = reopened(tmp_path)
    host.set_policy("policy-2")
    architect = actor.model_copy(update={"role": "human_architect"})
    scoped = current_grant(host, architect, request, "policy-2", 2, "lane.reauthorize")
    store.reauthorize(architect, scoped, "repair", lambda: Clock(now=12.0))
    host.set_policy("policy-2")
    current_grant(host, actor, request, "policy-2", 3, "lane.seal")
    with pytest.raises(PermissionError, match="LANE_REOPEN_AUTHORITY_STALE"):
        seal_successor(tmp_path, store, actor, request)
    current_grant(host, architect, request, "policy-2", 3, "lane.reauthorize")
    store.reauthorize(architect, scoped, "repair", lambda: Clock(now=16.0))
    assert seal_successor(tmp_path, store, actor, request, now=17.0).gate.epoch == 3
