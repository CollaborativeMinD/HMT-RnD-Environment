"""RC-ANCESTOR-01: the existing post-evaluator check repeats assignment validation."""
import pytest
from test_ancestor_freshness_support import chain
from test_lane_tracer import execute_gate
from test_revision_issuance_support import snapshot

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_submission import submit


@pytest.mark.parametrize("depth", [1, 2])
def test_same_transaction_assignment_change_is_detected_after_evaluator(tmp_path, depth):
    host, store, receipts, owner, request, candidate = chain(tmp_path, depth)
    before = snapshot(host)
    calls = []
    with pytest.raises(PermissionError, match="LANE_PREDECESSOR_ASSIGNMENT_STALE"):
        with host.transaction() as db:

            def changed_gate(context):
                calls.append(context)
                result = execute_gate(context)
                db.execute("UPDATE host_tasks SET revision=2 WHERE task_id='CMAD1'")
                return result

            submit(db, owner, request, candidate, lambda: Clock(now=11.0), changed_gate)
    assert len(calls) == 1
    assert snapshot(host) == before
    assert [store.receipt(item.candidate.candidate_id) for item in receipts] == receipts
