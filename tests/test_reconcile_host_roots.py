"""RC-HOST-01: a working-directory change must not enlarge granted roots."""
import json

import pytest
from pydantic import ValidationError
from test_host_tracer import fixture_store

from hmt_rnd.host_admission import admit
from hmt_rnd.host_models import Clock, Grant
from hmt_rnd.host_store import HostStore


def stored_grant(store):
    with store.transaction() as connection:
        return json.loads(connection.execute("SELECT body FROM host_grants").fetchone()[0])


@pytest.mark.parametrize("root", [".", "project", "../sibling"])
def test_relative_grant_rejected_before_provision(tmp_path, root):
    store, _, _ = fixture_store(tmp_path / "host.sqlite")
    body = stored_grant(store)
    body["root"] = root
    with pytest.raises(ValidationError, match="HOST_GRANT_ROOT_NOT_ABSOLUTE"):
        store.grant(Grant.model_validate(body))
    assert stored_grant(store)["root"] == str(tmp_path)


def test_legacy_relative_grant_cannot_expand_after_restart(tmp_path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    sibling = tmp_path / "sibling"
    sibling.mkdir()
    monkeypatch.chdir(project)
    store, identity, request = fixture_store(project / "host.sqlite")
    body = stored_grant(store)
    body["root"] = "."
    with store.transaction() as connection:
        connection.execute("UPDATE host_grants SET body=?", (json.dumps(body),))
    monkeypatch.chdir(tmp_path)
    request = request.model_copy(update={"root": str(sibling)})
    with pytest.raises(ValidationError, match="HOST_GRANT_ROOT_NOT_ABSOLUTE"):
        admit(HostStore(store.path), identity, request, Clock(now=10.0))


def test_absolute_grant_preserves_scope_across_restart(tmp_path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    store, identity, request = fixture_store(project / "host.sqlite")
    monkeypatch.chdir(tmp_path)
    restarted = HostStore(store.path)
    assert admit(restarted, identity, request, Clock(now=10.0)).effect_authority == "NONE"
    with pytest.raises(PermissionError, match="HOST_ROOT_DENIED"):
        admit(restarted, identity, request.model_copy(update={"root": str(tmp_path)}),
              Clock(now=11.0))
