"""RC-CUSTODY-001: cancelled reservations retain the effect/input binding."""
import sqlite3

import pytest
from test_custody_support import KEY, authority, revoke, setup

from hmt_rnd.custody_database import CustodyFault
from hmt_rnd.custody_endpoint import Endpoint


@pytest.mark.parametrize("operation", ["apply", "lookup_or_cancel"])
@pytest.mark.parametrize("restart", [False, True])
def test_cancelled_effect_rejects_changed_input(tmp_path, operation, restart):
    store, endpoint, _ = setup(tmp_path)
    old = store.reserve("alice", "effect1")
    assert store.reconcile(endpoint.lookup_or_cancel(old)) == "NOT_EXECUTED"
    changed = old.model_copy(update={
        "reservation_id": "new-reservation",
        "intent": old.intent.model_copy(update={"payload_digest": "b" * 64})})
    if restart:
        endpoint = Endpoint(endpoint.domain.path, "endpoint", KEY, authority)
    with pytest.raises(CustodyFault, match="INTENT_COLLISION"):
        getattr(endpoint, operation)(changed)
    with sqlite3.connect(endpoint.domain.path) as db:
        assert db.execute("SELECT count(*) FROM custody_endpoint_effects").fetchone()[0] == 0
        assert db.execute("SELECT digest,status FROM custody_endpoint_reservations").fetchall() == [
            ("a" * 64, "NOT_EXECUTED")]


def test_same_input_retry_survives_restart_and_old_cancel_fence(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    old = store.reserve("alice", "effect1")
    proof = endpoint.lookup_or_cancel(old)
    assert store.reconcile(proof) == "NOT_EXECUTED"
    endpoint = Endpoint(endpoint.domain.path, "endpoint", KEY, authority)
    retry = store.reserve("alice", "effect1")
    assert retry.intent == old.intent and retry.reservation_id != old.reservation_id
    with pytest.raises(CustodyFault, match="RESERVATION_CANCELLED"):
        endpoint.apply(old)
    with pytest.raises(CustodyFault, match="RESERVATION_MISMATCH"):
        store.reconcile(proof)
    assert store.reconcile(endpoint.apply(retry)) == "COMMITTED"
    assert endpoint.apply(retry).outcome == "COMMITTED"
    with sqlite3.connect(endpoint.domain.path) as db:
        assert db.execute("SELECT * FROM custody_endpoint_effects").fetchall() == [
            ("alice", "effect1", "a" * 64)]


def test_different_effect_remains_independent_and_retry_requires_authority(tmp_path):
    store, endpoint, intent = setup(tmp_path)
    old = store.reserve("alice", "effect1")
    assert store.reconcile(endpoint.lookup_or_cancel(old)) == "NOT_EXECUTED"
    other = intent.model_copy(update={"effect_id": "effect2", "payload_digest": "b" * 64})
    store.stage(other)
    assert store.reconcile(endpoint.apply(store.reserve("alice", "effect2"))) == "COMMITTED"
    retry = store.reserve("alice", "effect1")
    revoke(endpoint.domain.path)
    with pytest.raises(CustodyFault, match="HOLD"):
        endpoint.apply(retry)
    assert store.status("alice", "effect1") == "OUTCOME_UNCERTAIN"
