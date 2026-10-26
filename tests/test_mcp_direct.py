"""Registered callable wrappers preserve the same admission and result semantics."""
import asyncio

import pytest
from test_mcp_support import handoff_payload, make_lane

from hmt_rnd.mcp_server import LaneMCP
from hmt_rnd.mcp_surface import LaneSurface


def test_registered_wrappers_and_protocol_dispatch_have_parity(tmp_path):
    store, binding = make_lane(tmp_path)
    server = LaneMCP(LaneSurface(binding))
    context = server.inspect_context()
    handoff = handoff_payload()
    evaluated = server.validate_handoff(handoff)
    async def scenario():
        tools = await server.list_tools()
        assert {t.name for t in tools} == {"inspect_context", "validate_handoff"}
        assert (await server.call_tool("inspect_context", {})).structured_content == context
        reply = await server.call_tool("validate_handoff", {"handoff": handoff})
        assert reply.structured_content == evaluated
        assert evaluated["acceptance_granted"] is False
        store.revoke(binding.identity.principal)
        assert await server.list_tools() == []
    asyncio.run(scenario())
    with pytest.raises(PermissionError, match="HOST_GRANT_DENIED"):
        server.inspect_context()
    with pytest.raises(PermissionError, match="HOST_GRANT_DENIED"):
        server.validate_handoff(handoff)


def test_unknown_direct_operation_is_never_an_admin_route(tmp_path):
    _, binding = make_lane(tmp_path)
    with pytest.raises(PermissionError, match="MCP_OPERATION_NOT_EXPOSED"):
        LaneSurface(binding).invoke("custody.reconcile", {})


def test_binding_policy_cannot_silently_follow_new_authority(tmp_path):
    _, binding = make_lane(tmp_path)
    binding = binding.model_copy(update={"policy": "obsolete-launch-policy"})
    with pytest.raises(PermissionError, match="MCP_POLICY_BINDING_STALE"):
        LaneSurface(binding).invoke("inspect_context", {})


@pytest.mark.parametrize("field,value", [("implementation", "x" * 4097),
                                         ("artifact_refs", ["x"] * 65)])
def test_direct_handoff_is_bounded_before_evaluation(tmp_path, field, value):
    _, binding = make_lane(tmp_path)
    handoff = handoff_payload()
    handoff["response"][field] = value
    with pytest.raises(ValueError):
        LaneMCP(LaneSurface(binding)).validate_handoff(handoff)
