"""Invocation bounds and stale source/schema metadata fail before native dispatch."""
import pytest
from test_inspection_observer import dispatches, watch
from test_inspection_support import fixture, surface
from test_revision_issuance_support import snapshot

from hmt_rnd import inspection_binding


@pytest.mark.parametrize("fault", ["source_set", "output_schema", "future", "source_total",
                                  "source_file", "argument", "oversize", "hidden", "egress"])
def test_invocation_boundaries_preserve_zero_dispatch(tmp_path, monkeypatch, fault):
    store, binding, cap = fixture(tmp_path)
    arguments, operation = {}, "inspect_context"
    if fault == "source_set":
        cap["source_pins"].pop("host_schema.py")
    elif fault == "output_schema":
        cap["output_schema_pin"] = "0" * 64
    elif fault == "future":
        cap["valid_from"] = 21.0
    elif fault == "source_total":
        cap["limits"]["source_total_bytes"] = 1
    elif fault == "source_file":
        cap["limits"]["source_file_bytes"] = 1
    elif fault in {"argument", "oversize"}:
        arguments = {"principal": "forged" if fault == "argument" else "x" * 65536}
    elif fault == "hidden":
        operation = "validate_handoff"
    else:
        binding = binding.model_copy(update={"destination": "remote"})
        from hmt_rnd.lane_queries import receipt_digest
        cap["binding_sha256"] = receipt_digest(binding.model_dump(mode="json"))
    target = surface(binding, (cap,))
    watch(monkeypatch, tmp_path / "native.jsonl")
    before = snapshot(store)
    with pytest.raises((PermissionError, ValueError)):
        target.invoke(operation, arguments)
    assert dispatches(tmp_path / "native.jsonl") == [] and snapshot(store) == before


def test_missing_source_is_not_an_optional_provider_fallback(tmp_path, monkeypatch):
    store, binding, cap = fixture(tmp_path)
    target = surface(binding, (cap,))
    watch(monkeypatch, tmp_path / "native.jsonl")
    before = snapshot(store)

    def missing(*args, **kwargs):
        raise PermissionError("CAP_SOURCE_UNAVAILABLE")

    monkeypatch.setattr(inspection_binding, "read_regular", missing)
    assert target.visible() == ()
    with pytest.raises(PermissionError, match="CAP_SOURCE_UNAVAILABLE"):
        target.invoke("inspect_context", {})
    assert not dispatches(tmp_path / "native.jsonl") and snapshot(store) == before
