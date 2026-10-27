"""Baseline coupling observer: reopening accepted, designated successor denied."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from test_ancestor_freshness_issuance_support import prepare, successor
from test_ancestor_freshness_support import drift
from test_revision_issuance_support import snapshot

from hmt_rnd.host_models import Clock


def observe(root, depth):
    host, store, ancestors, owner, request, scoped, change, origin = prepare(root, depth)
    drift(host, "CMAD1", "revision")
    opened = store.reopen(owner, scoped, change, lambda: Clock(now=12.0))
    result = {"ancestor_depth": depth, "event_issued": True,
              "required_stage": opened.required_stage,
              "persisted_events": len(snapshot(host)["lane_reopens"]),
              "persisted_invalidations": len(snapshot(host)["lane_invalidations"])}
    try:
        successor(root, store, owner, request, origin)
    except PermissionError as error:
        result["successor_denial"] = str(error)
    result["closures"] = len(snapshot(host)["lane_closures"])
    return result


if __name__ == "__main__":
    observations = []
    for depth in (1, 2):
        with TemporaryDirectory() as directory:
            observations.append(observe(Path(directory), depth))
    print(json.dumps(observations, indent=2))
