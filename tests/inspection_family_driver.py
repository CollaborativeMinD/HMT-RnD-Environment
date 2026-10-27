"""One causal arm: binding scope and canonical host authority are distinct edges."""
import json
import sys
from pathlib import Path

import pytest
from test_inspection_observer import dispatches, receipts, watch
from test_inspection_support import fixture, surface
from test_revision_issuance_support import snapshot


def main(root, arm):
    root.mkdir()
    store, binding, cap = fixture(root)
    forged = binding.model_copy(update={"identity": binding.identity.model_copy(
        update={"principal": "not-assigned"})})
    target = surface(forged, (cap,))
    before = snapshot(store)
    with pytest.MonkeyPatch.context() as patch:
        watch(patch, root / "native.jsonl")
        result, error = None, None
        try:
            result = target.invoke("inspect_context", {})
        except PermissionError as failure:
            error = str(failure)
    calls = dispatches(root / "native.jsonl")
    observed = {"arm": arm, "error": error, "result": result,
                "native_dispatches": len(calls), "receipt_count": len(receipts(store)),
                "tables_unchanged": snapshot(store) == before,
                "limits": "Controlled faulty source overlays; not permission for real execution."}
    print(json.dumps(observed))
    if arm == "alternate_off":
        assert error is None and len(calls) == 1 and len(receipts(store)) == 1
        assert result["principal"] == "not-assigned"
    else:
        expected = "HOST_GRANT_DENIED" if arm in {"delete", "alternate_on"} else "CAP_SCOPE_STALE"
        assert error == expected and not calls and not receipts(store)
        assert snapshot(store) == before


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2])
