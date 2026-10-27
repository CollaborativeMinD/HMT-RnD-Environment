"""Declared drift cannot mask an invalid source in the current lineage."""
import json

import pytest
from test_drift_symlink_support import replace_with_link, state, two_stages
from test_lane_reopen import reopen_request
from test_reconcile_lane_support import event

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_evidence import digest_file


@pytest.mark.parametrize("dangling", [False, True])
@pytest.mark.parametrize("location", ["earlier_undeclared", "later_undeclared", "same_receipt"])
def test_discovery_never_hides_invalid_source(tmp_path, dangling, location):
    host, owner, request, store, first, _, _, second = two_stages(tmp_path)
    scoped = reopen_request(host, owner, request)
    if location == "earlier_undeclared":
        invalid = first.gate.evidence[0].path
        second.candidate.artifact.write_bytes(b"declared later drift")
        change = event(changed="second")
    else:
        first.candidate.artifact.write_bytes(b"declared earlier drift")
        invalid = (second if location == "later_undeclared" else first).gate.evidence[0].path
        change = event()
    replace_with_link(invalid, tmp_path, dangling)
    with pytest.raises(PermissionError, match="LANE_ARTIFACT_SCOPE"):
        digest_file(invalid, tmp_path)
    before, denial, result = state(host), None, None
    try:
        result = store.reopen(owner, scoped, change, lambda: Clock(now=12.0))
    except PermissionError as error:
        denial = str(error)
    witness = {"location": location, "dangling": dangling, "denial": denial,
               "invalidated": None if result is None else list(result.invalidated_candidates),
               "before": before, "after": state(host)}
    (tmp_path / "drift_symlink_observed.json").write_text(json.dumps(witness))
    print(json.dumps(witness))
    assert denial == "LANE_ARTIFACT_SCOPE" and state(host) == before
