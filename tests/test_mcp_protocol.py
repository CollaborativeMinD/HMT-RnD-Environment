"""Actual official SDK client/session over spawned stdio, not FastMCP mocks."""
import asyncio

from test_mcp_support import client_for, handoff_payload, make_lane

from hmt_rnd.mcp_surface import LaneSurface


def test_real_stdio_discovery_and_direct_call_parity(tmp_path):
    _, binding = make_lane(tmp_path)
    direct = LaneSurface(binding).invoke("inspect_context", {})
    async def scenario():
        async with client_for(binding, tmp_path) as client:
            tools = await client.list_tools(cache_mode="refresh")
            assert {t.name for t in tools.tools} == {"inspect_context", "validate_handoff"}
            assert all(t.input_schema["additionalProperties"] is False for t in tools.tools)
            handoff = next(t for t in tools.tools if t.name == "validate_handoff")
            assert handoff.input_schema["$defs"]["Handoff"]["additionalProperties"] is False
            context = await client.call_tool("inspect_context", {})
            assert not context.is_error and context.structured_content == direct
            result = await client.call_tool("validate_handoff", {"handoff": handoff_payload()})
            assert not result.is_error
            assert result.structured_content["acceptance_granted"] is False
    asyncio.run(scenario())


def test_revocation_updates_discovery_and_blocks_cached_tool(tmp_path):
    store, binding = make_lane(tmp_path)
    async def scenario():
        async with client_for(binding, tmp_path) as client:
            assert (await client.list_tools(cache_mode="refresh")).tools
            store.revoke(binding.identity.principal)
            assert not (await client.list_tools(cache_mode="refresh")).tools
            result = await client.call_tool("inspect_context", {})
            assert result.is_error
    asyncio.run(scenario())


def test_hidden_and_malformed_tools_fail_over_protocol(tmp_path):
    _, binding = make_lane(tmp_path)
    async def scenario():
        async with client_for(binding, tmp_path) as client:
            for operation, payload in [("custody.reconcile", {}),
                                       ("inspect_context", {"principal": "admin"}),
                                       ("inspect_context", {"admission": "ADMITTED"}),
                                       ("validate_handoff", {"handoff": {"response": {}}})]:
                result = await client.call_tool(operation, payload)
                assert result.is_error, (operation, payload)
    asyncio.run(scenario())
