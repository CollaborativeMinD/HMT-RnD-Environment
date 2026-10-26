"""Closed handoff, exact ordering, and evaluator-only role ceilings."""
from pathlib import Path

import pytest
from pydantic import ValidationError
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_handoff import Handoff
from hmt_rnd.lane_models import Reopen
from hmt_rnd.lane_stages import STAGES, lane, predecessor
from hmt_rnd.lane_store import LaneStore


def test_eight_lanes_twenty_six_stages_and_closed_handoff() -> None:
    assert len(STAGES) == 26
    assert {lane(stage) for stage in STAGES} == {
        "CMAD", "PMCT", "DOKE", "MR", "CSSI", "IIEA", "Build", "OPS"}
    assert predecessor("B1") == "IIEA3"
    assert predecessor("OPS1") == "B5"
    body = dict(agent_role="builder", task_owned="task", implementation="candidate",
                risks=[], assumptions=[], follow_up_instructions=[], validation_status="hold",
                artifact_refs=[], provenance_id="case")
    assert Handoff.model_validate({"response": body}).response.validation_status == "hold"
    with pytest.raises(ValidationError):
        Handoff.model_validate({"response": {**body, "admission": "PASS"}})
    with pytest.raises(ValidationError):
        Handoff.model_validate({"response": body, "override": True})


@pytest.mark.parametrize("role", ["rrca", "RRCA", "mission_assurance", "MissionAssurance"])
def test_evidence_roles_cannot_progress(tmp_path: Path, role: str) -> None:
    host, identity, request = setup_host(tmp_path)
    with pytest.raises(PermissionError, match="LANE_EVALUATOR_ROLE_CANNOT_PROGRESS"):
        LaneStore(host).submit(identity.model_copy(update={"role": role}), request,
                               make_candidate(tmp_path), lambda: Clock(now=10.0), execute_gate)


def test_stage_skip_and_unsubstantiated_reopen_fail(tmp_path: Path) -> None:
    host, identity, request = setup_host(tmp_path)
    store = LaneStore(host)
    store.submit(identity, request, make_candidate(tmp_path), lambda: Clock(now=10.0), execute_gate)
    _, later, later_request = setup_host(tmp_path, "CMAD3")
    with pytest.raises(PermissionError, match="LANE_PREDECESSOR_ORDER"):
        store.submit(later, later_request, make_candidate(tmp_path, "skip", "CMAD3", "first"),
                     lambda: Clock(now=11.0), execute_gate)
    event = Reopen(event_id="no-change", lineage_id="mission-1", changed_candidates=("first",),
                   successor_candidate_id="next", reason="ARTIFACT_DRIFT",
                   termination_condition="Reseal corrected artifact")
    with pytest.raises(PermissionError, match="LANE_REOPEN_WITHOUT_ARTIFACT_CHANGE"):
        store.reopen(identity, reopen_request(host, identity, request), event,
                     lambda: Clock(now=11.0))
