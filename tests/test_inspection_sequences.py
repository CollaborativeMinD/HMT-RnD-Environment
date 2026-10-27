"""Fresh canonical host authority fences cached discovery and forged metadata."""
import asyncio

import pytest
from test_inspection_observer import client, dispatches, receipts, watch
from test_inspection_support import fixture, surface
from test_revision_issuance_support import snapshot

from hmt_rnd.host_models import Assignment
from hmt_rnd.lane_queries import receipt_digest


@pytest.mark.parametrize("change", ["revoke", "revision", "policy"])
def test_current_host_change_denies_cached_direct_and_mcp_call(tmp_path, monkeypatch, change):
    store, binding, cap = fixture(tmp_path)
    target = surface(binding, (cap,))
    watch(monkeypatch, tmp_path / "native.jsonl")

    async def scenario():
        async with client(binding, (cap,), tmp_path) as session:
            assert (await session.list_tools(cache_mode="refresh")).tools
            assert not receipts(store) and not dispatches(tmp_path / "mcp.jsonl")
            if change == "revoke":
                store.revoke(binding.identity.principal)
            elif change == "revision":
                store.assign(Assignment(task_id=binding.task_id,
                    principal=binding.identity.principal, revision=2))
            else:
                store.set_policy("policy-2")
            before = snapshot(store)
            assert (await session.call_tool("inspect_context", {})).is_error
            assert not (await session.list_tools(cache_mode="refresh")).tools
            with pytest.raises(PermissionError):
                target.invoke("inspect_context", {})
            assert snapshot(store) == before
    asyncio.run(scenario())
    assert not receipts(store) and not dispatches(tmp_path / "native.jsonl")
    assert not dispatches(tmp_path / "mcp.jsonl")


def test_self_consistent_descriptor_does_not_grant_a_new_principal_authority(tmp_path, monkeypatch):
    store, binding, cap = fixture(tmp_path)
    forged = binding.model_copy(update={"identity": binding.identity.model_copy(
        update={"principal": "not-assigned"})})
    cap["binding_sha256"] = receipt_digest(forged.model_dump(mode="json"))
    target = surface(forged, (cap,))
    watch(monkeypatch, tmp_path / "native.jsonl")
    before = snapshot(store)
    with pytest.raises(PermissionError, match="HOST_GRANT_DENIED"):
        target.invoke("inspect_context", {})
    assert not dispatches(tmp_path / "native.jsonl") and snapshot(store) == before
