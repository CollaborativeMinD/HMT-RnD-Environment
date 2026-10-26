"""Immutable host launch binding; no protocol argument selects identity or scope."""
from pathlib import Path
from typing import Annotated

from pydantic import Field

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


class EmptyArguments(Strict):
    pass


class HandoffArguments(Strict):
    handoff: Handoff
