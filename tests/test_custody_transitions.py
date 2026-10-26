"""Standalone uncertainty/cancellation behavior over actual SQLite transactions."""
import sqlite3

import pytest
from test_custody_support import KEY, authority, setup

from hmt_rnd.custody_adapter import CustodyStore
from hmt_rnd.custody_database import CustodyFault


def test_uncertainty_reopen_and_completion_once(tmp_path):
    store, endpoint, intent = setup(tmp_path)
    reservation = store.reserve(intent.principal, intent.effect_id)
    endpoint.apply(reservation)  # Simulate endpoint commit followed by lost reply.
    reopened = CustodyStore(store.domain.path, authority, {"endpoint": KEY})
    assert reopened.status("alice", "effect1") == "OUTCOME_UNCERTAIN"
    with pytest.raises(CustodyFault, match="RECONCILIATION_REQUIRED"):
        reopened.reserve("alice", "effect1")
    proof = endpoint.lookup_or_cancel(reservation)
    assert reopened.reconcile(proof) == "COMMITTED"
    assert reopened.reconcile(proof) == "COMMITTED"
    with sqlite3.connect(endpoint.domain.path) as db:
        assert db.execute("SELECT count(*) FROM custody_endpoint_effects").fetchone()[0] == 1


def test_cancellation_fences_late_dispatch_and_stale_proof(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    old = store.reserve("alice", "effect1")
    proof = endpoint.lookup_or_cancel(old)
    assert store.reconcile(proof) == "NOT_EXECUTED"
    with pytest.raises(CustodyFault, match="RESERVATION_CANCELLED"):
        endpoint.apply(old)
    new = store.reserve("alice", "effect1")
    assert new.intent == old.intent and new.reservation_id != old.reservation_id
    with pytest.raises(CustodyFault, match="RESERVATION_MISMATCH"):
        store.reconcile(proof)
