"""RC-RECEIPT-PATH-01: working-directory changes must not rebind saved paths."""
import pytest
from test_receipt_path_support import invoke, observe, prepare
from test_revision_issuance_support import snapshot


@pytest.mark.parametrize("artifact_relative", [False, True])
@pytest.mark.parametrize("evidence_relative", [False, True])
@pytest.mark.parametrize("outcome", ["SEALED", "DENIED"])
@pytest.mark.parametrize("child", [False, True])
def test_receipt_paths_survive_cwd_change_and_process_restart(
        tmp_path, monkeypatch, artifact_relative, evidence_relative, outcome, child):
    scope, host, owner, request, store, first, candidate, seen, other = prepare(
        tmp_path, monkeypatch, artifact_relative, evidence_relative, outcome)
    before = snapshot(host)
    monkeypatch.chdir(other)
    actual = invoke(scope, "verify", other, child)
    observe(tmp_path, operation="verify", artifact_relative=artifact_relative,
            evidence_relative=evidence_relative, outcome=outcome, child=child, actual=actual,
            artifact=str(first.candidate.artifact), evidence=str(first.gate.evidence[0].path))
    assert actual.get("error") is None
    assert actual["receipt"] == first.receipt_sha256
    assert first.candidate.artifact == scope / "first.txt"
    assert first.gate.evidence[0].path == scope / "first.evidence"
    assert seen == [str(candidate.artifact)]
    assert store.receipt("first") == first and snapshot(host) == before


@pytest.mark.parametrize("artifact_relative", [False, True])
@pytest.mark.parametrize("evidence_relative", [False, True])
@pytest.mark.parametrize("child", [False, True])
def test_downstream_consumes_original_receipt_from_new_cwd(
        tmp_path, monkeypatch, artifact_relative, evidence_relative, child):
    scope, host, owner, request, store, first, candidate, seen, other = prepare(
        tmp_path, monkeypatch, artifact_relative, evidence_relative)
    monkeypatch.chdir(other)
    actual = invoke(scope, "consume", other, child)
    observe(tmp_path, operation="consume", artifact_relative=artifact_relative,
            evidence_relative=evidence_relative, child=child, actual=actual)
    assert actual.get("error") is None
    assert actual["outcome"] == "SEALED" and actual["parent"] == first.receipt_sha256
    assert store.receipt("first") == first
