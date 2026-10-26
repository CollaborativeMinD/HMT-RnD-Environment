"""Configuration and storage boundary failures cannot authorize custody effects."""
import sqlite3

import pytest
from test_custody_support import KEY, authority, setup

from hmt_rnd.custody_adapter import CustodyStore
from hmt_rnd.custody_database import CustodyFault
from hmt_rnd.custody_endpoint import Endpoint
from hmt_rnd.custody_signing import sign


def test_short_trust_keys_rejected_at_all_entrypoints(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    proof = endpoint.apply(store.reserve("alice", "effect1"))
    with pytest.raises(CustodyFault, match="ENDPOINT_KEY_INVALID"):
        CustodyStore(tmp_path / "bad-store.sqlite", authority, {"endpoint": b"short"})
    with pytest.raises(CustodyFault, match="ENDPOINT_KEY_INVALID"):
        Endpoint(tmp_path / "bad-endpoint.sqlite", "endpoint", b"short", authority)
    with pytest.raises(CustodyFault, match="ENDPOINT_KEY_INVALID"):
        sign(proof, b"short")


def test_unknown_effect_and_completed_effect_never_reserve(tmp_path):
    store, endpoint, _ = setup(tmp_path)
    with pytest.raises(CustodyFault, match="EFFECT_UNKNOWN"):
        store.status("alice", "missing")
    with pytest.raises(CustodyFault, match="EFFECT_UNKNOWN"):
        store.reserve("alice", "missing")
    proof = endpoint.apply(store.reserve("alice", "effect1"))
    store.reconcile(proof)
    with pytest.raises(CustodyFault, match="EFFECT_ALREADY_COMMITTED"):
        store.reserve("alice", "effect1")


def test_old_schema_requires_explicit_migration(tmp_path):
    path = tmp_path / "old.sqlite"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE custody_intents(principal TEXT,effect TEXT,digest TEXT,"
                   "status TEXT,reservation TEXT,PRIMARY KEY(principal,effect))")
    with pytest.raises(CustodyFault, match="SCHEMA_REVISION_REQUIRED"):
        CustodyStore(path, authority, {"endpoint": KEY})
