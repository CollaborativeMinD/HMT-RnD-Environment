"""WP-01/WP-08 falsifiers: metadata cannot substitute for bound execution."""
import json

import pytest
from test_inspection_support import changed, fixture, surface
from test_revision_issuance_support import snapshot


@pytest.mark.parametrize("fault", ["missing", "conflict", "scope", "schema", "source",
                                  "epoch", "expiry", "credential"])
def test_unresolved_binding_has_no_dispatch_or_committed_effect(tmp_path, fault):
    store, binding, cap = fixture(tmp_path)
    target = surface(binding, changed(cap, fault))
    before = snapshot(store)
    result, error = None, None
    try:
        result = target.invoke("inspect_context", {})
    except (PermissionError, ValueError) as failure:
        error = str(failure)
    observed = {"fault": fault, "error": error, "native_result": result,
                "tables_unchanged": snapshot(store) == before}
    (tmp_path / "inspection_observation.json").write_text(json.dumps(observed, indent=2))
    assert error is not None and result is None
    assert snapshot(store) == before


def test_native_positive_contract_is_retained(tmp_path):
    store, binding, cap = fixture(tmp_path)
    target = surface(binding, (cap,))
    result = target.invoke("inspect_context", {})
    assert result == {"principal": binding.identity.principal, "task_id": binding.task_id,
                      "task_revision": 1, "operation": "inspect_context", "policy": "policy-1",
                      "epoch": 1, "effect_authority": "NONE"}
