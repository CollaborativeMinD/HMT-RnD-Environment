"""Derivative host contracts; identity and clock originate at trusted host boundary."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Text = Annotated[str, Field(min_length=1, max_length=256)]


class Strict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True,
                              allow_inf_nan=False, revalidate_instances="always")


class Identity(Strict):
    principal: Text
    role: Text
    lane: Text
    stage: Text
    credential: Text


class Clock(Strict):
    now: Annotated[float, Field(ge=0)]
    uncertainty: Annotated[float, Field(ge=0)] = 0.0


class Assignment(Strict):
    task_id: Text
    principal: Text
    revision: Annotated[int, Field(ge=1)]


class Request(Strict):
    task_id: Text
    revision: Annotated[int, Field(ge=1)]
    operation: Text
    root: Text
    destination: Text


class Grant(Identity):
    task_id: Text
    revision: Annotated[int, Field(ge=1)] = 1
    operation: Text
    root: Text
    destination: Text
    policy: Text
    epoch: Annotated[int, Field(ge=1)]
    not_before: Annotated[float, Field(ge=0)]
    expires: Annotated[float, Field(gt=0)]
    evidence_expires: Annotated[float, Field(gt=0)]


class Decision(Strict):
    principal: Text
    task_id: Text
    task_revision: int
    operation: Text
    policy: Text
    epoch: int
    effect_authority: Literal["NONE"] = "NONE"
