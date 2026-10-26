"""Fresh authority and exact authenticated proof close the existing reservation."""
from collections.abc import Mapping

from .custody_database import CustodyFault, Domain
from .custody_models import Proof
from .custody_signing import verify


def reconcile(domain: Domain, proof: Proof, keys: Mapping[str, bytes]) -> str:
    proof = Proof.model_validate(proof)
    key = keys.get(proof.endpoint_id)
    if key is None:
        raise CustodyFault("ENDPOINT_UNKNOWN")
    verify(proof, key)
    intent = proof.intent
    if intent.endpoint_id != proof.endpoint_id:
        raise CustodyFault("ENDPOINT_SCOPE_MISMATCH")
    with domain.transaction() as db:
        domain.authority(db, "custody.reconcile", intent.principal, intent.effect_id)
        row = db.execute("SELECT * FROM custody_intents WHERE principal=? AND effect=?",
                         (intent.principal, intent.effect_id)).fetchone()
        if not row or row["digest"] != intent.payload_digest:
            raise CustodyFault("PROOF_INTENT_MISMATCH")
        if row["target"] != proof.endpoint_id:
            raise CustodyFault("ENDPOINT_SCOPE_MISMATCH")
        if row["reservation"] != proof.reservation_id:
            raise CustodyFault("RESERVATION_MISMATCH")
        if row["status"] == proof.outcome:
            return proof.outcome
        if row["status"] != "OUTCOME_UNCERTAIN":
            raise CustodyFault("RECONCILIATION_STATE_INVALID")
        db.execute("UPDATE custody_intents SET status=? WHERE principal=? AND effect=?",
                   (proof.outcome, intent.principal, intent.effect_id))
        return proof.outcome
