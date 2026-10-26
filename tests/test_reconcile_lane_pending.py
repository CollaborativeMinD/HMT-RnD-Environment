"""HMT-B07: a pending stage repair requires its exact designated successor."""
import pytest
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate, setup_host
from test_reconcile_lane_support import event, fixture

from hmt_rnd.host_models import Clock


def test_old_closed_ancestor_cannot_bypass_new_pending_reopen(tmp_path):
    host, actor, request, store, first = fixture(tmp_path)
    _, downstream, later = setup_host(tmp_path, "CMAD2")
    store.submit(downstream, later, make_candidate(tmp_path, "second", "CMAD2", "first"),
                 lambda: Clock(now=11.0), execute_gate)
    first.candidate.artifact.write_text("first changed")
    store.reopen(actor, reopen_request(host, actor, request), event(), lambda: Clock(now=12.0))
    store.submit(actor, request, make_candidate(tmp_path, "fixed", reopen="repair"),
                 lambda: Clock(now=13.0), execute_gate)
    second = store.submit(downstream, later,
                           make_candidate(tmp_path, "second-fixed", "CMAD2", "fixed"),
                           lambda: Clock(now=14.0), execute_gate)
    second.candidate.artifact.write_text("second changed")
    change = event(name="second-repair", changed="second-fixed", successor="second-final")
    store.reopen(downstream, reopen_request(host, downstream, later), change,
                 lambda: Clock(now=15.0))
    with pytest.raises(PermissionError, match="LANE_TYPED_SUCCESSOR_REQUIRED"):
        store.submit(downstream, later, make_candidate(tmp_path, "intruder", "CMAD2", "fixed"),
                     lambda: Clock(now=16.0), execute_gate)
    result = store.submit(downstream, later,
                           make_candidate(tmp_path, "second-final", "CMAD2", "fixed",
                                          "second-repair"),
                           lambda: Clock(now=17.0), execute_gate)
    assert result.gate.outcome == "SEALED"
