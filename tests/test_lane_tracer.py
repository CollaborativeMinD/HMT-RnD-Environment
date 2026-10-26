"""Real SQLite lifecycle tracer with an executed, controlled artifact evaluator."""
import hashlib
from pathlib import Path

from hmt_rnd.host_models import Assignment, Clock, Grant, Identity, Request
from hmt_rnd.host_store import HostStore
from hmt_rnd.lane_models import Candidate, Evidence, GateContext, GateResult
from hmt_rnd.lane_store import LaneStore


def execute_gate(context: GateContext) -> GateResult:
    assert context.candidate.artifact.read_bytes() == b"valid artifact"
    path = context.candidate.artifact.with_suffix(".evidence")
    path.write_text("Executed exact-byte assertion against controlled artifact")
    evidence = Evidence(path=path, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return GateResult(stage=context.candidate.stage,
                      artifact_sha256=context.candidate.artifact_sha256,
                      predecessor_sha256=context.predecessor_sha256,
                      policy=context.policy, epoch=context.epoch, outcome="SEALED",
                      evidence=(evidence,))


def setup_host(root: Path, stage="CMAD1", operation="lane.seal"):
    host = HostStore.create(root / "host.sqlite", "policy-1")
    identity = Identity(principal="alice", role="builder", lane="CMAD", stage=stage,
                        credential="local")
    host.assign(Assignment(task_id=stage, principal="alice", revision=1))
    host.grant(Grant(**identity.model_dump(), task_id=stage, operation=operation,
                     root=str(root), destination="local", policy="policy-1", epoch=1,
                     not_before=1.0, expires=100.0, evidence_expires=90.0))
    request = Request(task_id=stage, revision=1, operation=operation,
                      root=str(root), destination="local")
    return host, identity, request


def make_candidate(root: Path, name="first", stage="CMAD1", parent=None, reopen=None):
    path = root / (name + ".txt")
    path.write_bytes(b"valid artifact")
    return Candidate(candidate_id=name, lineage_id="mission-1", stage=stage, artifact=path,
                     artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     predecessor_id=parent, reopen_id=reopen)


def test_upstream_seal_then_next_stage(tmp_path: Path) -> None:
    host, identity, request = setup_host(tmp_path)
    store = LaneStore(host)
    first = store.submit(identity, request, make_candidate(tmp_path),
                         lambda: Clock(now=10.0), execute_gate)
    assert first.gate.outcome == "SEALED"
    _, identity, request = setup_host(tmp_path, "CMAD2")
    second = store.submit(identity, request,
                          make_candidate(tmp_path, "second", "CMAD2", "first"),
                          lambda: Clock(now=11.0), execute_gate)
    assert second.gate.predecessor_sha256 == first.receipt_sha256
