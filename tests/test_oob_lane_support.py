"""Controlled host fixtures for reserved successor and event authority tracers."""
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate
from test_reconcile_lane_support import event, fixture

from hmt_rnd.host_models import Clock, Grant


def reopened(root):
    host, actor, request, store, first = fixture(root)
    first.candidate.artifact.write_text("changed")
    opened = store.reopen(actor, reopen_request(host, actor, request), event(),
                          lambda: Clock(now=11.0))
    return host, actor, request, store, opened


def current_grant(host, actor, request, policy, epoch, operation):
    host.grant(Grant(**actor.model_dump(), task_id=request.task_id, revision=request.revision,
                     operation=operation,
                     root=request.root, destination="local", policy=policy, epoch=epoch,
                     not_before=1.0, expires=100.0, evidence_expires=90.0))
    return request.model_copy(update={"operation": operation})


def counts(host):
    with host.transaction() as db:
        return tuple(db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
                     for table in ("lane_candidates", "lane_reopens", "lane_invalidations",
                                   "lane_closures", "lane_artifacts"))


def seal_successor(root, store, actor, request, now=15.0):
    return store.submit(actor, request, make_candidate(root, "fixed", reopen="repair"),
                         lambda: Clock(now=now), execute_gate)
