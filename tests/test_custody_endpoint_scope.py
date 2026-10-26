"""A separately trusted endpoint cannot complete another target's reservation."""
import sqlite3

import pytest
from test_custody_support import KEY, authority, prepare, setup

from hmt_rnd.custody_adapter import CustodyStore
from hmt_rnd.custody_database import CustodyFault
from hmt_rnd.custody_endpoint import Endpoint
from hmt_rnd.custody_models import Proof
from hmt_rnd.custody_signing import sign


def test_trusted_other_endpoint_cannot_complete_reservation(tmp_path):
    original, _, _ = setup(tmp_path)
    store = CustodyStore(original.domain.path, authority,
                         {"endpoint": KEY, "other-endpoint": b"b" * 32})
    other_path = tmp_path / "other.sqlite"
    prepare(other_path)
    other = Endpoint(other_path, "other-endpoint", b"b" * 32, authority)
    reservation = store.reserve("alice", "effect1")
    with pytest.raises(CustodyFault, match="ENDPOINT_SCOPE_MISMATCH"):
        proof = other.apply(reservation)
        store.reconcile(proof)
    with sqlite3.connect(other_path) as db:
        assert db.execute("SELECT count(*) FROM custody_endpoint_effects").fetchone()[0] == 0


def test_authenticated_wrong_target_proof_is_rejected_by_store(tmp_path):
    original, _, _ = setup(tmp_path)
    store = CustodyStore(original.domain.path, authority,
                         {"endpoint": KEY, "other-endpoint": b"b" * 32})
    reservation = store.reserve("alice", "effect1")
    wrong_intent = reservation.intent.model_copy(update={"endpoint_id": "other-endpoint"})
    proof = Proof(intent=wrong_intent, reservation_id=reservation.reservation_id,
                  endpoint_id="other-endpoint", outcome="COMMITTED", signature="0" * 64)
    proof = proof.model_copy(update={"signature": sign(proof, b"b" * 32)})
    with pytest.raises(CustodyFault, match="ENDPOINT_SCOPE_MISMATCH"):
        store.reconcile(proof)
    assert store.status("alice", "effect1") == "OUTCOME_UNCERTAIN"
