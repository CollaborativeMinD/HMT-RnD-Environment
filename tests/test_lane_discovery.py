"""A downstream caller cannot hide an earlier changed authority owner."""
from pathlib import Path

import pytest
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_models import Reopen
from hmt_rnd.lane_store import LaneStore


def test_omitted_earlier_drift_still_routes_upstream(tmp_path: Path) -> None:
    host, owner, request = setup_host(tmp_path)
    store = LaneStore(host)
    first = make_candidate(tmp_path)
    store.submit(owner, request, first, lambda: Clock(now=10.0), execute_gate)
    _, downstream, later_request = setup_host(tmp_path, "CMAD2")
    second = make_candidate(tmp_path, "second", "CMAD2", "first")
    store.submit(downstream, later_request, second, lambda: Clock(now=11.0), execute_gate)
    first.artifact.write_bytes(b"earlier drift")
    second.artifact.write_bytes(b"declared later drift")
    event = Reopen(event_id="hidden-earlier", lineage_id="mission-1",
                   changed_candidates=("second",), successor_candidate_id="new-second",
                   reason="ARTIFACT_DRIFT", termination_condition="Reseal corrected artifact")
    scoped = reopen_request(host, downstream, later_request)
    with pytest.raises(PermissionError, match="LANE_STAGE_OR_OPERATION_DENIED"):
        store.reopen(downstream, scoped, event, lambda: Clock(now=12.0))
