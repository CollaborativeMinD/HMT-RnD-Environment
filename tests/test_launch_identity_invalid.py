"""Invalid serialized store/root identities must fail before opening any store."""
import hashlib

import pytest
from test_launch_identity_observer import direct, export, startup
from test_launch_identity_support import marker_rows, setup, snapshot


@pytest.mark.parametrize("transport", ["direct", "mcp"])
@pytest.mark.parametrize("field", ["store", "root"])
@pytest.mark.parametrize("spelling", ["", ".", "host.sqlite", "../host.sqlite"])
@pytest.mark.parametrize("cwd_name", ["authority", "alternate"])
def test_invalid_identity_zero_store_open(tmp_path, monkeypatch, transport, field,
                                         spelling, cwd_name):
    raw, _, config, authority, alternate = setup(tmp_path, field, spelling)
    paths = [authority / "host.sqlite", alternate / "host.sqlite"]
    before, encoded = [snapshot(p) for p in paths], config.read_bytes()
    cwd = authority if cwd_name == "authority" else alternate
    observed = (direct(monkeypatch, config, tmp_path, cwd) if transport == "direct"
                else startup(config, tmp_path, cwd))
    after = [snapshot(p) for p in paths]
    index = ["", ".", "host.sqlite", "../host.sqlite"].index(spelling)
    name = f"invalid-{transport}-{field}-{index}-{cwd_name}"
    export(tmp_path, name, dict(raw=raw, observed=observed, before=before, after=after,
        config_sha256=hashlib.sha256(encoded).hexdigest(), cwd=str(cwd)))
    if transport == "direct":
        assert observed["denied"]
        assert "MCP_BINDING_PATH_NOT_ABSOLUTE" in observed["error"]
    else:
        assert observed["returncode"] != 0
        assert "MCP_BINDING_PATH_NOT_ABSOLUTE" in observed["stderr"]
    assert config.read_bytes() == encoded
    assert marker_rows(tmp_path / "stores") == []
    assert marker_rows(tmp_path / "native") == []
    assert after == before
