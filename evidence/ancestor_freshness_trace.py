"""Baseline-only RC-ANCESTOR-01 observer; not a post-repair pass oracle."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from test_ancestor_freshness_support import chain, drift
from test_lane_tracer import execute_gate

from hmt_rnd.host_models import Clock


def observe(root, depth, change):
    host, store, receipts, owner, request, candidate = chain(root, depth)
    drift(host, "CMAD1", change)
    with host.transaction() as db:
        assignment = db.execute("SELECT principal,revision FROM host_tasks WHERE task_id='CMAD1'")
        current = assignment.fetchone()
    calls = []

    def observed_gate(context):
        calls.append(context.candidate.candidate_id)
        return execute_gate(context)

    result = store.submit(owner, request, candidate, lambda: Clock(now=11.0), observed_gate)
    return {"depth": depth, "change": change, "current_assignment": current,
            "recorded_assignment": [receipts[0].principal, receipts[0].task_revision],
            "downstream_outcome": result.gate.outcome, "evaluator_calls": len(calls),
            "predecessor_receipt_unchanged": store.receipt("candidate-1") == receipts[0]}


if __name__ == "__main__":
    observations = []
    for depth in (1, 2):
        for change in ("revision", "reassigned", "missing", "principal-only"):
            with TemporaryDirectory() as directory:
                observations.append(observe(Path(directory), depth, change))
    print(json.dumps(observations, indent=2))
