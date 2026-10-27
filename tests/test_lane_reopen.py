"""Typed reopen invalidates descendants without mutating prior receipts."""
from pathlib import Path

import pytest
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock, Grant
from hmt_rnd.lane_models import Reopen
from hmt_rnd.lane_store import LaneStore


def reopen_request(host, identity, request):
    host.grant(Grant(**identity.model_dump(), task_id=request.task_id,
                     operation="lane.reopen", root=request.root, destination="local",
                     policy="policy-1", epoch=1, not_before=1.0, expires=100.0,
                     evidence_expires=90.0))
    return request.model_copy(update={"operation": "lane.reopen"})


def test_tamper_reopen_earliest_owner_and_reseal_descendants(tmp_path: Path) -> None:
    host, owner, first_request = setup_host(tmp_path)
    store = LaneStore(host)
    first = store.submit(owner, first_request, make_candidate(tmp_path),
                         lambda: Clock(now=10.0), execute_gate)
    _, second_owner, second_request = setup_host(tmp_path, "CMAD2")
    store.submit(second_owner, second_request,
                 make_candidate(tmp_path, "second", "CMAD2", "first"),
                 lambda: Clock(now=11.0), execute_gate)
    _, third_owner, third_request = setup_host(tmp_path, "CMAD3")
    first.candidate.artifact.write_bytes(b"tampered")
    with pytest.raises(PermissionError, match="LANE_ARTIFACT_DRIFT"):
        store.submit(third_owner, third_request,
                     make_candidate(tmp_path, "stale", "CMAD3", "second"),
                     lambda: Clock(now=12.0), execute_gate)
    event = Reopen(event_id="reopen-1", lineage_id="mission-1",
                   changed_candidates=("first",), successor_candidate_id="new-first",
                   reason="ARTIFACT_DRIFT", termination_condition="Reseal corrected artifact")
    result = store.reopen(owner, reopen_request(host, owner, first_request), event,
                          lambda: Clock(now=12.0))
    assert result.required_stage == "CMAD1"
    assert set(result.invalidated_candidates) == {"first", "second"}
    assert store.receipt("first") == first
    with pytest.raises(PermissionError, match="LANE_TYPED_SUCCESSOR_REQUIRED"):
        store.submit(owner, first_request, make_candidate(tmp_path, "untyped"),
                     lambda: Clock(now=13.0), execute_gate)
    store.submit(owner, first_request,
                 make_candidate(tmp_path, "new-first", reopen="reopen-1"),
                 lambda: Clock(now=13.0), execute_gate)
    following = store.submit(second_owner, second_request,
                             make_candidate(tmp_path, "new-second", "CMAD2", "new-first"),
                             lambda: Clock(now=14.0), execute_gate)
    assert following.gate.outcome == "SEALED"


def test_reopen_routes_to_earliest_changed_owner(tmp_path: Path) -> None:
    host, owner, request = setup_host(tmp_path)
    store = LaneStore(host)
    candidate = make_candidate(tmp_path)
    store.submit(owner, request, candidate, lambda: Clock(now=10.0), execute_gate)
    candidate.artifact.write_bytes(b"changed")
    _, downstream, down_request = setup_host(tmp_path, "CMAD2", "lane.reopen")
    event = Reopen(event_id="wrong-owner", lineage_id="mission-1",
                   changed_candidates=("first",), successor_candidate_id="successor",
                   reason="ARTIFACT_DRIFT", termination_condition="Reseal corrected artifact")
    with pytest.raises(PermissionError, match="LANE_STAGE_OR_OPERATION_DENIED"):
        store.reopen(downstream, down_request, event, lambda: Clock(now=11.0))
