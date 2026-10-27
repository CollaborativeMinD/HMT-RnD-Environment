"""Independent negative controls for repaired reopening authority boundaries."""
import pytest
from test_lane_tracer import execute_gate, make_candidate, setup_host
from test_reconcile_lane_support import assert_counts, event, fixture

from hmt_rnd.host_models import Assignment, Clock, Grant
from hmt_rnd.lane_successor import has_reopen_ancestor


def test_current_stage_requires_reopen_not_duplicate_candidate(tmp_path):
    host, actor, request, store, first = fixture(tmp_path)
    with pytest.raises(PermissionError, match="LANE_TYPED_REOPEN_REQUIRED"):
        store.submit(actor, request, make_candidate(tmp_path, "duplicate"),
                     lambda: Clock(now=11.0), execute_gate)
    assert store.receipt("first") == first
    assert_counts(host, 0, 0)


def test_matching_stage_with_wrong_lane_cannot_seal(tmp_path):
    host, actor, request, store, first = fixture(tmp_path)
    with pytest.raises(PermissionError, match="LANE_OWNER_DENIED"):
        store.submit(actor.model_copy(update={"lane": "MR"}), request,
                     make_candidate(tmp_path, "wrong-lane"), lambda: Clock(now=11.0), execute_gate)
    assert_counts(host, 0, 0)


def test_current_grant_for_another_task_cannot_reopen(tmp_path):
    host, actor, request, store, first = fixture(tmp_path)
    first.candidate.artifact.write_text("drift")
    host.assign(Assignment(task_id="another", principal=actor.principal, revision=1))
    host.grant(Grant(**actor.model_dump(), task_id="another", operation="lane.reopen",
                     root=request.root, destination="local", policy="policy-1", epoch=1,
                     not_before=1.0, expires=100.0, evidence_expires=90.0))
    scoped = request.model_copy(update={"task_id": "another", "operation": "lane.reopen"})
    with pytest.raises(PermissionError, match="LANE_REOPEN_TASK_MISMATCH"):
        store.reopen(actor, scoped, event(), lambda: Clock(now=11.0))
    assert_counts(host, 0, 0)


def test_unreopened_ancestry_confers_no_repair_authority(tmp_path):
    host, actor, request, store, first = fixture(tmp_path)
    _, downstream, later = setup_host(tmp_path, "CMAD2")
    store.submit(downstream, later, make_candidate(tmp_path, "second", "CMAD2", "first"),
                 lambda: Clock(now=11.0), execute_gate)
    with host.transaction() as db:
        assert has_reopen_ancestor(db, "second") is False
        assert has_reopen_ancestor(db, None) is False
