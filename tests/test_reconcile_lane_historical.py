"""HMT-B07: historical invalidated failures cannot invalidate current repairs."""
import pytest
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate
from test_reconcile_lane_support import assert_counts, deny, event, fixture

from hmt_rnd.host_models import Clock


@pytest.mark.parametrize("reason", ["DENIED_REPAIR", "ARTIFACT_DRIFT"])
def test_resolved_history_cannot_reopen_again(tmp_path, reason):
    host, actor, request, store, first = fixture(tmp_path, deny)
    first.candidate.artifact.write_text("old changed artifact")
    scoped = reopen_request(host, actor, request)
    store.reopen(actor, scoped, event(reason=reason), lambda: Clock(now=11.0))
    fixed = store.submit(actor, request, make_candidate(tmp_path, "fixed", reopen="repair"),
                         lambda: Clock(now=12.0), execute_gate)
    with pytest.raises(PermissionError, match="LANE_REOPEN_NOT_CURRENT"):
        store.reopen(actor, scoped, event(name="again", reason=reason, successor="another"),
                     lambda: Clock(now=13.0))
    assert store.receipt("fixed") == fixed
    assert_counts(host, 1, 1)
