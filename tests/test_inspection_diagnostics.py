"""Receipt diagnostics check integrity; bounds and projection remain distinct."""
import json

import pytest
from test_inspection_observer import receipts
from test_inspection_support import fixture, surface

from hmt_rnd.inspection_receipts import InspectionReceipt, read
from hmt_rnd.inspection_surface import InspectionSurface
from hmt_rnd.lane_queries import receipt_digest


@pytest.mark.parametrize("fault", ["missing", "digest", "identity", "result"])
def test_receipt_corruption_or_absence_is_never_accepted(tmp_path, fault):
    store, binding, cap = fixture(tmp_path)
    target = surface(binding, (cap,))
    target.invoke("inspect_context", {})
    call_id, body, digest = receipts(store)[0]
    if fault == "missing":
        with pytest.raises(PermissionError, match="CAP_RECEIPT_MISSING"):
            read(store, "not-issued")
        return
    with store.transaction() as db:
        db.execute("DROP TRIGGER inspection_no_UPDATE")
        data = json.loads(body)
        if fault == "identity":
            data["call_id"] = "another-call"
            digest = receipt_digest(data)
        elif fault == "result":
            data["result_sha256"] = "0" * 64
            digest = receipt_digest(data)
        else:
            digest = "0" * 64
        db.execute("UPDATE host_inspection_receipts SET body=?,digest=? WHERE id=?",
                   (json.dumps(data), digest, call_id))
    with pytest.raises((PermissionError, ValueError)):
        read(store, call_id)


@pytest.mark.parametrize("entries", [17, 1])
def test_registration_count_and_bytes_are_bounded(tmp_path, entries):
    store, binding, cap = fixture(tmp_path)
    if entries == 1:
        cap["evidence_contract"] = "x" * 65536
    with pytest.raises(ValueError, match="CAP_REGISTRATION_BOUND"):
        InspectionSurface(binding, tuple(cap for _ in range(entries)), lambda: 20.0)


def test_receipt_model_rejects_a_self_inconsistent_result(tmp_path):
    store, binding, cap = fixture(tmp_path)
    surface(binding, (cap,)).invoke("inspect_context", {})
    body = json.loads(receipts(store)[0][1])
    body["result_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="CAP_RECEIPT_RESULT_IDENTITY"):
        InspectionReceipt.model_validate(body)
