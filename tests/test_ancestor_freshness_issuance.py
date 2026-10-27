"""RC-ANCESTOR-01 coupling: do not issue unusable downstream reopen events."""
import pytest
from test_ancestor_freshness_issuance_support import prepare, successor
from test_ancestor_freshness_support import drift
from test_revision_issuance_support import snapshot

from hmt_rnd.host_models import Assignment, Clock
from hmt_rnd.host_store import HostStore
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("depth", [1, 2])
@pytest.mark.parametrize("change", ["revision", "reassigned", "missing", "principal-only"])
@pytest.mark.parametrize("restart", [False, True])
def test_reopen_denies_before_mutation_when_ancestor_assignment_is_stale(
        tmp_path, depth, change, restart):
    host, store, ancestors, owner, request, scoped, change_event, origin = prepare(tmp_path, depth)
    drift(host, "CMAD1", change)
    if restart:
        store = LaneStore(HostStore(host.path))
    before = snapshot(host)
    with pytest.raises(PermissionError, match="LANE_PREDECESSOR_ASSIGNMENT_STALE"):
        store.reopen(owner, scoped, change_event, lambda: Clock(now=12.0))
    assert snapshot(host) == before
    restarted = LaneStore(HostStore(host.path))
    assert snapshot(restarted.host) == before
    assert restarted.receipt(origin.candidate.candidate_id) == origin
    assert [restarted.receipt(x.candidate.candidate_id) for x in ancestors] == ancestors


@pytest.mark.parametrize("depth", [1, 2])
@pytest.mark.parametrize("unrelated", [False, True])
def test_unchanged_ancestor_allows_reopening_and_persisted_successor(tmp_path, depth, unrelated):
    host, store, ancestors, owner, request, scoped, change_event, origin = prepare(tmp_path, depth)
    if unrelated:
        host.assign(Assignment(task_id="unrelated", principal="alice", revision=1))
        host.assign(Assignment(task_id="unrelated", principal="bob", revision=2))
    restarted = LaneStore(HostStore(host.path))
    opened = restarted.reopen(owner, scoped, change_event, lambda: Clock(now=12.0))
    assert opened.required_stage == origin.candidate.stage
    assert opened.invalidated_candidates == (origin.candidate.candidate_id,)
    restarted = LaneStore(HostStore(host.path))
    assert successor(tmp_path, restarted, owner, request, origin).gate.outcome == "SEALED"
    assert restarted.receipt(origin.candidate.candidate_id) == origin
    assert [restarted.receipt(x.candidate.candidate_id) for x in ancestors] == ancestors
