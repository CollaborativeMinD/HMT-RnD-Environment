"""Direct and wire rejection preserve the same trusted task/role boundary."""
import asyncio

import pytest
from test_mcp_support import client_for, handoff_payload, make_lane

from hmt_rnd.mcp_surface import LaneSurface


@pytest.mark.parametrize("field,value", [("agent_role", "admin"),
                                         ("task_owned", "different-task")])
def test_handoff_cannot_claim_another_role_or_task(tmp_path, field, value):
    _, binding = make_lane(tmp_path)
    payload = handoff_payload()
    payload["response"][field] = value
    with pytest.raises(PermissionError, match="MCP_HANDOFF_SCOPE_DENIED"):
        LaneSurface(binding).invoke("validate_handoff", {"handoff": payload})
    async def scenario():
        async with client_for(binding, tmp_path) as client:
            result = await client.call_tool("validate_handoff", {"handoff": payload})
            assert result.is_error
    asyncio.run(scenario())


def test_no_implicit_anonymous_launch(tmp_path, monkeypatch):
    from hmt_rnd import mcp_stdio
    monkeypatch.setattr(mcp_stdio.sys, "argv", ["mcp_stdio"])
    with pytest.raises(PermissionError, match="MCP_HOST_BINDING_REQUIRED"):
        mcp_stdio.main()


def test_direct_argument_bounds_and_closed_schema(tmp_path):
    _, binding = make_lane(tmp_path)
    surface = LaneSurface(binding)
    with pytest.raises(ValueError, match="MCP_ARGUMENT_BOUND"):
        surface.invoke("validate_handoff", {"handoff": {"large": "x" * 65536}})
    with pytest.raises(ValueError):
        surface.invoke("inspect_context", {"principal": "admin"})
