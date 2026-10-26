"""Bounded content-addressed byte preservation inside lifecycle transaction."""
import hashlib
import sqlite3
from pathlib import Path

from .lane_models import Candidate, GateResult

MAX_BYTES = 16777216


def preserved_bytes(db: sqlite3.Connection, digest: str) -> bytes:
    row = db.execute("SELECT length(body) FROM lane_artifacts WHERE digest=?", (digest,)).fetchone()
    if row is None or row[0] > MAX_BYTES:
        raise PermissionError("LANE_SNAPSHOT_MISSING_OR_OVERSIZE")
    raw = db.execute("SELECT body FROM lane_artifacts WHERE digest=?", (digest,)).fetchone()
    body = bytes(raw[0])
    if hashlib.sha256(body).hexdigest() != digest:
        raise PermissionError("LANE_SNAPSHOT_INTEGRITY")
    return body


def preserve(db: sqlite3.Connection, candidate: Candidate, gate: GateResult, root: Path) -> None:
    sources = [(candidate.artifact, candidate.artifact_sha256)]
    sources.extend((item.path, item.sha256) for item in gate.evidence)
    total = 0
    for path, digest in sources:
        actual = path.resolve()
        if not actual.is_relative_to(root.resolve()) or not actual.is_file():
            raise PermissionError("LANE_SNAPSHOT_SCOPE")
        with actual.open("rb") as stream:
            body = stream.read(MAX_BYTES + 1)
        total += len(body)
        if total > MAX_BYTES:
            raise PermissionError("LANE_SNAPSHOT_TOTAL_BOUND")
        if hashlib.sha256(body).hexdigest() != digest:
            raise PermissionError("LANE_SNAPSHOT_SOURCE_DRIFT")
        db.execute("INSERT OR IGNORE INTO lane_artifacts VALUES(?,?)", (digest, body))
        preserved_bytes(db, digest)
