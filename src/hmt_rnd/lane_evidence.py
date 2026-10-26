"""Bounded artifact/evidence identity; no arbitrary instructions are executed."""
import hashlib
from pathlib import Path

from .lane_models import Candidate, GateContext, GateResult, Receipt


def digest_file(path: Path, root: Path) -> str:
    path, root = path.resolve(), root.resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise PermissionError("LANE_ARTIFACT_SCOPE")
    with path.open("rb") as stream:
        data = stream.read(16777217)
    if len(data) > 16777216:
        raise PermissionError("LANE_ARTIFACT_BOUND")
    return hashlib.sha256(data).hexdigest()


def verify_artifact(candidate: Candidate, root: Path) -> None:
    if digest_file(candidate.artifact, root) != candidate.artifact_sha256:
        raise PermissionError("LANE_ARTIFACT_DRIFT")


def verify_result(context: GateContext, result: GateResult, root: Path) -> None:
    expected = (context.candidate.stage, context.candidate.artifact_sha256,
                context.predecessor_sha256, context.policy, context.epoch)
    actual = (result.stage, result.artifact_sha256, result.predecessor_sha256,
              result.policy, result.epoch)
    if actual != expected:
        raise PermissionError("LANE_GATE_CONTEXT_MISMATCH")
    if result.outcome == "DENIED" and not result.reasons:
        raise PermissionError("LANE_DENIAL_REASON_REQUIRED")
    for evidence in result.evidence:
        if digest_file(evidence.path, root) != evidence.sha256:
            raise PermissionError("LANE_EVIDENCE_DRIFT")


def verify_receipt_artifacts(receipt: Receipt, root: Path) -> None:
    verify_artifact(receipt.candidate, root)
    context = GateContext(candidate=receipt.candidate,
                          predecessor_sha256=receipt.gate.predecessor_sha256,
                          policy=receipt.gate.policy, epoch=receipt.gate.epoch,
                          principal=receipt.principal, task_id=receipt.task_id,
                          task_revision=receipt.task_revision)
    verify_result(context, receipt.gate, root)
