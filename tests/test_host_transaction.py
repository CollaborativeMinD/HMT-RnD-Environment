"""Existing custody transaction can read admission without nested writers."""
import sqlite3
from pathlib import Path

import pytest
from test_host_tracer import fixture_store

from hmt_rnd.host_checks import authorize
from hmt_rnd.host_models import Assignment, Clock


def test_authorize_inside_existing_transaction_is_read_only(tmp_path: Path) -> None:
    store, identity, request = fixture_store(tmp_path / "authority.sqlite")
    with store.transaction() as connection:
        connection.row_factory = sqlite3.Row
        before = connection.total_changes
        assert authorize(connection, identity, request, Clock(now=10.0)).effect_authority == "NONE"
        assert connection.total_changes == before
    with pytest.raises(PermissionError, match="HOST_REVISION_NOT_ADVANCED"):
        store.assign(Assignment(task_id="task-1", principal="mallory", revision=1))


def test_revoke_deletion_restoration_and_matched_control(tmp_path: Path) -> None:
    store, identity, request = fixture_store(tmp_path / "authority.sqlite")
    assert authorize_in_transaction(store, identity, request) is None
    store.revoke("unrelated-principal")
    assert authorize_in_transaction(store, identity, request) is None
    store.revoke("alice")
    with pytest.raises(PermissionError):
        authorize_in_transaction(store, identity, request)
    with store.transaction() as connection:
        body = connection.execute("SELECT body FROM host_grants").fetchone()[0]
    from hmt_rnd.host_models import Grant
    store.grant(Grant.model_validate_json(body))
    assert authorize_in_transaction(store, identity, request) is None


def authorize_in_transaction(store, identity, request) -> None:
    with store.transaction() as connection:
        authorize(connection, identity, request, Clock(now=10.0))


def test_clock_checkpoint_uses_callers_transaction(tmp_path: Path) -> None:
    from hmt_rnd.host_admission import authorize_and_checkpoint
    store, identity, request = fixture_store(tmp_path / "authority.sqlite")
    with store.transaction() as connection:
        authorize_and_checkpoint(connection, identity, request, Clock(now=20.0))
    with store.transaction() as connection:
        with pytest.raises(PermissionError, match="HOST_CLOCK_ROLLBACK"):
            authorize_and_checkpoint(connection, identity, request, Clock(now=19.0))
