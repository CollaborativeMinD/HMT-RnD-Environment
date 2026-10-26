"""Standalone reference-derived custody with host dependencies, never source imports."""
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from .custody_database import Authority, CustodyFault, Domain
from .custody_models import Intent, Proof, Reservation
from .custody_operations import reserve, stage
from .custody_reconcile import reconcile


class CustodyStore:
    def __init__(self, path: Path, authority: Authority,
                 endpoint_keys: Mapping[str, bytes]) -> None:
        if any(len(key) < 32 for key in endpoint_keys.values()):
            raise CustodyFault("ENDPOINT_KEY_INVALID")
        self.domain = Domain(path, authority)
        self.endpoint_keys = MappingProxyType(dict(endpoint_keys))

    def stage(self, intent: Intent) -> None:
        stage(self.domain, intent)

    def reserve(self, principal: str, effect_id: str) -> Reservation:
        return reserve(self.domain, principal, effect_id)

    def reconcile(self, proof: Proof) -> str:
        return reconcile(self.domain, proof, self.endpoint_keys)

    def status(self, principal: str, effect_id: str) -> str:
        with self.domain.transaction() as db:
            self.domain.authority(db, "custody.inspect", principal, effect_id)
            row = db.execute("SELECT status FROM custody_intents WHERE principal=? AND effect=?",
                             (principal, effect_id)).fetchone()
            if row is None:
                raise CustodyFault("EFFECT_UNKNOWN")
            return str(row["status"])
