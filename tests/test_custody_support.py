"""New standalone fixture domains; authorization state shares the custody DB."""
import hashlib
import sqlite3
from pathlib import Path

from hmt_rnd.custody_adapter import CustodyStore
from hmt_rnd.custody_database import CustodyFault
from hmt_rnd.custody_endpoint import Endpoint
from hmt_rnd.custody_models import Intent

KEY = hashlib.sha256(b"synthetic-custody-endpoint-key").digest()


def authority(db: sqlite3.Connection, operation: str, principal: str, effect: str) -> None:
    allowed = db.execute("SELECT allowed FROM fixture_authority WHERE principal=?",
                         (principal,)).fetchone()
    if allowed is None or not allowed[0]:
        raise CustodyFault("HOLD")


def prepare(path: Path) -> None:
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE fixture_authority(principal TEXT PRIMARY KEY,allowed INT)")
        db.execute("INSERT INTO fixture_authority VALUES('alice',1)")


def setup(root: Path):
    local_path, remote_path = root / "local.sqlite", root / "endpoint.sqlite"
    prepare(local_path)
    prepare(remote_path)
    store = CustodyStore(local_path, authority, {"endpoint": KEY})
    endpoint = Endpoint(remote_path, "endpoint", KEY, authority)
    intent = Intent(endpoint_id="endpoint", principal="alice",
                    effect_id="effect1", payload_digest="a" * 64)
    store.stage(intent)
    return store, endpoint, intent


def revoke(path: Path) -> None:
    with sqlite3.connect(path, isolation_level=None) as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE fixture_authority SET allowed=0 WHERE principal='alice'")
        db.commit()
