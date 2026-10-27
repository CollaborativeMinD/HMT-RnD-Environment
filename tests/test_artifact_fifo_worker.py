"""Disposable process exercises each production read under the real host fence."""
import json
import sys
import time
from pathlib import Path

from test_artifact_fifo_hooks import install_swap
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_artifacts import preserve
from hmt_rnd.lane_evidence import digest_file
from hmt_rnd.lane_models import GateContext
from hmt_rnd.lane_store import LaneStore


def run(root: Path, mode: str) -> None:
    host, owner, request = setup_host(root)
    LaneStore(host)
    candidate = make_candidate(root)
    context = GateContext(candidate=candidate, predecessor_sha256=None, policy="policy-1",
                          epoch=1, principal="alice", task_id="CMAD1", task_revision=1)
    gate = execute_gate(context)
    install_swap(candidate.artifact, host.path)
    started = time.monotonic()
    try:
        with host.transaction() as db:
            db.execute("UPDATE host_meta SET last_clock=77")
            if mode == "digest":
                digest_file(candidate.artifact, root)
            else:
                preserve(db, candidate, gate, root)
    except PermissionError as error:
        denial = str(error)
    else:
        raise AssertionError("FIFO was not denied")
    elapsed = time.monotonic() - started
    host.revoke("alice")
    with host.transaction() as db:
        assert db.execute("SELECT last_clock FROM host_meta").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM lane_artifacts").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM lane_candidates").fetchone()[0] == 0
        assert db.execute("SELECT revoked FROM host_grants").fetchone()[0] == 1
    restarted = LaneStore(host)
    try:
        restarted.submit(owner, request, candidate, lambda: Clock(now=10.0), execute_gate)
    except PermissionError as error:
        assert str(error) == "HOST_GRANT_DENIED"
    else:
        raise AssertionError("revoked restart unexpectedly admitted")
    print(json.dumps({"denial": denial, "elapsed": elapsed, "rollback": True,
                      "revocation_proceeds": True, "restart_denied": True}), flush=True)


if __name__ == "__main__":
    run(Path(sys.argv[1]), sys.argv[2])
