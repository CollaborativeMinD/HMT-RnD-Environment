"""Test-only fresh-process receipt verification/consumption from another cwd."""
import hashlib
import json
import sys
from pathlib import Path

from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock
from hmt_rnd.host_store import HostStore
from hmt_rnd.lane_evidence import verify_receipt_artifacts
from hmt_rnd.lane_store import LaneStore


def perform(scope, mode):
    store = LaneStore(HostStore(scope / "host.sqlite"))
    try:
        receipt = store.receipt("first")
        if mode == "consume":
            _, owner, request = setup_host(scope, "CMAD2")
            result = store.submit(owner, request,
                                  make_candidate(scope, "second", "CMAD2", "first"),
                                  lambda: Clock(now=11.0), execute_gate)
            return {"outcome": result.gate.outcome, "parent": result.gate.predecessor_sha256}
        verify_receipt_artifacts(receipt, scope)
        digests = [receipt.candidate.artifact_sha256]
        digests += [item.sha256 for item in receipt.gate.evidence]
        assert all(hashlib.sha256(store.snapshot(value)).hexdigest() == value for value in digests)
        return {"error": None, "receipt": receipt.receipt_sha256, "snapshots": digests}
    except PermissionError as error:
        return {"error": str(error)}


if __name__ == "__main__":
    print(json.dumps(perform(Path(sys.argv[1]), sys.argv[2])))
