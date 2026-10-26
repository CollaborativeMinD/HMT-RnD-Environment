"""Trusted provisioning must not silently replace authority or task history."""
import pytest

from hmt_rnd.host_models import Assignment, Grant
from hmt_rnd.host_store import HostStore


def test_policy_collision_and_invalid_policy_do_not_reinitialize(tmp_path):
    path = tmp_path / "host.sqlite"
    host = HostStore.create(path, "original")
    with pytest.raises(PermissionError, match="HOST_POLICY_COLLISION"):
        HostStore.create(path, "different")
    with pytest.raises(ValueError, match="HOST_POLICY_INVALID"):
        HostStore.create(path, "")
    with pytest.raises(ValueError, match="HOST_POLICY_INVALID"):
        host.set_policy("")


def test_unknown_store_and_nonadvancing_revision_are_denied(tmp_path):
    with pytest.raises(PermissionError, match="HOST_STORE_UNBOUND"):
        HostStore(tmp_path / "missing.sqlite")
    host = HostStore.create(tmp_path / "host.sqlite", "p1")
    task = Assignment(task_id="t1", principal="alice", revision=2)
    host.assign(task)
    with pytest.raises(PermissionError, match="HOST_REVISION_NOT_ADVANCED"):
        host.assign(task)


def test_empty_grant_interval_does_not_create_authority(tmp_path):
    host = HostStore.create(tmp_path / "host.sqlite", "p1")
    grant = Grant(principal="alice", role="builder", lane="Build", stage="B3",
                  credential="cred1", task_id="t1", operation="inspect", root=str(tmp_path),
                  destination="local", policy="p1", epoch=1, not_before=20.0,
                  expires=10.0, evidence_expires=30.0)
    with pytest.raises(PermissionError, match="HOST_GRANT_INTERVAL"):
        host.grant(grant)
    with host.transaction() as connection:
        assert connection.execute("SELECT count(*) FROM host_grants").fetchone()[0] == 0
