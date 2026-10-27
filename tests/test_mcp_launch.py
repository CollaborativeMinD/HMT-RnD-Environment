"""Configuration identity follows one opened descriptor, not stat/open paths."""
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_mcp_support import make_lane

from hmt_rnd import mcp_stdio
from hmt_rnd.mcp_framing import BoundedInput


def test_symlink_binding_is_rejected(tmp_path):
    _, binding = make_lane(tmp_path)
    target = tmp_path / "real.json"
    target.write_text(binding.model_dump_json())
    link = tmp_path / "symlink.json"
    link.symlink_to(target)
    with pytest.raises(OSError):
        mcp_stdio.load_binding(link)


def test_path_replacement_cannot_swap_opened_binding(tmp_path, monkeypatch):
    _, binding = make_lane(tmp_path)
    target = tmp_path / "launch.json"
    target.write_text(binding.model_dump_json())
    replacement = tmp_path / "replacement.json"
    replacement.write_text('{"forged":true}')
    original_open = os.open
    def replace_after_open(path, flags):
        descriptor = original_open(path, flags)
        replacement.replace(target)
        return descriptor
    monkeypatch.setattr(mcp_stdio.os, "open", replace_after_open)
    assert mcp_stdio.load_binding(target) == binding


def test_group_writable_binding_is_rejected(tmp_path):
    _, binding = make_lane(tmp_path)
    target = tmp_path / "launch.json"
    target.write_text(binding.model_dump_json())
    target.chmod(0o620)
    with pytest.raises(PermissionError, match="MCP_UNTRUSTED_LAUNCH_BINDING"):
        mcp_stdio.load_binding(target)


def test_frame_is_bounded_before_json_parse():
    assert BoundedInput(io.BytesIO(b"{}\n")).readline() == "{}\n"
    with pytest.raises(ValueError, match="MCP_FRAME_BOUND"):
        BoundedInput(io.BytesIO(b"x" * 65537)).readline()


def test_oversized_wire_frame_closes_real_server(tmp_path):
    _, binding = make_lane(tmp_path)
    launch = tmp_path / "launch.json"
    launch.write_text(binding.model_dump_json())
    root = Path(__file__).resolve().parents[1]
    command = [sys.executable, "-m", "hmt_rnd.mcp_stdio", str(launch)]
    result = subprocess.run(command, input=b"x" * 65537 + b"\n", capture_output=True,
                            timeout=5, cwd=root,
                            env={**os.environ, "PYTHONPATH": str(root / "src")})
    assert result.returncode != 0 and b"MCP_FRAME_BOUND" in result.stderr
