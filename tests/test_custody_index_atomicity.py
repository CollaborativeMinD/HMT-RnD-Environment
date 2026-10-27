"""Index provisioning shares the existing atomic schema transaction."""
import sqlite3

import pytest
from test_custody_index_support import INDEX, seed_history, table_state
from test_custody_support import KEY, authority, prepare, setup

from hmt_rnd import custody_database
from hmt_rnd.custody_endpoint import Endpoint


def schema(path):
    with sqlite3.connect(path) as db:
        return db.execute("SELECT name,sql FROM sqlite_master ORDER BY name").fetchall()


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("cut", ["after_index", "before_commit"])
def test_failed_provisioning_rolls_back_and_can_restart(tmp_path, monkeypatch, existing, cut):
    path = tmp_path / "endpoint.sqlite"
    if existing:
        _, endpoint, _ = setup(tmp_path)
        path = endpoint.domain.path
        with sqlite3.connect(path) as db:
            db.execute("DROP INDEX " + INDEX)
        seed_history(path, 512)
    else:
        prepare(path)
    before, before_schema = table_state(path), schema(path)

    class Faulted(sqlite3.Connection):
        def execute(self, sql, *args, **kwargs):
            value = super().execute(sql, *args, **kwargs)
            if cut == "after_index" and sql.startswith("CREATE INDEX"):
                raise sqlite3.OperationalError("controlled provisioning cut")
            return value

        def commit(self):
            if cut == "before_commit":
                raise sqlite3.OperationalError("controlled provisioning cut")
            return super().commit()

    original = sqlite3.connect
    with monkeypatch.context() as patch:
        patch.setattr(custody_database.sqlite3, "connect",
                      lambda *a, **kw: original(*a, factory=Faulted, **kw))
        with pytest.raises(sqlite3.OperationalError, match="controlled provisioning cut"):
            Endpoint(path, "endpoint", KEY, authority)
    assert table_state(path) == before and schema(path) == before_schema
    Endpoint(path, "endpoint", KEY, authority)
    if existing:
        assert table_state(path) == before
    with sqlite3.connect(path) as db:
        assert [row[2] for row in db.execute("PRAGMA index_info(" + INDEX + ")")] == [
            "principal", "effect", "digest"]
