"""RC-LANE-07: unsupported cross-revision events must never be issued."""
import pytest
from test_oob_lane_support import current_grant, seal_successor
from test_reconcile_lane_support import event
from test_revision_issuance_support import advance, changed_origin, snapshot

from hmt_rnd.host_models import Assignment, Clock
from hmt_rnd.host_store import HostStore
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("restart", [False, True])
def test_fresh_revision_cannot_invalidate_previous_revision_origin(tmp_path, restart):
    host, actor, request, store, origin = changed_origin(tmp_path)
    revised = advance(host, actor, request)
    if restart:
        store = LaneStore(HostStore(host.path))
    before = snapshot(host)
    with pytest.raises(PermissionError, match="LANE_REOPEN_REVISION_MISMATCH"):
        store.reopen(actor, revised, event(), lambda: Clock(now=11.0))
    assert snapshot(host) == before
    restarted = LaneStore(HostStore(host.path))
    assert snapshot(restarted.host) == before
    assert restarted.receipt("first") == origin


@pytest.mark.parametrize("restart", [False, True])
def test_unchanged_revision_event_remains_usable_after_restart(tmp_path, restart):
    host, actor, request, store, origin = changed_origin(tmp_path)
    if restart:
        store = LaneStore(HostStore(host.path))
    scoped = request.model_copy(update={"operation": "lane.reopen"})
    opened = store.reopen(actor, scoped, event(), lambda: Clock(now=11.0))
    assert opened.task_revision == origin.task_revision == 1
    restarted = LaneStore(HostStore(host.path))
    sealed = seal_successor(tmp_path, restarted, actor, request)
    assert sealed.gate.outcome == "SEALED"
    assert restarted.receipt("first") == origin
    assert snapshot(host)["lane_closures"][0][0] == "repair"


@pytest.mark.parametrize("condition,reason", [
    ("other-task", "LANE_REOPEN_TASK_MISMATCH"),
    ("stale-grant", "HOST_TASK_REVISION_DENIED"),
    ("revoked", "HOST_GRANT_DENIED"),
])
def test_origin_and_current_authority_controls(tmp_path, condition, reason):
    host, actor, request, store, origin = changed_origin(tmp_path)
    scoped = request.model_copy(update={"operation": "lane.reopen"})
    if condition == "other-task":
        host.assign(Assignment(task_id="other", principal=actor.principal, revision=1))
        scoped = request.model_copy(update={"task_id": "other"})
        scoped = current_grant(host, actor, scoped, "policy-1", 1, "lane.reopen")
    elif condition == "stale-grant":
        host.assign(Assignment(task_id=request.task_id, principal=actor.principal, revision=2))
        scoped = scoped.model_copy(update={"revision": 2})
    else:
        host.revoke(actor.principal)
    before = snapshot(host)
    with pytest.raises(PermissionError, match=reason):
        store.reopen(actor, scoped, event(), lambda: Clock(now=11.0))
    assert snapshot(host) == before
