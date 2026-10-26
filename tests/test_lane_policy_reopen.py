"""Current policy changes require the real changed owner and architecture role."""
from pathlib import Path

import pytest
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock, Grant
from hmt_rnd.lane_models import GateContext, GateResult, Reopen
from hmt_rnd.lane_store import LaneStore


def test_policy_reopen_requires_architect_and_current_policy(tmp_path: Path) -> None:
    host, identity, request = setup_host(tmp_path)
    store = LaneStore(host)
    store.submit(identity, request, make_candidate(tmp_path), lambda: Clock(now=10.0), execute_gate)
    host.set_policy("policy-2")
    request = request.model_copy(update={"operation": "lane.reopen"})
    event = Reopen(event_id="policy-change", lineage_id="mission-1",
                   changed_candidates=("first",), successor_candidate_id="new-first",
                   reason="POLICY_DRIFT", termination_condition="Current policy gate receipt")
    for role, expected in [("builder", "DENIED"), ("human_architect", "ADMITTED")]:
        actor = identity.model_copy(update={"role": role})
        host.grant(Grant(**actor.model_dump(), task_id=request.task_id,
                         operation=request.operation, root=request.root, destination="local",
                         policy="policy-2", epoch=2, not_before=1.0, expires=100.0,
                         evidence_expires=90.0))
        if expected == "DENIED":
            with pytest.raises(PermissionError, match="LANE_POLICY_REOPEN_REQUIRES_ARCHITECT"):
                store.reopen(actor, request, event, lambda: Clock(now=11.0))
        else:
            result = store.reopen(actor, request, event, lambda: Clock(now=12.0))
            assert result.required_stage == "CMAD1"


def test_denied_repair_has_a_terminal_successor(tmp_path: Path) -> None:
    from test_lane_reopen import reopen_request
    host, identity, request = setup_host(tmp_path)
    store = LaneStore(host)

    def denied(context: GateContext) -> GateResult:
        return execute_gate(context).model_copy(update={"outcome": "DENIED",
                                                        "reasons": ("ACTUAL_GATE_DENIAL",)})

    first = store.submit(identity, request, make_candidate(tmp_path),
                         lambda: Clock(now=10.0), denied)
    event = Reopen(event_id="repair-denial", lineage_id="mission-1",
                   changed_candidates=("first",), successor_candidate_id="fixed",
                   reason="DENIED_REPAIR", termination_condition="New target gate receipt")
    result = store.reopen(identity, reopen_request(host, identity, request), event,
                          lambda: Clock(now=11.0))
    assert result.origin_receipt_sha256 == first.receipt_sha256
    successor = make_candidate(tmp_path, "fixed", reopen=event.event_id)
    fixed = store.submit(identity, request, successor,
                         lambda: Clock(now=12.0), execute_gate)
    assert fixed.gate.outcome == "SEALED"
