"""Read-path parity adapters; snapshot execution retains production hash validation."""
import hashlib
import sqlite3
from pathlib import Path

from hmt_rnd.lane_artifacts import preserve, preserved_bytes
from hmt_rnd.lane_evidence import digest_file
from hmt_rnd.lane_models import Candidate, Evidence, GateResult


def observe(mode: str, path: Path, root: Path, expected: bytes) -> str:
    digest = hashlib.sha256(expected).hexdigest()
    if mode == "digest":
        return digest_file(path, root)
    evidence = root / "empty.evidence"
    evidence.write_bytes(b"")
    candidate = Candidate(candidate_id="first", lineage_id="mission", stage="CMAD1",
                          artifact=path, artifact_sha256=digest)
    gate = GateResult(stage="CMAD1", artifact_sha256=digest, predecessor_sha256=None,
                      policy="policy", epoch=1, outcome="SEALED", evidence=(Evidence(
                          path=evidence, sha256=hashlib.sha256(b"").hexdigest()),))
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE lane_artifacts(digest TEXT PRIMARY KEY,body BLOB)")
        preserve(db, candidate, gate, root)
        assert preserved_bytes(db, digest) == expected
    return digest
