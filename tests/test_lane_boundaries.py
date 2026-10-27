"""Missing evaluator, gate tampering, revocation, and immutable denial boundaries."""
import sqlite3
from pathlib import Path

import pytest
from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_models import GateContext, GateResult
from hmt_rnd.lane_store import LaneStore


def test_missing_evaluator_and_revoked_principal_cannot_seal(tmp_path: Path) -> None:
    host, owner, request = setup_host(tmp_path)
    store = LaneStore(host)
    with pytest.raises(PermissionError, match="LANE_EVALUATOR_UNBOUND"):
        store.submit(owner, request, make_candidate(tmp_path), lambda: Clock(now=10.0), None)
    host.revoke("alice")
    with pytest.raises(PermissionError, match="HOST_GRANT_DENIED"):
        store.submit(owner, request, make_candidate(tmp_path),
                     lambda: Clock(now=11.0), execute_gate)


def test_gate_output_must_bind_current_context(tmp_path: Path) -> None:
    host, owner, request = setup_host(tmp_path)

    def wrong_gate(context: GateContext) -> GateResult:
        return execute_gate(context).model_copy(update={"policy": "forged-policy"})

    with pytest.raises(PermissionError, match="LANE_GATE_CONTEXT_MISMATCH"):
        LaneStore(host).submit(owner, request, make_candidate(tmp_path),
                               lambda: Clock(now=10.0), wrong_gate)


def test_denied_receipt_is_immutable_and_never_promotes(tmp_path: Path) -> None:
    host, owner, request = setup_host(tmp_path)
    store = LaneStore(host)

    def deny(context: GateContext) -> GateResult:
        return execute_gate(context).model_copy(update={"outcome": "DENIED",
                                                        "reasons": ("CONTROLLED_FAILURE",)})

    receipt = store.submit(owner, request, make_candidate(tmp_path),
                           lambda: Clock(now=10.0), deny)
    assert receipt.gate.outcome == "DENIED"
    with host.transaction() as db:
        with pytest.raises(sqlite3.IntegrityError, match="IMMUTABLE_LIFECYCLE"):
            db.execute("UPDATE lane_candidates SET body='changed'")
    assert LaneStore(host).receipt("first") == receipt
    _, owner, request = setup_host(tmp_path, "CMAD2")
    with pytest.raises(PermissionError, match="LANE_PREDECESSOR_NOT_CURRENT"):
        store.submit(owner, request, make_candidate(tmp_path, "next", "CMAD2", "first"),
                     lambda: Clock(now=11.0), execute_gate)


def test_expiry_during_evaluator_rolls_back_progression(tmp_path: Path) -> None:
    host, owner, request = setup_host(tmp_path)
    ticks = iter((Clock(now=10.0), Clock(now=90.0)))
    store = LaneStore(host)
    with pytest.raises(PermissionError, match="HOST_LEASE_OR_EVIDENCE_EXPIRED"):
        store.submit(owner, request, make_candidate(tmp_path), lambda: next(ticks), execute_gate)
    with host.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM lane_candidates").fetchone()[0] == 0
