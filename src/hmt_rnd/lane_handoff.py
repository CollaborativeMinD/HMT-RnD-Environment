"""Closed generic handoff shape; referenced artifacts carry additional contracts."""
from typing import Literal

from .host_models import Strict


class HandoffBody(Strict):
    agent_role: str
    task_owned: str
    implementation: str | list[str]
    risks: list[str]
    assumptions: list[str]
    follow_up_instructions: list[str]
    validation_status: Literal["pass", "hold", "fail"]
    artifact_refs: list[str]
    provenance_id: str


class Handoff(Strict):
    response: HandoffBody
