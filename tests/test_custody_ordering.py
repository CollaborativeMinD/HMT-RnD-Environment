"""Actual SQLite lock fences a host revoke at the reserve authorization cut point."""
import sqlite3

import pytest
from test_custody_support import KEY, authority, revoke, setup

from hmt_rnd.custody_adapter import CustodyStore
from hmt_rnd.custody_database import CustodyFault


def test_revoke_serializes_after_admitted_reservation(tmp_path):
    original, _, _ = setup(tmp_path)
    observations = []
    def check(db, operation, principal, effect):
        authority(db, operation, principal, effect)
        if operation == "custody.reserve":
            with sqlite3.connect(original.domain.path, timeout=0) as other:
                with pytest.raises(sqlite3.OperationalError, match="database is locked"):
                    other.execute("BEGIN IMMEDIATE")
            observations.append("revoke-writer-fenced")
    store = CustodyStore(original.domain.path, check, {"endpoint": KEY})
    reserved = store.reserve("alice", "effect1")
    assert reserved.status == "OUTCOME_UNCERTAIN"
    assert observations == ["revoke-writer-fenced"]
    revoke(store.domain.path)
    with pytest.raises(CustodyFault, match="HOLD"):
        store.reserve("alice", "effect1")
