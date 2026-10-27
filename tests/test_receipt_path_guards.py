"""Persisting absolute spellings must not normalize forbidden relative inputs."""
from pathlib import Path

import pytest
from test_lane_tracer import execute_gate, make_candidate, setup_host
from test_revision_issuance_support import snapshot

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("source", ["artifact", "evidence"])
@pytest.mark.parametrize("kind", ["link", "dangling", "parent"])
def test_relative_scope_denial_precedes_absolute_persistence(tmp_path, monkeypatch, source, kind):
    scope = tmp_path / "scope"
    scope.mkdir()
    monkeypatch.chdir(tmp_path)
    host, owner, request = setup_host(scope)
    store = LaneStore(host)
    candidate = make_candidate(scope)
    suffix = ".txt" if source == "artifact" else ".evidence"
    if kind == "parent":
        (scope / "child").mkdir()
        invalid = Path("scope/child/../first" + suffix)
    else:
        invalid = Path("scope/link")
        invalid.symlink_to("absent" if kind == "dangling" else "first" + suffix)
    if source == "artifact":
        candidate = candidate.model_copy(update={"artifact": invalid})
    calls = []

    def evaluator(context):
        calls.append(context)
        result = execute_gate(context)
        item = result.evidence[0].model_copy(update={"path": invalid})
        return result.model_copy(update={"evidence": (item,)})

    before = snapshot(host)
    with pytest.raises(PermissionError, match="LANE_ARTIFACT_SCOPE"):
        store.submit(owner, request, candidate, lambda: Clock(now=10.0), evaluator)
    assert snapshot(host) == before
    assert len(calls) == (1 if source == "evidence" else 0)
