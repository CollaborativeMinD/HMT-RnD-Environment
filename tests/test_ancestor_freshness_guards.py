"""RC-ANCESTOR-01: every ancestor needs its recorded current host assignment."""
import pytest
from test_ancestor_freshness_support import chain, drift
from test_lane_tracer import execute_gate
from test_revision_issuance_support import snapshot

from hmt_rnd.host_models import Assignment, Clock
from hmt_rnd.host_store import HostStore
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("depth", [1, 2])
@pytest.mark.parametrize("change", ["revision", "reassigned", "missing", "principal-only"])
@pytest.mark.parametrize("restart", [False, True])
def test_stale_assignment_blocks_before_evaluator(tmp_path, depth, change, restart):
    host, store, receipts, owner, request, candidate = chain(tmp_path, depth)
    drift(host, "CMAD1", change)
    if restart:
        store = LaneStore(HostStore(host.path))
    before = snapshot(host)
    calls = []

    def observed_gate(context):
        calls.append(context)
        return execute_gate(context)

    with pytest.raises(PermissionError, match="LANE_PREDECESSOR_ASSIGNMENT_STALE"):
        store.submit(owner, request, candidate, lambda: Clock(now=11.0), observed_gate)
    assert calls == []
    assert snapshot(host) == before
    restarted = LaneStore(HostStore(host.path))
    assert snapshot(restarted.host) == before
    assert [restarted.receipt(item.candidate.candidate_id) for item in receipts] == receipts


@pytest.mark.parametrize("depth", [1, 2])
@pytest.mark.parametrize("unrelated", [False, True])
def test_unchanged_ancestry_and_unrelated_assignment_allow_progress(tmp_path, depth, unrelated):
    host, store, receipts, owner, request, candidate = chain(tmp_path, depth)
    if unrelated:
        host.assign(Assignment(task_id="unrelated", principal="alice", revision=1))
        host.assign(Assignment(task_id="unrelated", principal="bob", revision=2))
    restarted = LaneStore(HostStore(host.path))
    result = restarted.submit(owner, request, candidate, lambda: Clock(now=11.0), execute_gate)
    assert result.gate.outcome == "SEALED"
    assert result.gate.predecessor_sha256 == receipts[-1].receipt_sha256
    assert [restarted.receipt(item.candidate.candidate_id) for item in receipts] == receipts
