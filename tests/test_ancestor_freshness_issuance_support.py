"""Fresh downstream authority fixture for ancestor drift during reopen issuance."""
from test_ancestor_freshness_support import chain
from test_lane_tracer import execute_gate, make_candidate
from test_oob_lane_support import current_grant
from test_reconcile_lane_support import event

from hmt_rnd.host_models import Clock


def prepare(root, depth):
    host, store, ancestors, owner, request, candidate = chain(root, depth)
    origin = store.submit(owner, request, candidate, lambda: Clock(now=11.0), execute_gate)
    candidate.artifact.write_text("target artifact changed")
    scoped = current_grant(host, owner, request, "policy-1", 1, "lane.reopen")
    change = event(changed=candidate.candidate_id)
    return host, store, ancestors, owner, request, scoped, change, origin


def successor(root, store, owner, request, origin):
    candidate = make_candidate(root, "fixed", origin.candidate.stage,
                               origin.candidate.predecessor_id, "repair")
    return store.submit(owner, request, candidate, lambda: Clock(now=13.0), execute_gate)
