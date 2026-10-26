"""RC-LANE-06: legacy bodies and temporal authority must fail closed."""
import json

import pytest
from test_lane_tracer import execute_gate, make_candidate
from test_oob_lane_support import counts, current_grant, reopened

from hmt_rnd.host_models import Clock


def test_legacy_event_requires_explicit_migration_not_assumed_authority(tmp_path):
    host, actor, request, store, opened = reopened(tmp_path)
    body = opened.model_dump(mode="json")
    for key in ("policy", "epoch", "task_id", "task_revision"):
        del body[key]
    body["request"].update(event_id="legacy", lineage_id="legacy-lineage",
                           successor_candidate_id="legacy-fixed")
    with host.transaction() as db:
        db.execute("INSERT INTO lane_reopens VALUES(?,?,?,?,?)",
                   ("legacy", "legacy-lineage", "CMAD1", "legacy-fixed", json.dumps(body)))
    candidate = make_candidate(tmp_path, "legacy-fixed", reopen="legacy").model_copy(
        update={"lineage_id": "legacy-lineage"})
    before = counts(host)
    with pytest.raises(PermissionError, match="LANE_REOPEN_BINDING_MISSING"):
        store.submit(actor, request, candidate, lambda: Clock(now=12.0), execute_gate)
    architect = actor.model_copy(update={"role": "human_architect"})
    scoped = current_grant(host, architect, request, "policy-1", 1, "lane.reauthorize")
    with pytest.raises(PermissionError, match="LANE_REOPEN_BINDING_MISSING"):
        store.reauthorize(architect, scoped, "legacy", lambda: Clock(now=13.0))
    assert counts(host) == before
    with host.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM lane_reauthorizations").fetchone()[0] == 0


@pytest.mark.parametrize("fresh_grant", [False, True])
def test_reauthorization_needs_current_unexpired_grant_at_both_checks(tmp_path, fresh_grant):
    host, actor, request, store, opened = reopened(tmp_path)
    architect = actor.model_copy(update={"role": "human_architect"})
    scoped = current_grant(host, architect, request, "policy-1", 1, "lane.reauthorize")
    host.set_policy("policy-2")
    if fresh_grant:
        current_grant(host, architect, request, "policy-2", 2, "lane.reauthorize")
    ticks = iter([Clock(now=12.0), Clock(now=100.0)])
    before = counts(host)
    with pytest.raises(PermissionError):
        store.reauthorize(architect, scoped, "repair", lambda: next(ticks))
    assert counts(host) == before
    with host.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM lane_reauthorizations").fetchone()[0] == 0
