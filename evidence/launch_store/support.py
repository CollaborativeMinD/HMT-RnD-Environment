"""Synthetic authority stores and observers for RC-LAUNCH-STORE-01."""
import json
import sqlite3

from test_inspection_support import fixture

from hmt_rnd.host_store import HostStore
from hmt_rnd.inspection_receipts import initialize
from hmt_rnd.lane_queries import receipt_digest
from hmt_rnd.mcp_contracts import LaneBinding


def setup(root, relative):
    authority = root / "authority"
    alternate = root / "alternate"
    authority.mkdir()
    alternate.mkdir()
    store, binding, cap = fixture(authority)
    with sqlite3.connect(alternate / "host.sqlite") as target:
        with sqlite3.connect(store.path) as source:
            source.backup(target)
    store.revoke(binding.identity.principal)
    initialize(store)
    initialize(HostStore(alternate / "host.sqlite"))
    payload = binding.model_dump(mode="json")
    if relative:
        payload["store"] = "host.sqlite"
    binding = LaneBinding.model_validate_json(json.dumps(payload))
    cap["binding_sha256"] = receipt_digest(binding.model_dump(mode="json"))
    config = root / "launch.json"
    config.write_text(json.dumps({"binding": binding.model_dump(mode="json"),
                                 "capabilities": [cap]}))
    config.chmod(0o600)
    return binding, cap, config, authority, alternate


def snapshot(path):
    with sqlite3.connect(path) as db:
        return list(db.iterdump())


def rows(path):
    with sqlite3.connect(path) as db:
        present = db.execute("SELECT name FROM sqlite_master WHERE name="
                             "'host_inspection_receipts'").fetchone()
        return [] if not present else db.execute(
            "SELECT id,body,digest FROM host_inspection_receipts").fetchall()


def markers(path):
    return [] if not path.exists() else path.read_text().splitlines()
