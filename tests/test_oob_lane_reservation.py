"""RC-LANE-05: reserved successor identities are global and cannot be stolen."""
import pytest
from test_lane_reopen import reopen_request
from test_lane_tracer import execute_gate, make_candidate
from test_oob_lane_support import counts, reopened, seal_successor
from test_reconcile_lane_support import event

from hmt_rnd.host_models import Clock


def test_cross_lineage_cannot_consume_reserved_successor(tmp_path):
    host, actor, request, store, opened = reopened(tmp_path)
    before = counts(host)
    intruder = make_candidate(tmp_path, "fixed").model_copy(update={"lineage_id": "mission-B"})
    with pytest.raises(PermissionError, match="LANE_RESERVED_SUCCESSOR_BINDING"):
        store.submit(actor, request, intruder, lambda: Clock(now=12.0), execute_gate)
    assert counts(host) == before
    assert seal_successor(tmp_path, store, actor, request).candidate.reopen_id == "repair"


def test_duplicate_global_reservation_denied_before_mutation(tmp_path):
    host, actor, request, store, opened = reopened(tmp_path)
    other = make_candidate(tmp_path, "other").model_copy(update={"lineage_id": "mission-B"})
    store.submit(actor, request, other, lambda: Clock(now=12.0), execute_gate)
    other.artifact.write_text("changed B")
    before = counts(host)
    collision = event(name="other-repair", changed="other").model_copy(
        update={"lineage_id": "mission-B"})
    with pytest.raises(PermissionError, match="LANE_SUCCESSOR_ALREADY_RESERVED"):
        store.reopen(actor, reopen_request(host, actor, request), collision,
                     lambda: Clock(now=13.0))
    assert counts(host) == before
    assert seal_successor(tmp_path, store, actor, request).gate.outcome == "SEALED"
