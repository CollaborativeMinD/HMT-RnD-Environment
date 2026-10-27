"""Prior sealed/denied bytes survive path mutation in atomic bounded snapshots."""
from pathlib import Path

import pytest
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_models import GateContext, GateResult
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("outcome", ["SEALED", "DENIED"])
def test_preserved_artifact_and_gate_bytes_survive_mutation(tmp_path: Path, outcome: str) -> None:
    host, owner, request = setup_host(tmp_path)
    store = LaneStore(host)

    def gate(context: GateContext) -> GateResult:
        result = execute_gate(context)
        return result.model_copy(update={"outcome": outcome, "reasons": ("CONTROL",)})

    receipt = store.submit(owner, request, make_candidate(tmp_path),
                           lambda: Clock(now=10.0), gate)
    evidence = receipt.gate.evidence[0]
    original_evidence = evidence.path.read_bytes()
    receipt.candidate.artifact.write_bytes(b"mutated current bytes")
    evidence.path.write_bytes(b"mutated current evidence")
    restarted = LaneStore(host)
    assert restarted.snapshot(receipt.candidate.artifact_sha256) == b"valid artifact"
    assert restarted.snapshot(evidence.sha256) == original_evidence


def test_snapshot_total_bound_rolls_back_all_stage_mutations(tmp_path: Path) -> None:
    import hashlib

    from hmt_rnd.lane_models import Evidence
    host, owner, request = setup_host(tmp_path)
    store = LaneStore(host)

    def oversized(context: GateContext) -> GateResult:
        result = execute_gate(context)
        path = tmp_path / "oversize.bin"
        path.write_bytes(b"x" * 16777216)
        item = Evidence(path=path, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        return result.model_copy(update={"evidence": (item,)})

    with pytest.raises(PermissionError, match="LANE_SNAPSHOT_TOTAL_BOUND"):
        store.submit(owner, request, make_candidate(tmp_path),
                     lambda: Clock(now=10.0), oversized)
    with host.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM lane_candidates").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM lane_artifacts").fetchone()[0] == 0
