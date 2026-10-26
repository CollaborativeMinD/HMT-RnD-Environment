"""Scope-checked source drift includes evidence and absent in-scope files."""
from pathlib import Path

from .lane_evidence import digest_file
from .lane_models import Receipt


def source_changed(path: Path, expected: str, root: Path) -> bool:
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise PermissionError("LANE_ARTIFACT_SCOPE")
    if not resolved.exists():
        return True
    return digest_file(resolved, root) != expected


def artifact_changed(receipt: Receipt, root: Path) -> bool:
    sources = [(receipt.candidate.artifact, receipt.candidate.artifact_sha256)]
    sources += [(entry.path, entry.sha256) for entry in receipt.gate.evidence]
    # Evaluate every source so earlier drift never hides a later scope violation.
    observations = [source_changed(path, digest, root) for path, digest in sources]
    return any(observations)
