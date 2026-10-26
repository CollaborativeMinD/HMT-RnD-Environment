"""Local simulated resource endpoint; cancellation and effects serialize here."""
from pathlib import Path

from .custody_database import Authority, CustodyFault, Domain
from .custody_models import Proof, Reservation
from .custody_signing import sign


class Endpoint:
    def __init__(self, path: Path, endpoint_id: str, key: bytes,
                 authority: Authority) -> None:
        if len(key) < 32:
            raise CustodyFault("ENDPOINT_KEY_INVALID")
        self.domain, self.endpoint_id, self.key = Domain(path, authority), endpoint_id, key

    def apply(self, reservation: Reservation) -> Proof:
        return self._transition(reservation, cancel=False)

    def lookup_or_cancel(self, reservation: Reservation) -> Proof:
        return self._transition(reservation, cancel=True)

    def _transition(self, reservation: Reservation, cancel: bool) -> Proof:
        reservation = Reservation.model_validate(reservation)
        intent, rid = reservation.intent, reservation.reservation_id
        if intent.endpoint_id != self.endpoint_id:
            raise CustodyFault("ENDPOINT_SCOPE_MISMATCH")
        with self.domain.transaction() as db:
            self.domain.authority(db, "endpoint.cancel" if cancel else "endpoint.apply",
                                  intent.principal, intent.effect_id)
            row = db.execute("SELECT * FROM custody_endpoint_reservations WHERE id=?",
                             (rid,)).fetchone()
            identity = (intent.principal, intent.effect_id, intent.payload_digest)
            if row and tuple(row)[1:4] != identity:
                raise CustodyFault("RESERVATION_COLLISION")
            if row and row["status"] == "NOT_EXECUTED" and not cancel:
                raise CustodyFault("RESERVATION_CANCELLED")
            done = db.execute("SELECT digest FROM custody_endpoint_effects "
                              "WHERE principal=? AND effect=?", identity[:2]).fetchone()
            if done and done["digest"] != intent.payload_digest:
                raise CustodyFault("INTENT_COLLISION")
            outcome = "COMMITTED" if done or not cancel else "NOT_EXECUTED"
            if not cancel:
                db.execute("INSERT OR IGNORE INTO custody_endpoint_effects VALUES(?,?,?)", identity)
            db.execute("INSERT OR IGNORE INTO custody_endpoint_reservations VALUES(?,?,?,?,?)",
                       (rid, *identity, outcome))
            proof = Proof(intent=intent, reservation_id=rid, endpoint_id=self.endpoint_id,
                          outcome=outcome, signature="0" * 64)
            return proof.model_copy(update={"signature": sign(proof, self.key)})
