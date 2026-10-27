"""F20 closed descriptor rejects incomplete/unsupported admission metadata."""
import copy

import pytest
from test_inspection_support import fixture
from test_revision_issuance_support import snapshot

from hmt_rnd.inspection_models import InspectionCapability
from hmt_rnd.inspection_surface import InspectionSurface


@pytest.mark.parametrize("field", list(InspectionCapability.model_fields))
def test_missing_required_registration_field_never_changes_host(tmp_path, field):
    store, binding, cap = fixture(tmp_path)
    del cap[field]
    before = snapshot(store)
    with pytest.raises(ValueError):
        InspectionSurface(binding, (cap,), lambda: 20.0)
    assert snapshot(store) == before


@pytest.mark.parametrize("field,value", [("owner", "model"), ("effect_class", "READ"),
    ("implementation", "arbitrary.module.call"), ("resource_profile", "unknown"),
    ("evidence_contract", "unresolved"), ("valid_until", 0.0), ("epoch", "1"),
    ("unknown", "field")])
def test_unsupported_registration_is_not_an_execution_grant(tmp_path, field, value):
    store, binding, cap = fixture(tmp_path)
    cap[field] = value
    before = snapshot(store)
    with pytest.raises(ValueError):
        InspectionSurface(binding, (cap,), lambda: 20.0)
    assert snapshot(store) == before


@pytest.mark.parametrize("section,field,value", [
    ("retry_reconciliation_owner", "automatic_retry", True),
    ("retry_reconciliation_owner", "automatic_retry", 0),
    ("retry_reconciliation_owner", "maximum_attempts", True),
    ("retry_reconciliation_owner", "maximum_attempts", 2),
    ("limits", "input_bytes", 65537), ("limits", "deadline_seconds", 31),
    ("credential_scope_and_data_egress", "external_egress", "ALLOW")])
def test_retry_egress_and_resource_constraints_fail_closed(tmp_path, section, field, value):
    store, binding, cap = fixture(tmp_path)
    cap = copy.deepcopy(cap)
    cap[section][field] = value
    before = snapshot(store)
    with pytest.raises(ValueError):
        InspectionSurface(binding, (cap,), lambda: 20.0)
    assert snapshot(store) == before
