"""RC-LANE-06: one architecture decision cannot stand in for another event."""
import json

import pytest
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate
from test_oob_lane_support import counts, current_grant, reopened
from test_reconcile_lane_support import event

from hmt_rnd.host_models import Clock


def test_exact_event_approval_cannot_authorize_another_event(tmp_path):
    host, actor, request, store, opened = reopened(tmp_path)
    other = make_candidate(tmp_path, "other").model_copy(update={"lineage_id": "mission-B"})
    store.submit(actor, request, other, lambda: Clock(now=12.0), execute_gate)
    other.artifact.write_text("changed B")
    repair = event(name="other-repair", changed="other", successor="other-fixed").model_copy(
        update={"lineage_id": "mission-B"})
    store.reopen(actor, reopen_request(host, actor, request), repair, lambda: Clock(now=13.0))
    host.set_policy("policy-2")
    current_grant(host, actor, request, "policy-2", 2, "lane.seal")
    architect = actor.model_copy(update={"role": "human_architect"})
    scoped = current_grant(host, architect, request, "policy-2", 2, "lane.reauthorize")
    approval = store.reauthorize(architect, scoped, "repair", lambda: Clock(now=14.0))
    successor = make_candidate(tmp_path, "other-fixed", reopen="other-repair").model_copy(
        update={"lineage_id": "mission-B"})
    before = counts(host)
    with pytest.raises(PermissionError, match="LANE_REOPEN_AUTHORITY_STALE"):
        store.submit(actor, request, successor, lambda: Clock(now=15.0), execute_gate)
    assert counts(host) == before
    # Corrupt-store control: a misplaced approval still cannot satisfy exact event identity.
    with host.transaction() as db:
        db.execute("INSERT INTO lane_reauthorizations VALUES(?,?,?,?)",
                   ("other-repair", "policy-2", 2, approval.model_dump_json()))
    with pytest.raises(PermissionError, match="LANE_REAUTHORIZATION_BINDING"):
        store.submit(actor, request, successor, lambda: Clock(now=16.0), execute_gate)
    with pytest.raises(PermissionError, match="LANE_REAUTHORIZATION_BINDING"):
        store.reauthorize(architect, scoped, "other-repair", lambda: Clock(now=17.0))
    assert counts(host) == before


@pytest.mark.parametrize("change,reason", [
    ({"task_id": "other"}, "LANE_REOPEN_TASK_BINDING"),
    ({"origin_receipt_sha256": "0" * 64}, "LANE_REOPEN_ORIGIN_MISSING"),
    ({"required_stage": "CMAD2"}, "LANE_REOPEN_BINDING_MISMATCH"),
])
def test_corrupt_event_binding_cannot_gain_reauthorization(tmp_path, change, reason):
    host, actor, request, store, opened = reopened(tmp_path)
    body = opened.model_dump(mode="json")
    body.update(change)
    body["request"].update(event_id="corrupt", successor_candidate_id="corrupt-fixed")
    with host.transaction() as db:
        db.execute("INSERT INTO lane_reopens VALUES(?,?,?,?,?)",
                   ("corrupt", "mission-1", "CMAD1", "corrupt-fixed", json.dumps(body)))
    architect = actor.model_copy(update={"role": "human_architect"})
    scoped = current_grant(host, architect, request, "policy-1", 1, "lane.reauthorize")
    before = counts(host)
    with pytest.raises(PermissionError, match=reason):
        store.reauthorize(architect, scoped, "corrupt", lambda: Clock(now=12.0))
    assert counts(host) == before
