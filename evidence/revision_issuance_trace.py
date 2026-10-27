"""Baseline-only diagnostic retained for RC-LANE-07, not a production oracle."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from test_oob_lane_support import current_grant, seal_successor
from test_reconcile_lane_support import event
from test_revision_issuance_support import advance, changed_origin, snapshot

from hmt_rnd.host_models import Clock


def observe(root):
    host, actor, request, store, origin = changed_origin(root)
    revised = advance(host, actor, request)
    issued = store.reopen(actor, revised, event(), lambda: Clock(now=11.0))
    findings = {"origin_revision": origin.task_revision,
                "accepted_event_revision": issued.task_revision,
                "event_count": len(snapshot(host)["lane_reopens"]),
                "invalidation_count": len(snapshot(host)["lane_invalidations"])}
    try:
        seal_successor(root, store, actor, revised.model_copy(update={"operation": "lane.seal"}))
    except PermissionError as error:
        findings["successor_denial"] = str(error)
    architect = actor.model_copy(update={"role": "human_architect"})
    scoped = current_grant(host, architect, revised, "policy-1", 1, "lane.reauthorize")
    try:
        store.reauthorize(architect, scoped, "repair", lambda: Clock(now=16.0))
    except PermissionError as error:
        findings["architect_reauthorization_denial"] = str(error)
    findings["closure_count"] = len(snapshot(host)["lane_closures"])
    return findings


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        print(json.dumps(observe(Path(directory)), indent=2))
