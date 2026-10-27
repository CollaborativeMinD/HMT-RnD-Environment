"""RC-PATH-01: the original spelling must not select different evaluator bytes."""
import hashlib
import json

import pytest
from test_artifact_fifo_support import observe
from test_lane_tracer import setup_host
from test_path_identity_support import (
    INSIDE,
    OUTSIDE,
    alias_fixture,
    candidate_for,
    gate_for,
    state,
)

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_store import LaneStore


@pytest.mark.parametrize("mode", ["digest", "snapshot"])
def test_parent_component_rejects_native_guarded_identity_split(tmp_path, mode):
    root, alias = alias_fixture(tmp_path)
    native = alias.read_bytes()
    assert native == OUTSIDE
    observed, denial = None, None
    try:
        observed = observe(mode, alias, root, INSIDE)
    except PermissionError as error:
        denial = str(error)
    witness = {"mode": mode, "native_hex": native.hex(),
               "native_sha256": hashlib.sha256(native).hexdigest(),
               "normalized_hex": INSIDE.hex(), "guarded_sha256": observed, "denial": denial}
    (tmp_path / "path_identity_observed.json").write_text(json.dumps(witness))
    print(json.dumps(witness))
    expected = "LANE_ARTIFACT_SCOPE" if mode == "digest" else "LANE_SNAPSHOT_SCOPE"
    assert denial == expected


def test_submission_denies_alias_before_evaluator_and_rolls_back(tmp_path):
    root, alias = alias_fixture(tmp_path)
    host, identity, request = setup_host(root)
    store, evaluated = LaneStore(host), []
    before = state(host)
    receipt, denial = None, None
    try:
        receipt = store.submit(identity, request, candidate_for(alias), lambda: Clock(now=10.0),
                               lambda context: gate_for(context, root, evaluated))
    except PermissionError as error:
        denial = str(error)
    snapshot = None if receipt is None else store.snapshot(receipt.candidate.artifact_sha256).hex()
    witness = {"evaluated_hex": evaluated, "snapshot_hex": snapshot, "denial": denial,
               "receipt_outcome": None if receipt is None else receipt.gate.outcome,
               "before": before, "after": state(host)}
    (tmp_path / "path_identity_observed.json").write_text(json.dumps(witness))
    print(json.dumps(witness))
    assert denial == "LANE_ARTIFACT_SCOPE"
    assert evaluated == [] and state(host) == before
    host.revoke("alice")
    with host.transaction() as db:
        assert db.execute("SELECT revoked FROM host_grants").fetchone()[0] == 1
    with pytest.raises(PermissionError, match="HOST_GRANT_DENIED"):
        LaneStore(host).submit(identity, request, candidate_for(root / "source"),
                               lambda: Clock(now=11.0),
                               lambda context: gate_for(context, root, evaluated))
    assert evaluated == [] and state(host) == before
