"""Exact SQLite state and fresh-authority fixtures for RC-LANE-07."""
from test_oob_lane_support import current_grant
from test_reconcile_lane_support import fixture

from hmt_rnd.host_models import Assignment


def snapshot(host):
    with host.transaction() as db:
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return {name: tuple(sorted(db.execute('SELECT * FROM "' + name + '"').fetchall(),
                                   key=repr)) for (name,) in tables.fetchall()}


def changed_origin(root):
    host, actor, request, store, origin = fixture(root)
    origin.candidate.artifact.write_text("observed artifact drift")
    current_grant(host, actor, request, "policy-1", 1, "lane.reopen")
    return host, actor, request, store, origin


def advance(host, actor, request):
    host.assign(Assignment(task_id=request.task_id, principal=actor.principal, revision=2))
    revised = request.model_copy(update={"revision": 2})
    current_grant(host, actor, revised, "policy-1", 1, "lane.seal")
    return current_grant(host, actor, revised, "policy-1", 1, "lane.reopen")
