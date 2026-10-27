"""Compose binding checks, canonical authority, native inspection and one receipt."""
import json
import sqlite3
from collections.abc import Callable
from uuid import uuid4

from . import mcp_surface
from .host_admission import authorize_and_checkpoint
from .host_models import Clock, Decision, Request
from .host_store import HostStore
from .inspection_binding import resolve
from .inspection_models import InspectionCapability
from .inspection_receipts import InspectionReceipt, persist
from .lane_queries import receipt_digest
from .mcp_contracts import EmptyArguments, LaneBinding


def current(db: sqlite3.Connection, launch: LaneBinding, cap: InspectionCapability,
            clock: Callable[[], float], monotonic: Callable[[], float],
            deadline: float) -> Decision:
    now = clock()
    if monotonic() >= deadline:
        raise PermissionError("CAP_DEADLINE_EXCEEDED")
    if now < cap.valid_from or now >= cap.valid_until:
        raise PermissionError("CAP_BINDING_TIME_STALE")
    request = Request(task_id=launch.task_id, revision=launch.revision, operation="inspect_context",
                      root=str(launch.root), destination=launch.destination)
    decision = authorize_and_checkpoint(db, launch.identity, request, Clock(now=now))
    if (decision.policy, decision.epoch) != (launch.policy, cap.epoch):
        raise PermissionError("CAP_POLICY_EPOCH_STALE")
    return decision


def execute(store: HostStore, launch: LaneBinding, entries: tuple[InspectionCapability, ...],
            arguments: dict[str, object], clock: Callable[[], float],
            monotonic: Callable[[], float]) -> dict[str, object]:
    started, call_id = monotonic(), str(uuid4())
    with store.transaction() as db:
        cap = resolve(entries, launch)
        if len(json.dumps(arguments).encode()) > cap.limits.input_bytes:
            raise ValueError("CAP_ARGUMENT_BOUND")
        EmptyArguments.model_validate(arguments)
        digest = receipt_digest(cap.model_dump(mode="json"))
        deadline = started + cap.limits.deadline_seconds
        admitted = current(db, launch, cap, clock, monotonic, deadline)
        output = mcp_surface.inspect_context(admitted, arguments)
        parsed = Decision.model_validate(output)
        if output != admitted.model_dump():
            raise PermissionError("CAP_RESULT_MISMATCH")
        if len(json.dumps(output).encode()) > cap.limits.output_bytes:
            raise ValueError("CAP_OUTPUT_BOUND")
        checked = resolve(entries, launch)
        if receipt_digest(checked.model_dump(mode="json")) != digest:
            raise PermissionError("CAP_BINDING_CHANGED")
        final = current(db, launch, checked, clock, monotonic, deadline)
        if final != admitted:
            raise PermissionError("CAP_ADMISSION_CHANGED")
        checkpoint = db.execute("SELECT last_clock FROM host_meta WHERE id=1").fetchone()[0]
        persist(db, InspectionReceipt(call_id=call_id, capability_sha256=digest,
                source_manifest_sha256=receipt_digest(cap.source_pins), result=parsed,
                input_schema_sha256=cap.input_schema_pin,
                output_schema_sha256=cap.output_schema_pin,
                arguments_sha256=receipt_digest(arguments),
                result_sha256=receipt_digest(output), clock_checkpoint=checkpoint))
        return output
