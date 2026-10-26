"""Reject fabricated change claims and attempts to replace immutable candidates."""
from pathlib import Path

import pytest
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_models import Reopen
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("updates,reason", [
    ({"changed_candidates": ("first", "first")}, "LANE_DUPLICATE_CHANGE_REFERENCE"),
    ({"lineage_id": "another-mission"}, "LANE_REOPEN_LINEAGE_MISMATCH"),
    ({"reason": "POLICY_DRIFT"}, "LANE_REOPEN_WITHOUT_POLICY_CHANGE"),
    ({"reason": "DENIED_REPAIR"}, "LANE_REOPEN_WITHOUT_DENIAL"),
    ({"successor_candidate_id": "first"}, "LANE_SUCCESSOR_ALREADY_EXISTS"),
])
def test_invalid_reopen_cannot_change_history(tmp_path: Path, updates: dict, reason: str) -> None:
    host, identity, request = setup_host(tmp_path)
    store = LaneStore(host)
    first = store.submit(identity, request, make_candidate(tmp_path),
                         lambda: Clock(now=10.0), execute_gate)
    first.candidate.artifact.write_bytes(b"changed")
    event = Reopen(event_id="change", lineage_id="mission-1", changed_candidates=("first",),
                   successor_candidate_id="successor", reason="ARTIFACT_DRIFT",
                   termination_condition="New current target gate receipt")
    with pytest.raises(PermissionError, match=reason):
        store.reopen(identity, reopen_request(host, identity, request),
                     event.model_copy(update=updates), lambda: Clock(now=11.0))
    assert store.receipt("first") == first
    with host.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM lane_reopens").fetchone()[0] == 0


def test_unbound_successor_cannot_close_someone_elses_event(tmp_path: Path) -> None:
    host, identity, request = setup_host(tmp_path)
    with pytest.raises(PermissionError, match="LANE_SUCCESSOR_BINDING"):
        LaneStore(host).submit(identity, request,
                               make_candidate(tmp_path, "next", reopen="not-owned-event"),
                               lambda: Clock(now=10.0), execute_gate)
