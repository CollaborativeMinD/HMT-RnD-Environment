"""Faulty adapters are test-injected; production guards are never changed."""
from pathlib import Path

import pytest
from test_temporal_support import KEY, guard, observed, prepare

from hmt_rnd.custody_adapter import CustodyStore
from hmt_rnd.custody_endpoint import Endpoint
from hmt_rnd.host_store import HostStore

ARMS = (
    ("intact", False, False, False, "STAGED", 0),
    ("delete_local", True, False, False, "OUTCOME_UNCERTAIN", 0),
    ("restore_local", False, False, False, "STAGED", 0),
    ("sham_query", False, False, True, "STAGED", 0),
    ("alternate_on", True, False, False, "OUTCOME_UNCERTAIN", 0),
    ("alternate_off", True, True, False, "OUTCOME_UNCERTAIN", 1),
)


def experiment(root: Path, delete_local: bool, delete_remote: bool, sham: bool) -> dict:
    local, _, intent = prepare(root)
    local.stage(intent)
    HostStore(root / "local.sqlite").revoke("alice")
    HostStore(root / "endpoint.sqlite").revoke("alice")
    local = CustodyStore(root / "local.sqlite", guard(root, delete_reserve=delete_local,
                                                     sham=sham), {"endpoint": KEY})
    endpoint = Endpoint(root / "endpoint.sqlite", "endpoint", KEY,
                        guard(root, delete_all=delete_remote))
    rejection = "NONE"
    try:
        endpoint.apply(local.reserve("alice", "effect1"))
    except PermissionError as error:
        rejection = str(error)
    status, effects = observed(root)
    return {"status": status, "endpoint_effects": effects, "rejection": rejection}


def assert_revoked_safety(result: dict) -> None:
    assert result["status"] == "STAGED", "REVOKED_RESERVATION_OCCURRED"
    assert result["endpoint_effects"] == 0, "REVOKED_ENDPOINT_EFFECT_OCCURRED"


@pytest.mark.parametrize("name,local,remote,sham,status,effects", ARMS,
                         ids=[arm[0] for arm in ARMS])
def test_authority_edge_arm(tmp_path, name, local, remote, sham, status, effects):
    result = experiment(tmp_path, local, remote, sham)
    assert result["status"] == status, (name, result)
    assert result["endpoint_effects"] == effects, (name, result)
    if local:
        with pytest.raises(AssertionError, match="REVOKED_RESERVATION_OCCURRED"):
            assert_revoked_safety(result)
    else:
        assert_revoked_safety(result)
    if remote:
        with pytest.raises(AssertionError):
            assert result["endpoint_effects"] == 0, "REVOKED_ENDPOINT_EFFECT_OCCURRED"


def test_redundancy_does_not_hide_local_guard_dependency(tmp_path):
    results = {}
    for name, local, remote, sham, _, _ in ARMS:
        root = tmp_path / name
        root.mkdir()
        results[name] = experiment(root, local, remote, sham)
    assert results["intact"] == results["restore_local"] == results["sham_query"]
    assert results["delete_local"]["status"] != results["intact"]["status"]
    assert results["delete_local"]["endpoint_effects"] == 0
    assert results["alternate_off"]["endpoint_effects"] == 1
