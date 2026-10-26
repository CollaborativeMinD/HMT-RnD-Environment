"""Corrupt/missing snapshots and source races must fail before receipt commit."""
from pathlib import Path

import pytest
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.lane_artifacts import preserve
from hmt_rnd.lane_models import GateContext
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("present", [False, True])
def test_missing_or_corrupt_snapshot_is_not_evidence(tmp_path: Path, present: bool) -> None:
    host, _, _ = setup_host(tmp_path)
    store = LaneStore(host)
    if present:
        with host.transaction() as db:
            db.execute("INSERT INTO lane_artifacts VALUES(?,?)", ("0" * 64, b"corruption"))
    with pytest.raises(PermissionError, match="LANE_SNAPSHOT_"):
        store.snapshot("0" * 64)


@pytest.mark.parametrize("race", ["changed", "missing"])
def test_snapshot_source_race_cannot_commit(tmp_path: Path, race: str) -> None:
    host, identity, request = setup_host(tmp_path)
    LaneStore(host)
    candidate = make_candidate(tmp_path)
    context = GateContext(candidate=candidate, predecessor_sha256=None, policy="policy-1",
                          epoch=1, principal=identity.principal, task_id=request.task_id,
                          task_revision=request.revision)
    gate = execute_gate(context)
    if race == "changed":
        candidate.artifact.write_bytes(b"modified between checks")
    else:
        candidate.artifact.unlink()
    with pytest.raises(PermissionError, match="LANE_SNAPSHOT_"):
        with host.transaction() as db:
            preserve(db, candidate, gate, tmp_path)
    with host.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM lane_artifacts").fetchone()[0] == 0
