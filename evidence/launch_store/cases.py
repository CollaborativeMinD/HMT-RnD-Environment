"""Expected denial contract; two baseline failures reproduce the binding seam."""
import asyncio
import hashlib
import json
import sys
from pathlib import Path

import pytest
from mcp import Client, StdioServerParameters
from support import markers, rows, setup, snapshot
from test_inspection_observer import watch

from hmt_rnd.inspection_surface import InspectionSurface

PROJECT = Path(__file__).resolve().parents[2]


async def protocol(config, marker, cwd):
    params = StdioServerParameters(command=sys.executable,
        args=[str(PROJECT / "tests/inspection_worker.py"), str(config), str(marker)],
        env={"PYTHONPATH": str(PROJECT / "src")}, cwd=cwd)
    async with Client(params, read_timeout_seconds=10) as client:
        result = await client.call_tool("inspect_context", {})
        return {"denied": result.is_error, "structured_content": result.structured_content,
                "content": [item.model_dump(mode="json") for item in result.content]}


@pytest.mark.parametrize("transport", ["direct", "mcp"])
@pytest.mark.parametrize("relative", [False, True], ids=["absolute", "relative"])
@pytest.mark.parametrize("cwd_name", ["authority", "alternate"])
def test_revoked_launch_cannot_select_other_authority(tmp_path, monkeypatch,
                                                     transport, relative, cwd_name):
    binding, cap, config, authority, alternate = setup(tmp_path, relative)
    stores = [authority / "host.sqlite", alternate / "host.sqlite"]
    before = [snapshot(path) for path in stores]
    config_bytes = config.read_bytes()
    marker = tmp_path / "native.jsonl"
    cwd = authority if cwd_name == "authority" else alternate
    if transport == "mcp":
        origin = asyncio.run(protocol(config, marker, authority))
        observed = asyncio.run(protocol(config, marker, cwd))
    else:
        watch(monkeypatch, marker)
        monkeypatch.chdir(cwd)
        monkeypatch.chdir(authority)
        origin_surface = InspectionSurface(binding, (cap,), lambda: 20.0)
        with pytest.raises(PermissionError):
            origin_surface.invoke("inspect_context", {})
        origin = {"denied": True, "store": str(origin_surface.store.path)}
        monkeypatch.chdir(cwd)
        surface = InspectionSurface(binding, (cap,), lambda: 20.0)
        try:
            observed = {"denied": False, "result": surface.invoke("inspect_context", {})}
        except PermissionError as error:
            observed = {"denied": True, "error": str(error)}
    evidence = dict(transport=transport, relative=relative, cwd=str(cwd),
        config_sha256=hashlib.sha256(config_bytes).hexdigest(),
        config=json.loads(config_bytes), origin=origin, observed=observed,
        native_dispatches=markers(marker), receipts=[rows(path) for path in stores],
        before=before, after=[snapshot(path) for path in stores])
    output = PROJECT / "evidence/launch_store" / f"{transport}-{relative}-{cwd_name}.json"
    output.write_text(json.dumps(evidence, indent=2) + "\n")
    assert origin["denied"]
    assert config.read_bytes() == config_bytes
    assert observed["denied"], "same launch selected alternate authority after cwd change"
    assert markers(marker) == []
    assert all(not rows(path) for path in stores)
