"""Six-arm performance experiment: deletion does not imply loss of effect safety."""
import json
import sqlite3

import pytest
from test_custody_index_support import INDEX, observe, seed_history
from test_custody_support import setup


def configure(path, arm):
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO custody_endpoint_reservations VALUES(?,?,?,?,?)",
                   ("matched-end-key", "zz-sentinel", "sentinel", "a" * 64, "NOT_EXECUTED"))
        if arm in {"delete", "alternate_on", "alternate_off", "restore"}:
            db.execute("DROP INDEX " + INDEX)
        if arm == "restore":
            db.execute("CREATE INDEX " + INDEX + " ON "
                       "custody_endpoint_reservations(principal,effect,digest)")
        if arm == "sham":
            db.execute("CREATE INDEX sham_status ON custody_endpoint_reservations(status)")
        if arm in {"alternate_on", "alternate_off"}:
            db.execute("CREATE INDEX alternate_identity ON "
                       "custody_endpoint_reservations(principal,effect,digest)")
        if arm == "alternate_off":
            db.execute("DROP INDEX alternate_identity")


@pytest.mark.parametrize("arm", ["intact", "delete", "restore", "sham",
                                "alternate_on", "alternate_off"])
@pytest.mark.parametrize("operation", ["apply", "lookup_or_cancel"])
def test_index_dependency_with_compensating_path(tmp_path, monkeypatch, arm, operation):
    observations = []
    for count in [0, 10000]:
        root = tmp_path / str(count)
        root.mkdir()
        store, endpoint, _ = setup(root)
        reservation = store.reserve("alice", "effect1")
        seed_history(endpoint.domain.path, count)
        configure(endpoint.domain.path, arm)
        proof, observed = observe(endpoint, operation, reservation, monkeypatch)
        expected = "COMMITTED" if operation == "apply" else "NOT_EXECUTED"
        assert proof.outcome == expected and store.reconcile(proof) == expected
        observations.append({"count": count, "fixed_later_key_sentinels": 1,
                             "outcome": proof.outcome, **observed})
    (tmp_path / "family_observation.json").write_text(json.dumps(
        {"arm": arm, "operation": operation, "observations": observations}, indent=2) + "\n")
    indexed = arm not in {"delete", "alternate_off"}
    assert all(("SEARCH" in row["plan"][0]) == indexed for row in observations)
    delta = observations[1]["lookup_vm_steps"] - observations[0]["lookup_vm_steps"]
    assert delta == 0 if indexed else delta >= 10000
