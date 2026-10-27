"""HMT-B07: discover all causes before selecting owner and authority."""
import pytest
from test_lane_reopen import reopen_request
from test_lane_tracer import make_candidate, setup_host
from test_reconcile_lane_support import assert_counts, deny, event, fixture

from hmt_rnd.host_models import Clock, Grant


def test_artifact_reason_cannot_bypass_policy_authority(tmp_path):
    host, actor, request, store, receipt = fixture(tmp_path)
    receipt.candidate.artifact.write_text("artifact changed")
    host.set_policy("policy-2")
    scoped = request.model_copy(update={"operation": "lane.reopen"})
    for role in ("builder", "human_architect"):
        current = actor.model_copy(update={"role": role})
        host.grant(Grant(**current.model_dump(), task_id=request.task_id,
                         operation="lane.reopen", root=request.root, destination="local",
                         policy="policy-2", epoch=2, not_before=1.0, expires=100.0,
                         evidence_expires=90.0))
        if role == "builder":
            with pytest.raises(PermissionError, match="LANE_POLICY_REOPEN_REQUIRES_ARCHITECT"):
                store.reopen(current, scoped, event(), lambda: Clock(now=11.0))
            assert_counts(host, 0, 0)
        else:
            result = store.reopen(current, scoped, event(), lambda: Clock(now=12.0))
            assert result.required_stage == "CMAD1"


def test_denial_reason_cannot_hide_earlier_artifact_drift(tmp_path):
    host, actor, request, store, first = fixture(tmp_path)
    _, downstream, later = setup_host(tmp_path, "CMAD2")
    store.submit(downstream, later, make_candidate(tmp_path, "second", "CMAD2", "first"),
                 lambda: Clock(now=11.0), deny)
    first.candidate.artifact.write_text("earlier drift")
    change = event(changed="second", reason="DENIED_REPAIR")
    with pytest.raises(PermissionError, match="LANE_STAGE_OR_OPERATION_DENIED"):
        store.reopen(downstream, reopen_request(host, downstream, later), change,
                     lambda: Clock(now=12.0))
    assert_counts(host, 0, 0)
    result = store.reopen(actor, reopen_request(host, actor, request), change,
                          lambda: Clock(now=13.0))
    assert result.required_stage == "CMAD1"
    assert set(result.invalidated_candidates) == {"first", "second"}
