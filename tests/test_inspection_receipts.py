"""Native result, independent dispatch and atomic same-host receipt are coupled."""
import json
import sqlite3

import pytest
from test_inspection_observer import dispatches, receipts, watch
from test_inspection_support import fixture, surface
from test_revision_issuance_support import snapshot

from hmt_rnd import inspection_execution
from hmt_rnd.inspection_receipts import read
from hmt_rnd.lane_queries import receipt_digest


def test_native_result_and_checkpoint_have_one_immutable_receipt(tmp_path, monkeypatch):
    store, binding, cap = fixture(tmp_path)
    target = surface(binding, (cap,))
    watch(monkeypatch, tmp_path / "native.jsonl")
    before = snapshot(store)
    result = target.invoke("inspect_context", {})
    after = snapshot(store)
    assert len(dispatches(tmp_path / "native.jsonl")) == 1 and len(receipts(store)) == 1
    for name in before:
        if name not in {"host_meta", "host_inspection_receipts"}:
            assert before[name] == after[name]
    call_id, body, digest = receipts(store)[0]
    receipt = read(store, call_id)
    assert receipt.result.model_dump() == result and receipt.external_effects == 0
    assert receipt.arguments_sha256 == receipt_digest({})
    assert receipt.capability_sha256 == receipt_digest(cap)
    assert receipt.clock_checkpoint == after["host_meta"][0][3] == 20.0
    assert digest == receipt_digest(json.loads(body))
    for verb in ("UPDATE", "DELETE"):
        with pytest.raises(sqlite3.IntegrityError, match="INSPECTION_RECEIPT_IMMUTABLE"):
            with store.transaction() as db:
                sql = "UPDATE host_inspection_receipts SET body=body" if verb == "UPDATE" else (
                    "DELETE FROM host_inspection_receipts")
                db.execute(sql)
    assert snapshot(store) == after


def test_receipt_persistence_failure_rolls_back_clock_but_retains_dispatch_observation(
        tmp_path, monkeypatch):
    store, binding, cap = fixture(tmp_path)
    target = surface(binding, (cap,))
    watch(monkeypatch, tmp_path / "native.jsonl")
    before = snapshot(store)

    def fail(db, receipt):
        raise sqlite3.OperationalError("controlled receipt failure")

    monkeypatch.setattr(inspection_execution, "persist", fail)
    with pytest.raises(sqlite3.OperationalError, match="controlled receipt failure"):
        target.invoke("inspect_context", {})
    assert len(dispatches(tmp_path / "native.jsonl")) == 1
    assert snapshot(store) == before
