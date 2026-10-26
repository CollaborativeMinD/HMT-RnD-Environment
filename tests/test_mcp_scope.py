"""Immutable launch scope cannot outrun current host grant and revision."""
import asyncio

import pytest
from test_mcp_support import client_for, make_lane

from hmt_rnd.host_models import Assignment


@pytest.mark.parametrize("field,value", [("credential", "forged"), ("stage", "B2"),
                                         ("lane", "OPS"), ("principal", "anonymous")])
def test_mismatched_launch_identity_has_no_tools_or_calls(tmp_path, field, value):
    _, binding = make_lane(tmp_path)
    identity = binding.identity.model_copy(update={field: value})
    binding = binding.model_copy(update={"identity": identity})
    async def scenario():
        async with client_for(binding, tmp_path) as client:
            assert not (await client.list_tools(cache_mode="refresh")).tools
            assert (await client.call_tool("inspect_context", {})).is_error
    asyncio.run(scenario())


@pytest.mark.parametrize("change", ["revision", "policy"])
def test_current_host_change_fences_existing_session(tmp_path, change):
    store, binding = make_lane(tmp_path)
    async def scenario():
        async with client_for(binding, tmp_path) as client:
            assert not (await client.call_tool("inspect_context", {})).is_error
            if change == "revision":
                store.assign(Assignment(task_id="task-1", principal=binding.identity.principal,
                                        revision=2))
            else:
                store.set_policy("policy-2")
            assert not (await client.list_tools(cache_mode="refresh")).tools
            assert (await client.call_tool("inspect_context", {})).is_error
    asyncio.run(scenario())
