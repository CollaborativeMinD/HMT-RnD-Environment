"""RC-REOPEN-EXPIRY-01: admission must follow the last ancestor I/O."""
import math

import pytest
from test_ancestor_freshness_issuance_support import prepare
from test_reopen_expiry_support import ReadClock, expiring_grant, observation, state_digest
from test_revision_issuance_support import snapshot

from hmt_rnd.host_store import HostStore
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("depth,stage", [(1, "CMAD1"), (2, "CMAD2"), (2, "CMAD1")])
@pytest.mark.parametrize("expiry", ["grant", "evidence"])
@pytest.mark.parametrize("time", ["unchanged", "below", "equal", "above"])
@pytest.mark.parametrize("restart", [False, True])
def test_reopen_authority_after_real_parent_reads(tmp_path, monkeypatch, depth, stage,
                                                 expiry, time, restart):
    host, store, ancestors, owner, request, scoped, event, origin = prepare(tmp_path, depth)
    expiring_grant(host, owner, scoped, expiry)
    if restart:
        store = LaneStore(HostStore(host.path))
    targets = {"unchanged": 12.0, "below": math.nextafter(50.0, 0.0),
               "equal": 50.0, "above": math.nextafter(50.0, math.inf)}
    clock = ReadClock(monkeypatch, stage, targets[time])
    before = snapshot(host)
    result, error = None, None
    try:
        result = store.reopen(owner, scoped, event, clock)
    except PermissionError as failure:
        error = str(failure)
    after = snapshot(host)
    observation(tmp_path, depth=depth, stage=stage, expiry=expiry, time=time,
                restart=restart, clock_calls=clock.calls, verified_stages=clock.reads,
                error=error, issued=result is not None, before=state_digest(before),
                after=state_digest(after), unchanged=before == after)
    assert clock.reads == (["CMAD1"] if depth == 1 else ["CMAD2", "CMAD1"])
    if time in {"equal", "above"}:
        assert error == "HOST_LEASE_OR_EVIDENCE_EXPIRED"
        assert result is None and before == after
    else:
        assert error is None and result is not None
        assert result.required_stage == origin.candidate.stage
        assert result.invalidated_candidates == (origin.candidate.candidate_id,)
        assert len(after["lane_reopens"]) == len(before["lane_reopens"]) + 1
        assert len(after["lane_invalidations"]) == len(before["lane_invalidations"]) + 1
    reopened = LaneStore(HostStore(host.path))
    assert snapshot(reopened.host) == after
    assert reopened.receipt(origin.candidate.candidate_id) == origin
    assert [reopened.receipt(x.candidate.candidate_id) for x in ancestors] == ancestors
