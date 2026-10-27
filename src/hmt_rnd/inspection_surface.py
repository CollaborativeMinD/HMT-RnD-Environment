"""Configured single-operation slice; default lane launcher is not activated here."""
import json
import time
from collections.abc import Callable

from .host_models import Decision
from .inspection_binding import resolve
from .inspection_execution import current, execute
from .inspection_models import InspectionCapability
from .inspection_receipts import initialize
from .mcp_contracts import LaneBinding
from .mcp_surface import LaneSurface


class InspectionSurface(LaneSurface):
    def __init__(self, binding: LaneBinding, entries: tuple[dict[str, object], ...],
                 clock: Callable[[], float] = time.time,
                 monotonic: Callable[[], float] = time.monotonic) -> None:
        if len(entries) > 16 or len(json.dumps(entries).encode()) > 65536:
            raise ValueError("CAP_REGISTRATION_BOUND")
        self.capabilities = tuple(InspectionCapability.model_validate_json(json.dumps(item))
                                  for item in entries)
        self.monotonic = monotonic
        super().__init__(binding, clock)
        initialize(self.store)

    def authorize(self, operation: str) -> Decision:
        if operation != "inspect_context":
            raise PermissionError("CAP_OPERATION_NOT_BOUND")
        started = self.monotonic()
        with self.store.transaction() as db:
            cap = resolve(self.capabilities, self.binding)
            return current(db, self.binding, cap, self.clock, self.monotonic,
                           started + cap.limits.deadline_seconds)

    def visible(self) -> tuple[str, ...]:
        try:
            self.authorize("inspect_context")
            return ("inspect_context",)
        except PermissionError:
            return ()

    def invoke(self, operation: str, arguments: dict[str, object]) -> dict[str, object]:
        if operation != "inspect_context":
            raise PermissionError("CAP_OPERATION_NOT_BOUND")
        return execute(self.store, self.binding, self.capabilities, arguments,
                       self.clock, self.monotonic)
