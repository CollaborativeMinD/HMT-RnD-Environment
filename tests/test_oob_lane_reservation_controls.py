"""RC-LANE-05: each reserved identity dimension is necessary."""
import pytest
from test_lane_tracer import execute_gate, make_candidate, setup_host
from test_oob_lane_support import counts, reopened, seal_successor

from hmt_rnd.host_models import Clock


@pytest.mark.parametrize("updates", [
    {"reopen_id": None}, {"reopen_id": "other-event"},
    {"lineage_id": "other-lineage"}, {"stage": "CMAD2"},
])
def test_reserved_successor_requires_every_binding(tmp_path, updates):
    host, actor, request, store, opened = reopened(tmp_path)
    candidate = make_candidate(tmp_path, "fixed", reopen="repair").model_copy(update=updates)
    caller, scoped = actor, request
    if candidate.stage == "CMAD2":
        _, caller, scoped = setup_host(tmp_path, "CMAD2")
    before = counts(host)
    with pytest.raises(PermissionError, match="LANE_RESERVED_SUCCESSOR_BINDING"):
        store.submit(caller, scoped, candidate, lambda: Clock(now=12.0), execute_gate)
    assert counts(host) == before
    assert seal_successor(tmp_path, store, actor, request).gate.outcome == "SEALED"
