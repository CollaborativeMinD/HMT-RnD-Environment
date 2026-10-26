"""Even valid signatures cannot widen proof scope or change invalid states."""
import pytest
from test_custody_support import KEY, authority, setup

from hmt_rnd.custody_adapter import CustodyStore
from hmt_rnd.custody_database import CustodyFault
from hmt_rnd.custody_signing import sign


def signed(proof, **updates):
    changed = proof.model_copy(update=updates)
    return changed.model_copy(update={"signature": sign(changed, KEY)})


def test_unknown_endpoint_and_self_inconsistent_proof_rejected(tmp_path):
    original, endpoint, _ = setup(tmp_path)
    proof = endpoint.apply(original.reserve("alice", "effect1"))
    with pytest.raises(CustodyFault, match="ENDPOINT_UNKNOWN"):
        original.reconcile(signed(proof, endpoint_id="unknown"))
    trust = CustodyStore(original.domain.path, authority,
                         {"endpoint": KEY, "other-endpoint": KEY})
    with pytest.raises(CustodyFault, match="ENDPOINT_SCOPE_MISMATCH"):
        trust.reconcile(signed(proof, endpoint_id="other-endpoint"))
    assert original.status("alice", "effect1") == "OUTCOME_UNCERTAIN"


def test_authenticated_wrong_intent_rejected(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    proof = endpoint.apply(store.reserve("alice", "effect1"))
    wrong = proof.intent.model_copy(update={"payload_digest": "b" * 64})
    with pytest.raises(CustodyFault, match="PROOF_INTENT_MISMATCH"):
        store.reconcile(signed(proof, intent=wrong))
    assert store.status("alice", "effect1") == "OUTCOME_UNCERTAIN"


def test_inconsistent_local_state_does_not_accept_proof(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    proof = endpoint.apply(store.reserve("alice", "effect1"))
    with store.domain.transaction() as db:
        db.execute("UPDATE custody_intents SET status='STAGED'")
    with pytest.raises(CustodyFault, match="RECONCILIATION_STATE_INVALID"):
        store.reconcile(proof)
