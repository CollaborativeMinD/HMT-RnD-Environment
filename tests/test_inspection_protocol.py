"""Real stdio parity and independent native-dispatch/result/receipt observations."""
import asyncio
import json

import pytest
from test_inspection_observer import client, dispatches, receipts, watch
from test_inspection_support import changed, fixture, surface
from test_revision_issuance_support import snapshot

from hmt_rnd.inspection_receipts import read
from hmt_rnd.lane_queries import receipt_digest


@pytest.mark.parametrize("fault", [None, "missing", "conflict", "scope", "schema", "source",
                                  "epoch", "expiry", "credential"])
def test_actual_stdio_binding_admission_matches_direct(tmp_path, monkeypatch, fault):
    store, binding, cap = fixture(tmp_path)
    entries = (cap,) if fault is None else changed(cap, fault)
    target = surface(binding, entries)
    watch(monkeypatch, tmp_path / "direct.jsonl")
    before = snapshot(store)
    direct, error = None, None
    try:
        direct = target.invoke("inspect_context", {})
    except PermissionError as failure:
        error = str(failure)

    async def scenario():
        async with client(binding, entries, tmp_path) as session:
            tools = await session.list_tools(cache_mode="refresh")
            assert bool(tools.tools) == (fault is None)
            assert dispatches(tmp_path / "mcp.jsonl") == []
            result = await session.call_tool("inspect_context", {})
            assert result.is_error == (fault is not None)
            if fault is None:
                assert result.structured_content == direct
    asyncio.run(scenario())
    direct_calls = dispatches(tmp_path / "direct.jsonl")
    wire_calls = dispatches(tmp_path / "mcp.jsonl")
    observed = {"fault": fault, "error": error, "direct": direct,
                "direct_dispatches": direct_calls, "MCP_dispatches": wire_calls,
                "receipt_count": len(receipts(store)),
                "tables_unchanged": snapshot(store) == before}
    (tmp_path / "inspection_protocol_observation.json").write_text(json.dumps(observed, indent=2))
    if fault is not None:
        assert error and not direct_calls and not wire_calls and not receipts(store)
        assert snapshot(store) == before
    else:
        assert len(direct_calls) == len(wire_calls) == 1 and len(receipts(store)) == 2
        for call_id, body, digest in receipts(store):
            receipt = read(store, call_id)
            assert receipt.result.model_dump() == direct and receipt.clock_checkpoint == 20.0
            assert receipt.result_sha256 == direct_calls[0]["result_sha256"]
            assert digest == receipt_digest(json.loads(body))
