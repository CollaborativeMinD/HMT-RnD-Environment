"""Same stale-copy mechanism as RC-LAUNCH-STORE-01, before model admission."""
import json
import sqlite3

from test_inspection_support import fixture

from hmt_rnd.host_store import HostStore
from hmt_rnd.inspection_receipts import initialize
from hmt_rnd.lane_queries import receipt_digest


def setup(root, field=None, spelling=None, revoked=True):
    authority, alternate = root / "authority", root / "alternate"
    authority.mkdir()
    alternate.mkdir()
    store, binding, cap = fixture(authority)
    with sqlite3.connect(alternate / "host.sqlite") as target:
        with sqlite3.connect(store.path) as source:
            source.backup(target)
    if revoked:
        store.revoke(binding.identity.principal)
    initialize(store)
    initialize(HostStore(alternate / "host.sqlite"))
    raw = binding.model_dump(mode="json")
    if field:
        raw[field] = spelling
    cap["binding_sha256"] = receipt_digest(raw)
    config = root / "launch.json"
    config.write_text(json.dumps({"binding": raw, "capabilities": [cap]}))
    config.chmod(0o600)
    return raw, cap, config, authority, alternate


def snapshot(path):
    with sqlite3.connect(path) as db:
        return list(db.iterdump())


def marker_rows(path):
    return [] if not path.exists() else path.read_text().splitlines()


def database_rows(path):
    with sqlite3.connect(path) as db:
        return db.execute("SELECT id,body,digest FROM host_inspection_receipts").fetchall()
