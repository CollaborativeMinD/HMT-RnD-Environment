"""Path-spelling persistence must remain before final exclusive-expiry admission."""
from pathlib import Path

import pytest
from test_lane_tracer import execute_gate, make_candidate, setup_host
from test_receipt_path_support import observe
from test_reopen_expiry_support import expiring_grant
from test_revision_issuance_support import snapshot

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("source", ["artifact", "evidence"])
@pytest.mark.parametrize("expiry", ["grant", "evidence"])
def test_expiry_during_absolute_spelling_denies_before_mutation(
        tmp_path, monkeypatch, source, expiry):
    scope = tmp_path / "scope"
    scope.mkdir()
    monkeypatch.chdir(tmp_path)
    host, owner, request = setup_host(scope)
    expiring_grant(host, owner, request, expiry)
    store = LaneStore(host)
    candidate = make_candidate(scope).model_copy(update={"artifact": Path("scope/first.txt")})
    target = candidate.artifact if source == "artifact" else Path("scope/first.evidence")
    now, calls = [10.0], []
    original = Path.absolute

    def absolute(path):
        value = original(path)
        if path == target:
            calls.append(str(path))
            now[0] = 50.0
        return value

    before = snapshot(host)
    monkeypatch.setattr(Path, "absolute", absolute)
    receipt, error = None, None
    try:
        receipt = store.submit(owner, request, candidate, lambda: Clock(now=now[0]), execute_gate)
    except PermissionError as failure:
        error = str(failure)
    observe(tmp_path, operation="absolute_expiry", source=source, expiry=expiry, error=error,
            issued=receipt is not None, tables_unchanged=snapshot(host) == before)
    assert error == "HOST_LEASE_OR_EVIDENCE_EXPIRED" and receipt is None
    assert calls == [str(target)]
    assert snapshot(host) == before
