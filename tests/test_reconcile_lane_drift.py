"""HMT-B07: evidence-only and missing-source repair must be reachable."""
import pytest
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate, setup_host
from test_reconcile_lane_support import assert_counts, event, fixture

from hmt_rnd.host_models import Clock


@pytest.mark.parametrize("source,missing", [("evidence", False), ("evidence", True),
                                          ("artifact", True)])
def test_drift_repair_reachable(tmp_path, source, missing):
    host, actor, request, store, receipt = fixture(tmp_path)
    path = receipt.gate.evidence[0].path if source == "evidence" else receipt.candidate.artifact
    original = store.snapshot(receipt.gate.evidence[0].sha256)
    if missing:
        path.unlink()
    else:
        path.write_text("changed evidence")
    result = store.reopen(actor, reopen_request(host, actor, request), event(),
                          lambda: Clock(now=11.0))
    assert result.required_stage == "CMAD1"
    assert store.receipt("first") == receipt
    assert store.snapshot(receipt.gate.evidence[0].sha256) == original
    successor = store.submit(actor, request, make_candidate(tmp_path, "fixed", reopen="repair"),
                              lambda: Clock(now=12.0), execute_gate)
    assert successor.gate.outcome == "SEALED"


def test_discovery_includes_earlier_evidence(tmp_path):
    host, actor, request, store, first = fixture(tmp_path)
    _, downstream, later = setup_host(tmp_path, "CMAD2")
    second = make_candidate(tmp_path, "second", "CMAD2", "first")
    store.submit(downstream, later, second, lambda: Clock(now=11.0), execute_gate)
    first.gate.evidence[0].path.write_text("earlier drift")
    second.artifact.write_text("declared drift")
    with pytest.raises(PermissionError, match="LANE_STAGE_OR_OPERATION_DENIED"):
        store.reopen(downstream, reopen_request(host, downstream, later),
                     event(changed="second"), lambda: Clock(now=12.0))
    assert_counts(host, 0, 0)


def test_outside_symlink_is_not_missing_source_repair(tmp_path):
    host, actor, request, store, receipt = fixture(tmp_path)
    path = receipt.candidate.artifact
    path.unlink()
    path.symlink_to(tmp_path.parent / "outside-missing")
    with pytest.raises(PermissionError, match="LANE_ARTIFACT_SCOPE"):
        store.reopen(actor, reopen_request(host, actor, request), event(),
                     lambda: Clock(now=11.0))
    assert_counts(host, 0, 0)
