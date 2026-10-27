"""Temporal and post-dispatch faults preserve observed execution and roll back state."""
import pytest
from test_inspection_observer import dispatches, watch
from test_inspection_support import fixture
from test_revision_issuance_support import snapshot

from hmt_rnd import mcp_surface
from hmt_rnd.inspection_surface import InspectionSurface


@pytest.mark.parametrize("fault", ["cap_expiry", "grant_expiry", "deadline", "output_bound",
                                  "output_identity", "output_shape", "binding_changed"])
def test_post_dispatch_denial_never_claims_nonexecution(tmp_path, monkeypatch, fault):
    store, binding, cap = fixture(tmp_path)
    now, elapsed = [20.0], [0.0]
    if fault == "grant_expiry":
        cap["valid_until"] = 100.0
    if fault == "output_bound":
        cap["limits"]["output_bytes"] = 1
    target = InspectionSurface(binding, (cap,), lambda: now[0], lambda: elapsed[0])
    watch(monkeypatch, tmp_path / "native.jsonl")
    original = mcp_surface.inspect_context

    def changed(decision, arguments):
        result = original(decision, arguments)
        if fault in {"cap_expiry", "grant_expiry"}:
            now[0] = 80.0 if fault == "cap_expiry" else 90.0
        elif fault == "deadline":
            elapsed[0] = 30.0
        elif fault == "output_identity":
            result["principal"] = "wrong"
        elif fault == "output_shape":
            result["extra"] = "forbidden"
        elif fault == "binding_changed":
            object.__setattr__(target.capabilities[0], "valid_until", 79.0)
        return result

    monkeypatch.setattr(mcp_surface, "inspect_context", changed)
    before = snapshot(store)
    with pytest.raises((PermissionError, ValueError)):
        target.invoke("inspect_context", {})
    assert len(dispatches(tmp_path / "native.jsonl")) == 1
    assert snapshot(store) == before


def test_deadline_expired_before_dispatch_has_no_native_effect(tmp_path, monkeypatch):
    store, binding, cap = fixture(tmp_path)
    ticks = iter([0.0, 30.0])
    target = InspectionSurface(binding, (cap,), lambda: 20.0, lambda: next(ticks))
    watch(monkeypatch, tmp_path / "native.jsonl")
    before = snapshot(store)
    with pytest.raises(PermissionError, match="CAP_DEADLINE_EXCEEDED"):
        target.invoke("inspect_context", {})
    assert not dispatches(tmp_path / "native.jsonl") and snapshot(store) == before
