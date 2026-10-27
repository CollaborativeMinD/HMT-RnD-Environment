"""Immutable host launch binding; no protocol argument selects identity or scope."""
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator

from .host_models import Identity, Strict, Text
from .mcp_handoff import Handoff


class LaneBinding(Strict):
    identity: Identity
    store: Path
    task_id: Text
    revision: Annotated[int, Field(ge=1)]
    root: Path
    destination: Text
    policy: Text

    @field_validator("store", "root")
    @classmethod
    def absolute_identity(cls, value: Path) -> Path:
        if not value.is_absolute():
            raise ValueError("MCP_BINDING_PATH_NOT_ABSOLUTE")
        return value


class EmptyArguments(Strict):
    pass


class HandoffArguments(Strict):
    handoff: Handoff
