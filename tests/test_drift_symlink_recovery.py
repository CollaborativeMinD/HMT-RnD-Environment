"""Genuine missing-source drift still routes earliest-owner recovery after restart."""
import pytest
from test_drift_symlink_support import state, two_stages
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate
from test_reconcile_lane_support import event

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("source", ["artifact", "evidence"])
def test_genuine_missing_source_keeps_earliest_owner_recovery(tmp_path, source):
    host, owner, request, store, first, downstream, later, second = two_stages(tmp_path)
    path = first.candidate.artifact if source == "artifact" else first.gate.evidence[0].path
    saved = store.snapshot(first.candidate.artifact_sha256)
    path.unlink()
    second.candidate.artifact.write_bytes(b"declared later change")
    change = event(changed="second")
    late_scope = reopen_request(host, downstream, later)
    before = state(host)
    with pytest.raises(PermissionError, match="LANE_STAGE_OR_OPERATION_DENIED"):
        store.reopen(downstream, late_scope, change, lambda: Clock(now=12.0))
    assert state(host) == before
    scoped = reopen_request(host, owner, request)
    reopened = store.reopen(owner, scoped, change, lambda: Clock(now=13.0))
    assert reopened.required_stage == "CMAD1"
    assert set(reopened.invalidated_candidates) == {"first", "second"}
    restarted = LaneStore(host)
    fixed = restarted.submit(owner, request, make_candidate(tmp_path, "fixed", reopen="repair"),
                             lambda: Clock(now=14.0), execute_gate)
    assert fixed.gate.outcome == "SEALED"
    assert restarted.receipt("first") == first
    assert restarted.snapshot(first.candidate.artifact_sha256) == saved
    final = restarted.submit(downstream, later,
                             make_candidate(tmp_path, "second-fixed", "CMAD2", "fixed"),
                             lambda: Clock(now=15.0), execute_gate)
    assert final.gate.outcome == "SEALED"
