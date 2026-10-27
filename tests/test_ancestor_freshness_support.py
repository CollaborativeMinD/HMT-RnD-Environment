"""Controlled ancestor assignment fixtures; no assignment-policy redesign."""
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Assignment, Clock
from hmt_rnd.lane_store import LaneStore


def chain(root, depth):
    host, owner, request = setup_host(root)
    store = LaneStore(host)
    receipts = []
    parent = None
    for index in range(1, depth + 1):
        stage, name = f"CMAD{index}", f"candidate-{index}"
        if index > 1:
            _, owner, request = setup_host(root, stage)
        candidate = make_candidate(root, name, stage, parent)
        receipts.append(store.submit(owner, request, candidate,
                                     lambda: Clock(now=10.0), execute_gate))
        parent = name
    _, downstream, scoped = setup_host(root, f"CMAD{depth + 1}")
    candidate = make_candidate(root, "downstream", f"CMAD{depth + 1}", parent)
    return host, store, receipts, downstream, scoped, candidate


def drift(host, task, change):
    if change in {"revision", "reassigned"}:
        owner = "alice" if change == "revision" else "bob"
        host.assign(Assignment(task_id=task, principal=owner, revision=2))
    else:
        with host.transaction() as db:
            if change == "missing":
                db.execute("DELETE FROM host_tasks WHERE task_id=?", (task,))
            else:
                db.execute("UPDATE host_tasks SET principal='bob' WHERE task_id=?", (task,))
