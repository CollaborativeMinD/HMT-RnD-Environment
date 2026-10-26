"""Cross-scope, exact temporal, schema, and transport-parity counterexamples."""
from pathlib import Path

import pytest
from pydantic import ValidationError
from test_host_tracer import fixture_store

from hmt_rnd.host_admission import admit, admit_wire
from hmt_rnd.host_models import Assignment, Clock


@pytest.mark.parametrize("field,value", [("principal", "mallory"), ("role", "reader"),
                         ("lane", "OPS"), ("stage", "B2"), ("credential", "wrong")])
def test_trusted_identity_must_match_entire_grant(tmp_path: Path, field: str, value: str) -> None:
    store, identity, request = fixture_store(tmp_path / "host.sqlite")
    with pytest.raises(PermissionError):
        admit(store, identity.model_copy(update={field: value}), request, Clock(now=10.0))


@pytest.mark.parametrize("field,value", [("revision", 2), ("operation", "write"),
                         ("destination", "https://forbidden.invalid"), ("root", "/")])
def test_request_scope_cannot_expand(tmp_path: Path, field: str, value: object) -> None:
    store, identity, request = fixture_store(tmp_path / "host.sqlite")
    with pytest.raises(PermissionError):
        admit(store, identity, request.model_copy(update={field: value}), Clock(now=10.0))


def test_direct_and_wire_share_admission_and_unknown_fields_fail(tmp_path: Path) -> None:
    store, identity, request = fixture_store(tmp_path / "host.sqlite")
    assert admit(store, identity, request, Clock(now=10.0)) == admit_wire(
        store, identity, request.model_dump_json(), Clock(now=10.0))
    with pytest.raises(ValidationError):
        admit_wire(store, identity, request.model_dump_json()[:-1] + ',"principal":"mallory"}',
                   Clock(now=10.0))
    with pytest.raises(ValueError, match="HOST_INPUT_BOUND"):
        admit_wire(store, identity, " " * 65537, Clock(now=10.0))


@pytest.mark.parametrize("now,uncertainty", [(90.0, 0.0), (89.0, 1.0), (0.5, 0.0)])
def test_exclusive_expiry_and_clock_uncertainty(tmp_path: Path, now: float,
                                               uncertainty: float) -> None:
    store, identity, request = fixture_store(tmp_path / "host.sqlite")
    with pytest.raises(PermissionError):
        admit(store, identity, request, Clock(now=now, uncertainty=uncertainty))


def test_revision_policy_and_clock_changes_invalidate(tmp_path: Path) -> None:
    store, identity, request = fixture_store(tmp_path / "host.sqlite")
    admit(store, identity, request, Clock(now=20.0))
    with pytest.raises(PermissionError, match="HOST_CLOCK_ROLLBACK"):
        admit(store, identity, request, Clock(now=19.0))
    store.set_policy("policy-2")
    with pytest.raises(PermissionError, match="HOST_POLICY_STALE"):
        admit(store, identity, request, Clock(now=21.0))
    store.assign(Assignment(task_id="task-1", principal="alice", revision=2))
    with pytest.raises(PermissionError, match="HOST_TASK_REVISION_DENIED"):
        admit(store, identity, request, Clock(now=22.0))
