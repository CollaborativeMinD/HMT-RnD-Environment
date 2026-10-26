"""Bounded closed handoff derivative; all output remains evaluation evidence."""
from typing import Annotated, Literal

from pydantic import Field

from .host_models import Strict

Text = Annotated[str, Field(max_length=4096)]
Items = Annotated[list[Text], Field(max_length=64)]


class HandoffResponse(Strict):
    agent_role: Text
    task_owned: Text
    implementation: Text | Items
    risks: Items
    assumptions: Items
    follow_up_instructions: Items
    validation_status: Literal["pass", "hold", "fail"]
    artifact_refs: Items
    provenance_id: Text


class Handoff(Strict):
    response: HandoffResponse


def validate_handoff(payload: dict[str, object], role: str, task_id: str) -> dict[str, object]:
    parsed = Handoff.model_validate(payload)
    if parsed.response.agent_role != role or parsed.response.task_owned != task_id:
        raise PermissionError("MCP_HANDOFF_SCOPE_DENIED")
    return {"schema_valid": True, "reported_validation_status": parsed.response.validation_status,
            "effect_authority": "NONE", "acceptance_granted": False}
