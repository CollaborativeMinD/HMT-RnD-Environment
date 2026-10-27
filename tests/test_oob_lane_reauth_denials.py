"""RC-LANE-06: role text is insufficient; all host authority dimensions apply."""
import pytest
from test_oob_lane_support import counts, current_grant, reopened

from hmt_rnd.host_models import Assignment, Clock


@pytest.mark.parametrize("change,reason", [
    ("builder", "LANE_REAUTHORIZATION_REQUIRES_ARCHITECT"),
    ("ungranted-role", "HOST_IDENTITY_SCOPE_DENIED"),
    ("wrong-stage", "LANE_STAGE_OR_OPERATION_DENIED"),
    ("wrong-operation", "LANE_STAGE_OR_OPERATION_DENIED"),
    ("wrong-task", "LANE_REOPEN_TASK_BINDING"),
    ("wrong-revision", "LANE_REOPEN_TASK_BINDING"),
    ("revoked", "HOST_GRANT_DENIED"),
    ("unknown-event", "LANE_REOPEN_UNKNOWN"),
])
def test_reauthorization_requires_exact_current_host_authority(tmp_path, change, reason):
    host, actor, request, store, opened = reopened(tmp_path)
    host.set_policy("policy-2")
    architect = actor.model_copy(update={"role": "human_architect"})
    if change == "builder":
        architect = actor
    if change == "wrong-stage":
        architect = architect.model_copy(update={"stage": "CMAD2"})
    if change == "wrong-task":
        request = request.model_copy(update={"task_id": "other"})
        host.assign(Assignment(task_id="other", principal=actor.principal, revision=1))
    if change == "wrong-revision":
        request = request.model_copy(update={"revision": 2})
        host.assign(Assignment(task_id=request.task_id, principal=actor.principal, revision=2))
    operation = "lane.seal" if change == "wrong-operation" else "lane.reauthorize"
    grant_actor = actor if change == "ungranted-role" else architect
    scoped = current_grant(host, grant_actor, request, "policy-2", 2, operation)
    if change == "revoked":
        host.revoke(actor.principal)
    before = counts(host)
    with pytest.raises(PermissionError, match=reason):
        store.reauthorize(architect, scoped, "absent" if change == "unknown-event" else "repair",
                          lambda: Clock(now=12.0))
    assert counts(host) == before
    with host.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM lane_reauthorizations").fetchone()[0] == 0
