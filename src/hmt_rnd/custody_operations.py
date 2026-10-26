"""Atomic immutable intent and uncertainty reservation in the owning domain."""
from uuid import uuid4

from .custody_database import CustodyFault, Domain
from .custody_models import Intent, Reservation


def stage(domain: Domain, intent: Intent) -> None:
    intent = Intent.model_validate(intent)
    with domain.transaction() as db:
        domain.authority(db, "custody.stage", intent.principal, intent.effect_id)
        row = db.execute("SELECT digest,target FROM custody_intents WHERE principal=? AND effect=?",
                         (intent.principal, intent.effect_id)).fetchone()
        if row and (row["digest"], row["target"]) != (intent.payload_digest, intent.endpoint_id):
            raise CustodyFault("INTENT_COLLISION")
        db.execute("INSERT OR IGNORE INTO custody_intents VALUES(?,?,?,?,'STAGED',NULL)",
                   (intent.principal, intent.effect_id, intent.payload_digest, intent.endpoint_id))


def reserve(domain: Domain, principal: str, effect: str) -> Reservation:
    with domain.transaction() as db:
        domain.authority(db, "custody.reserve", principal, effect)
        row = db.execute("SELECT * FROM custody_intents WHERE principal=? AND effect=?",
                         (principal, effect)).fetchone()
        if not row:
            raise CustodyFault("EFFECT_UNKNOWN")
        if row["status"] == "OUTCOME_UNCERTAIN":
            raise CustodyFault("RECONCILIATION_REQUIRED")
        if row["status"] == "COMMITTED":
            raise CustodyFault("EFFECT_ALREADY_COMMITTED")
        intent = Intent(endpoint_id=row["target"], principal=principal, effect_id=effect,
                        payload_digest=row["digest"])
        result = Reservation(intent=intent, reservation_id=uuid4().hex)
        db.execute("UPDATE custody_intents SET status='OUTCOME_UNCERTAIN',reservation=? "
                   "WHERE principal=? AND effect=?", (result.reservation_id, principal, effect))
        return result
