"""Absolute saved spellings support genuine drift recovery after cwd changes."""
import pytest
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate
from test_receipt_path_support import observe, prepare
from test_reconcile_lane_support import event

from hmt_rnd.host_models import Clock
from hmt_rnd.host_store import HostStore
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("artifact_relative", [False, True])
@pytest.mark.parametrize("evidence_relative", [False, True])
@pytest.mark.parametrize("source", ["artifact", "evidence"])
@pytest.mark.parametrize("missing", [False, True])
def test_reopen_and_reseal_original_source_from_new_cwd(
        tmp_path, monkeypatch, artifact_relative, evidence_relative, source, missing):
    scope, host, owner, request, store, first, candidate, seen, other = prepare(
        tmp_path, monkeypatch, artifact_relative, evidence_relative)
    path = scope / ("first.txt" if source == "artifact" else "first.evidence")
    original = store.snapshot(first.candidate.artifact_sha256)
    path.unlink() if missing else path.write_bytes(b"changed source")
    scoped = reopen_request(host, owner, request)
    monkeypatch.chdir(other)
    store = LaneStore(HostStore(host.path))
    opened, error = None, None
    try:
        opened = store.reopen(owner, scoped, event(), lambda: Clock(now=11.0))
    except PermissionError as failure:
        error = str(failure)
    observe(tmp_path, operation="reopen", artifact_relative=artifact_relative,
            evidence_relative=evidence_relative, source=source, missing=missing,
            error=error, issued=opened is not None)
    assert error is None and opened is not None
    assert opened.required_stage == "CMAD1" and opened.invalidated_candidates == ("first",)
    fixed = store.submit(owner, request, make_candidate(scope, "fixed", reopen="repair"),
                         lambda: Clock(now=12.0), execute_gate)
    assert fixed.gate.outcome == "SEALED"
    assert store.receipt("first") == first
    assert store.snapshot(first.candidate.artifact_sha256) == original
