"""Source/schema/scope checks narrow the native host-authorized operation."""
import hashlib
from pathlib import Path

from .host_models import Decision
from .inspection_models import InspectionCapability
from .lane_queries import receipt_digest
from .lane_reader import read_regular
from .mcp_contracts import EmptyArguments, LaneBinding

SPINE = ("host_admission.py", "host_checks.py", "host_models.py", "host_store.py",
         "host_admin.py", "host_schema.py", "mcp_contracts.py", "mcp_handoff.py", "mcp_surface.py")


def resolve(entries: tuple[InspectionCapability, ...], launch: LaneBinding) -> InspectionCapability:
    if not entries:
        raise PermissionError("CAP_BINDING_MISSING")
    if len(entries) != 1:
        raise PermissionError("CAP_BINDING_CONFLICT")
    cap = entries[0]
    if cap.binding_sha256 != receipt_digest(launch.model_dump(mode="json")):
        raise PermissionError("CAP_SCOPE_STALE")
    scope = cap.credential_scope_and_data_egress
    if scope.credential_ref != launch.identity.credential:
        raise PermissionError("CAP_CREDENTIAL_SCOPE")
    if launch.destination != scope.destination:
        raise PermissionError("CAP_EGRESS_SCOPE")
    if (cap.input_schema_pin != receipt_digest(EmptyArguments.model_json_schema())
            or cap.output_schema_pin != receipt_digest(Decision.model_json_schema())):
        raise PermissionError("CAP_SCHEMA_STALE")
    verify_sources(cap)
    return cap


def verify_sources(cap: InspectionCapability) -> None:
    if set(cap.source_pins) != set(SPINE):
        raise PermissionError("CAP_SOURCE_SET_STALE")
    root, total = Path(__file__).parent, 0
    for name in SPINE:
        data = read_regular(root / name, root, cap.limits.source_file_bytes,
                            "CAP_SOURCE_UNAVAILABLE", "CAP_SOURCE_FILE_BOUND")
        total += len(data)
        if total > cap.limits.source_total_bytes:
            raise PermissionError("CAP_SOURCE_TOTAL_BOUND")
        if hashlib.sha256(data).hexdigest() != cap.source_pins[name]:
            raise PermissionError("CAP_SOURCE_STALE")
