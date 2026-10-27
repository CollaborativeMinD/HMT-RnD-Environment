"""Scope-checked source drift includes evidence and absent in-scope files."""
from pathlib import Path

from .lane_evidence import digest_file
from .lane_models import Receipt


def source_changed(path: Path, expected: str, root: Path) -> bool:
    try:
        return digest_file(path, root) != expected
    except PermissionError as error:
        if isinstance(error.__cause__, FileNotFoundError):
            return True
        raise


def artifact_changed(receipt: Receipt, root: Path) -> bool:
    sources = [(receipt.candidate.artifact, receipt.candidate.artifact_sha256)]
    sources += [(entry.path, entry.sha256) for entry in receipt.gate.evidence]
    # Evaluate every source so earlier drift never hides a later scope violation.
    observations = [source_changed(path, digest, root) for path, digest in sources]
    return any(observations)
