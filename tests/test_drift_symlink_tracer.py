"""RC-DRIFT-01: scope denials cannot become permission to invalidate receipts."""
import json

import pytest
from test_drift_symlink_support import replace_with_link, state
from test_lane_reopen import reopen_request
from test_reconcile_lane_support import event, fixture

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_drift import source_changed
from hmt_rnd.lane_evidence import digest_file


@pytest.mark.parametrize("source", ["artifact", "evidence"])
@pytest.mark.parametrize("dangling", [False, True])
def test_declared_symlink_drift_denies_atomically(tmp_path, source, dangling):
    host, owner, request, store, receipt = fixture(tmp_path)
    path = receipt.candidate.artifact if source == "artifact" else receipt.gate.evidence[0].path
    expected = (receipt.candidate.artifact_sha256 if source == "artifact"
                else receipt.gate.evidence[0].sha256)
    scoped = reopen_request(host, owner, request)
    replace_with_link(path, tmp_path, dangling)
    with pytest.raises(PermissionError, match="LANE_ARTIFACT_SCOPE"):
        digest_file(path, tmp_path)
    drift, drift_denial = None, None
    try:
        drift = source_changed(path, expected, tmp_path)
    except PermissionError as error:
        drift_denial = str(error)
    before = state(host)
    reopened, reopen_denial = None, None
    try:
        reopened = store.reopen(owner, scoped, event(), lambda: Clock(now=12.0))
    except PermissionError as error:
        reopen_denial = str(error)
    witness = {"source": source, "dangling": dangling, "drift": drift,
               "drift_denial": drift_denial, "reopen_denial": reopen_denial,
               "invalidated": None if reopened is None else list(reopened.invalidated_candidates),
               "before": before, "after": state(host)}
    (tmp_path / "drift_symlink_observed.json").write_text(json.dumps(witness))
    print(json.dumps(witness))
    assert drift_denial == reopen_denial == "LANE_ARTIFACT_SCOPE"
    assert state(host) == before
    host.revoke(owner.principal)
    with host.transaction() as db:
        assert all(row[0] == 1 for row in db.execute("SELECT revoked FROM host_grants"))
