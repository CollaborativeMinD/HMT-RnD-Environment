"""Explicit legacy/qualified tracer backends; no runtime fallback is provided."""
import hashlib
import json
import os
from pathlib import Path

from test_mcp_support import make_lane

from hmt_rnd.host_models import Decision, Grant
from hmt_rnd.lane_queries import receipt_digest
from hmt_rnd.mcp_contracts import EmptyArguments
from hmt_rnd.mcp_surface import LaneSurface

SPINE = ("host_admission.py", "host_checks.py", "host_models.py", "host_store.py",
         "host_admin.py", "host_schema.py", "mcp_contracts.py", "mcp_handoff.py", "mcp_surface.py")


def fixture(root):
    store, binding = make_lane(root)
    store.grant(Grant(**binding.identity.model_dump(), task_id=binding.task_id, revision=1,
                      operation="inspect_context", root=str(root), destination="local",
                      policy="policy-1", epoch=1, not_before=1.0, expires=100.0,
                      evidence_expires=90.0))
    package = Path(__file__).parent.parent / "src/hmt_rnd"
    cap = dict(operation_id="inspect_context", owner="Host/IIEA", effect_class="LOCAL_MUTATION",
               implementation="hmt_rnd.mcp_surface.inspect_context",
               binding_sha256=receipt_digest(binding.model_dump(mode="json")), epoch=1,
               source_pins={p: hashlib.sha256((package / p).read_bytes()).hexdigest()
                            for p in SPINE},
               input_schema_pin=receipt_digest(EmptyArguments.model_json_schema()),
               output_schema_pin=receipt_digest(Decision.model_json_schema()),
               credential_scope_and_data_egress={"credential_ref": binding.identity.credential,
                                                "destination": "local", "external_egress": "DENY"},
               retry_reconciliation_owner={"owner": "Host", "maximum_attempts": 1,
                                            "automatic_retry": False, "uncertain": "HOLD"},
               limits={"input_bytes": 65536, "output_bytes": 4096, "source_file_bytes": 65536,
                       "source_total_bytes": 131072, "deadline_seconds": 30},
               valid_from=1.0, valid_until=80.0, resource_profile="LOCAL-CTRL-1",
               evidence_contract="atomic clock checkpoint and immutable native-result receipt")
    return store, binding, cap


def surface(binding, entries):
    mode = os.environ.get("HMT_INSPECTION_TRACER", "qualified")
    assert mode in {"legacy", "qualified"}
    if mode == "legacy":
        return LaneSurface(binding, lambda: 20.0)
    from hmt_rnd.inspection_surface import InspectionSurface
    return InspectionSurface(binding, entries, lambda: 20.0)


def changed(cap, fault):
    cap = json.loads(json.dumps(cap))
    if fault == "missing":
        return ()
    if fault == "conflict":
        return (cap, cap)
    if fault == "source":
        cap["source_pins"]["mcp_surface.py"] = "0" * 64
    elif fault == "credential":
        cap["credential_scope_and_data_egress"]["credential_ref"] = "wrong"
    else:
        field = {"scope": "binding_sha256", "schema": "input_schema_pin",
                 "epoch": "epoch", "expiry": "valid_until"}[fault]
        cap[field] = 2 if fault == "epoch" else 20.0 if fault == "expiry" else "0" * 64
    return (cap,)
