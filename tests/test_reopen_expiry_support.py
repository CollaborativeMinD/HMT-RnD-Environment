"""Controlled clock cut during real ancestor verification; never bypass the reader."""
import hashlib
import json

from hmt_rnd import lane_queries
from hmt_rnd.host_models import Clock, Grant


class ReadClock:
    def __init__(self, monkeypatch, stage, target):
        self.now, self.target, self.stage = 12.0, target, stage
        self.calls, self.reads = [], []
        original = lane_queries.verify_receipt_artifacts

        def verify(receipt, root):
            original(receipt, root)
            self.reads.append(receipt.candidate.stage)
            if receipt.candidate.stage == self.stage:
                self.now = self.target

        monkeypatch.setattr(lane_queries, "verify_receipt_artifacts", verify)

    def __call__(self):
        self.calls.append(self.now)
        return Clock(now=self.now)


def expiring_grant(host, owner, request, expiry):
    limits = {"expires": 50.0, "evidence_expires": 80.0}
    if expiry == "evidence":
        limits = {"expires": 80.0, "evidence_expires": 50.0}
    host.grant(Grant(**owner.model_dump(), task_id=request.task_id, revision=request.revision,
                     operation=request.operation, root=request.root, destination="local",
                     policy="policy-1", epoch=1, not_before=1.0, **limits))


def state_digest(state):
    return hashlib.sha256(repr(state).encode()).hexdigest()


def observation(root, **fields):
    (root / "expiry_observation.json").write_text(json.dumps(fields, indent=2) + "\n")
