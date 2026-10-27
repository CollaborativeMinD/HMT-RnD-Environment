"""RC-LANE-06: current builder grants cannot revive stale event authority."""
import pytest
from test_oob_lane_support import counts, current_grant, reopened, seal_successor

from hmt_rnd.host_store import HostStore
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("policy", ["policy-2", "policy-1"])
@pytest.mark.parametrize("restart", [False, True])
def test_event_drift_denied_with_fresh_builder_grant(tmp_path, policy, restart):
    host, actor, request, store, opened = reopened(tmp_path)
    host.set_policy(policy)
    current_grant(host, actor, request, policy, 2, "lane.seal")
    if restart:
        store = LaneStore(HostStore(host.path))
    before = counts(host)
    with pytest.raises(PermissionError, match="LANE_REOPEN_AUTHORITY_STALE"):
        seal_successor(tmp_path, store, actor, request)
    assert counts(host) == before


def test_unchanged_event_authority_seals_after_restart(tmp_path):
    host, actor, request, store, opened = reopened(tmp_path)
    restarted = LaneStore(HostStore(host.path))
    assert seal_successor(tmp_path, restarted, actor, request).gate.outcome == "SEALED"
