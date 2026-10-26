"""Host launch data cannot bypass finite read or regular-file ownership checks."""
import io
import os

import pytest
from test_mcp_support import make_lane

from hmt_rnd import mcp_stdio
from hmt_rnd.mcp_framing import BoundedInput


def test_binding_body_bound_precedes_json_validation(tmp_path):
    target = tmp_path / "oversized.json"
    target.write_bytes(b" " * 65537)
    with pytest.raises(ValueError, match="MCP_BINDING_BOUND"):
        mcp_stdio.load_binding(target)


def test_named_pipe_is_not_a_launch_binding(tmp_path):
    target = tmp_path / "launch.fifo"
    os.mkfifo(target)
    with pytest.raises(PermissionError, match="MCP_UNTRUSTED_LAUNCH_BINDING"):
        mcp_stdio.load_binding(target)


def test_different_server_owner_cannot_use_launch_binding(tmp_path, monkeypatch):
    _, binding = make_lane(tmp_path)
    target = tmp_path / "launch.json"
    target.write_text(binding.model_dump_json())
    different_owner = target.stat().st_uid + 1
    monkeypatch.setattr(mcp_stdio.os, "geteuid", lambda: different_owner)
    with pytest.raises(PermissionError, match="MCP_UNTRUSTED_LAUNCH_BINDING"):
        mcp_stdio.load_binding(target)


def test_stdio_input_is_readable_and_utf8_is_not_rewritten():
    source = BoundedInput(io.BytesIO(b"{}\n"))
    assert source.readable()
    assert source.readline() == "{}\n"
    with pytest.raises(UnicodeDecodeError):
        BoundedInput(io.BytesIO(b"\xff\n")).readline()
