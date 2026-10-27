"""Shared serialized and in-memory launch validation cannot defer path identity."""
import json
from pathlib import Path

import pytest
from test_inspection_support import fixture
from test_launch_identity_observer import startup
from test_launch_identity_support import setup, snapshot

from hmt_rnd import mcp_surface
from hmt_rnd.inspection_models import InspectionLaunch
from hmt_rnd.mcp_contracts import LaneBinding
from hmt_rnd.mcp_stdio import load_binding


@pytest.mark.parametrize("field", ["store", "root"])
@pytest.mark.parametrize("boundary", ["json", "python", "instance", "loader"])
def test_shared_boundary_rejects_relative(tmp_path, monkeypatch, field, boundary):
    _, binding, _ = fixture(tmp_path)
    raw = binding.model_dump(mode="python")
    raw[field] = Path("relative")
    if boundary == "instance":
        raw["identity"] = binding.identity
    opened = []
    monkeypatch.setattr(mcp_surface, "HostStore", lambda path: opened.append(path))
    with pytest.raises(ValueError, match="MCP_BINDING_PATH_NOT_ABSOLUTE"):
        if boundary == "python":
            LaneBinding.model_validate(raw)
        elif boundary == "json":
            LaneBinding.model_validate_json(json.dumps(raw, default=str))
        elif boundary == "instance":
            mcp_surface.LaneSurface(LaneBinding.model_construct(**raw))
        else:
            launch = tmp_path / "launch.json"
            launch.write_text(json.dumps(raw, default=str))
            launch.chmod(0o600)
            load_binding(launch)
    assert opened == []


@pytest.mark.parametrize("field", ["store", "root"])
@pytest.mark.parametrize("cwd_name", ["authority", "alternate"])
def test_default_entrypoint_rejects_before_protocol(tmp_path, field, cwd_name):
    raw, _, config, authority, alternate = setup(tmp_path, field, "host.sqlite")
    config.write_text(json.dumps(raw))
    paths = [authority / "host.sqlite", alternate / "host.sqlite"]
    before = [snapshot(p) for p in paths]
    observed = startup(config, tmp_path,
                       authority if cwd_name == "authority" else alternate, default=True)
    assert observed["returncode"] != 0
    assert "MCP_BINDING_PATH_NOT_ABSOLUTE" in observed["stderr"]
    assert observed["stdout"] == ""
    assert [snapshot(p) for p in paths] == before


def test_absolute_serialization_does_not_consult_cwd(tmp_path, monkeypatch):
    _, binding, cap = fixture(tmp_path)
    encoded = binding.model_dump_json()
    monkeypatch.chdir(tmp_path.parent)
    restored = LaneBinding.model_validate_json(encoded)
    assert restored.model_dump_json() == encoded
    launch = InspectionLaunch(binding=restored, capabilities=(cap,))
    assert launch.binding.store == binding.store
    assert launch.binding.root == binding.root
