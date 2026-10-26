"""Fresh authority, immutable identity, and exact proof boundary counterexamples."""
import pytest
from pydantic import ValidationError
from test_custody_support import revoke, setup

from hmt_rnd.custody_database import CustodyFault
from hmt_rnd.custody_models import Intent


def test_revoke_before_reservation_leaves_staged(tmp_path):
    store, _, _ = setup(tmp_path)
    revoke(store.domain.path)
    with pytest.raises(CustodyFault, match="HOLD"):
        store.reserve("alice", "effect1")
    with store.domain.transaction() as db:
        assert db.execute("SELECT status FROM custody_intents").fetchone()[0] == "STAGED"


def test_reconcile_requires_current_authority(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    proof = endpoint.apply(store.reserve("alice", "effect1"))
    revoke(store.domain.path)
    with pytest.raises(CustodyFault, match="HOLD"):
        store.reconcile(proof)


def test_tampered_proof_cannot_close_uncertainty(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    proof = endpoint.apply(store.reserve("alice", "effect1"))
    with pytest.raises(CustodyFault, match="PROOF_SIGNATURE_INVALID"):
        store.reconcile(proof.model_copy(update={"signature": "0" * 64}))
    assert store.status("alice", "effect1") == "OUTCOME_UNCERTAIN"


def test_intent_collision_and_closed_wire(tmp_path):
    store, _, intent = setup(tmp_path)
    with pytest.raises(CustodyFault, match="INTENT_COLLISION"):
        store.stage(intent.model_copy(update={"payload_digest": "b" * 64}))
    with pytest.raises(ValidationError):
        Intent.model_validate({**intent.model_dump(), "extra": "untrusted"})
