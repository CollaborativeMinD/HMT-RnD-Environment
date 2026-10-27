"""Controlled native-versus-guarded pathname identity fixture and state observer."""
import hashlib

from hmt_rnd.lane_models import Candidate, Evidence, GateResult

INSIDE = b"inside approved artifact"
OUTSIDE = b"outside evaluated artifact"


def alias_fixture(base):
    root, outside = base / "scope", base / "outside"
    root.mkdir()
    (outside / "child").mkdir(parents=True)
    (root / "source").write_bytes(INSIDE)
    (outside / "source").write_bytes(OUTSIDE)
    (root / "jump").symlink_to(outside / "child", target_is_directory=True)
    return root, root / "jump" / ".." / "source"


def candidate_for(path):
    return Candidate(candidate_id="first", lineage_id="mission", stage="CMAD1",
                     artifact=path, artifact_sha256=hashlib.sha256(INSIDE).hexdigest())


def gate_for(context, root, observed):
    body = context.candidate.artifact.read_bytes()
    observed.append(body.hex())
    evidence = root / "observed.evidence"
    evidence.write_bytes(body)
    return GateResult(stage=context.candidate.stage,
                      artifact_sha256=context.candidate.artifact_sha256,
                      predecessor_sha256=context.predecessor_sha256,
                      policy=context.policy, epoch=context.epoch, outcome="SEALED",
                      evidence=(Evidence(path=evidence,
                                         sha256=hashlib.sha256(body).hexdigest()),))


def state(host):
    names = ("lane_candidates", "lane_artifacts", "lane_closures", "lane_reopens",
             "lane_invalidations", "lane_reauthorizations")
    with host.transaction() as db:
        counts = {name: db.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
                  for name in names}
        counts["last_clock"] = db.execute("SELECT last_clock FROM host_meta").fetchone()[0]
    return counts
