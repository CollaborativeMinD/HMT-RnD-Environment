"""RC-CUSTODY-INDEX-01: principal/effect lookups must not scan unrelated history."""
import json
import sqlite3

import pytest
from test_custody_index_support import INDEX, observe, seed_history, state_digest, table_state
from test_custody_support import KEY, authority, setup

from hmt_rnd.custody_endpoint import Endpoint


@pytest.mark.parametrize("operation", ["apply", "lookup_or_cancel"])
@pytest.mark.parametrize("count", [0, 512, 10000])
@pytest.mark.parametrize("existing", [False, True])
def test_actual_endpoint_lookup_uses_scoped_covering_index(
        tmp_path, monkeypatch, operation, count, existing):
    store, endpoint, _ = setup(tmp_path)
    reservation = store.reserve("alice", "effect1")
    path = endpoint.domain.path
    if existing:
        with sqlite3.connect(path) as db:
            db.execute("DROP INDEX IF EXISTS " + INDEX)
    seed_history(path, count)
    before = table_state(path)
    endpoint = Endpoint(path, "endpoint", KEY, authority)
    after = table_state(path)
    proof, observed = observe(endpoint, operation, reservation, monkeypatch)
    with sqlite3.connect(path) as db:
        columns = [row[2] for row in db.execute("PRAGMA index_info(" + INDEX + ")")]
        retained = db.execute("SELECT count(*) FROM custody_endpoint_reservations").fetchone()[0]
    record = {"count": count, "operation": operation, "existing": existing, **observed,
              "index_columns": columns, "before": state_digest(before),
              "after_provision": state_digest(after), "rows_retained": retained}
    (tmp_path / "index_observation.json").write_text(json.dumps(record, indent=2) + "\n")
    assert before == after
    assert columns == ["principal", "effect", "digest"]
    assert len(observed["plan"]) == 1
    assert "SEARCH" in observed["plan"][0] and INDEX in observed["plan"][0]
    assert "COVERING INDEX" in observed["plan"][0]
    assert retained == count + 4
    expected = "COMMITTED" if operation == "apply" else "NOT_EXECUTED"
    assert proof.outcome == expected
    assert store.reconcile(proof) == expected
    persisted = table_state(path)
    Endpoint(path, "endpoint", KEY, authority)
    assert table_state(path) == persisted
