"""One common derivative admission boundary for direct and MCP operations."""
import json
import time
from collections.abc import Callable

from .host_admission import admit
from .host_models import Clock, Decision, Request
from .host_store import HostStore
from .mcp_contracts import EmptyArguments, HandoffArguments, LaneBinding
from .mcp_handoff import validate_handoff

OPERATIONS = ("inspect_context", "validate_handoff")


def inspect_context(decision: Decision, arguments: dict[str, object]) -> dict[str, object]:
    """Canonical native inspection; shared by legacy and explicitly bound surfaces."""
    EmptyArguments.model_validate(arguments)
    return decision.model_dump()


class LaneSurface:
    def __init__(self, binding: LaneBinding, clock: Callable[[], float] = time.time):
        self.binding = LaneBinding.model_validate_json(binding.model_dump_json())
        self.store = HostStore(self.binding.store)
        self.clock = clock

    def authorize(self, operation: str) -> Decision:
        if operation not in OPERATIONS:
            raise PermissionError("MCP_OPERATION_NOT_EXPOSED")
        b = self.binding
        request = Request(task_id=b.task_id, revision=b.revision, operation=operation,
                          root=str(b.root), destination=b.destination)
        decision = admit(self.store, b.identity, request, Clock(now=self.clock()))
        if decision.policy != b.policy:
            raise PermissionError("MCP_POLICY_BINDING_STALE")
        return decision

    def visible(self) -> tuple[str, ...]:
        visible = []
        for operation in OPERATIONS:
            try:
                self.authorize(operation)
                visible.append(operation)
            except PermissionError:
                continue
        return tuple(visible)

    def invoke(self, operation: str, arguments: dict[str, object]) -> dict[str, object]:
        decision = self.authorize(operation)
        if len(json.dumps(arguments, ensure_ascii=False).encode()) > 65536:
            raise ValueError("MCP_ARGUMENT_BOUND")
        if operation == "inspect_context":
            return inspect_context(decision, arguments)
        payload = HandoffArguments.model_validate(arguments)
        return validate_handoff(payload.handoff.model_dump(), self.binding.identity.role,
                                self.binding.task_id)
