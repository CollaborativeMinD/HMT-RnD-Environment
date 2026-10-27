"""Absolute identities survive fresh surface/process construction in either cwd."""
import asyncio
import hashlib
import sys

import pytest
from mcp import Client, StdioServerParameters
from test_launch_identity_observer import PROJECT, direct, export
from test_launch_identity_support import database_rows, marker_rows, setup, snapshot


async def invoke(config, root, cwd):
    params = StdioServerParameters(command=sys.executable,
        args=[str(PROJECT / "tests/launch_identity_worker.py"), str(root / "stores"),
              str(config), str(root / "native")],
        env={"PYTHONPATH": str(PROJECT / "src")}, cwd=cwd)
    async with Client(params, read_timeout_seconds=10) as client:
        result = await client.call_tool("inspect_context", {})
        return {"denied": result.is_error, "result": result.structured_content,
                "content": [item.model_dump(mode="json") for item in result.content]}


@pytest.mark.parametrize("transport", ["direct", "mcp"])
@pytest.mark.parametrize("revoked", [False, True], ids=["active", "revoked"])
def test_absolute_restart_control(tmp_path, monkeypatch, transport, revoked):
    raw, _, config, authority, alternate = setup(tmp_path, revoked=revoked)
    paths = [authority / "host.sqlite", alternate / "host.sqlite"]
    before, encoded, observations = [snapshot(p) for p in paths], config.read_bytes(), []
    for cwd in (authority, alternate):
        if transport == "direct":
            with monkeypatch.context() as scoped:
                observations.append(direct(scoped, config, tmp_path, cwd))
        else:
            observations.append(asyncio.run(invoke(config, tmp_path, cwd)))
    after = [snapshot(p) for p in paths]
    receipts = [database_rows(p) for p in paths]
    export(tmp_path, f"absolute-{transport}-{revoked}", dict(raw=raw,
        config_sha256=hashlib.sha256(encoded).hexdigest(), observations=observations,
        native=marker_rows(tmp_path / "native"), stores=marker_rows(tmp_path / "stores"),
        before=before, after=after, receipts=receipts))
    assert config.read_bytes() == encoded
    assert all(item["denied"] == revoked for item in observations)
    assert marker_rows(tmp_path / "stores") == [str(paths[0])] * 2
    assert len(marker_rows(tmp_path / "native")) == (0 if revoked else 2)
    assert [len(rows) for rows in receipts] == ([0, 0] if revoked else [2, 0])
    assert after[1] == before[1]
    if revoked:
        assert after == before
    else:
        assert observations[0]["result"] == observations[1]["result"]
