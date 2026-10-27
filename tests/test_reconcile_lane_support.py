"""Shared deterministic fixtures for requirement HMT-B07 repair witnesses."""
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_models import Reopen
from hmt_rnd.lane_store import LaneStore


def deny(context):
    return execute_gate(context).model_copy(update={"outcome": "DENIED", "reasons": ("BAD",)})


def event(name="repair", changed="first", reason="ARTIFACT_DRIFT", successor="fixed"):
    return Reopen(event_id=name, lineage_id="mission-1", changed_candidates=(changed,),
                  successor_candidate_id=successor, reason=reason,
                  termination_condition="Current exact-candidate gate receipt")


def fixture(root, evaluator=execute_gate):
    host, actor, request = setup_host(root)
    store = LaneStore(host)
    receipt = store.submit(actor, request, make_candidate(root), lambda: Clock(now=10.0),
                           evaluator)
    return host, actor, request, store, receipt


def assert_counts(host, reopens, invalidations):
    with host.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM lane_reopens").fetchone()[0] == reopens
        assert db.execute("SELECT COUNT(*) FROM lane_invalidations").fetchone()[0] == invalidations
