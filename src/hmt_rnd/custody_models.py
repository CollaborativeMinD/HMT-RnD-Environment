"""Closed wire contracts for the standalone bounded custody derivative."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Id = Annotated[str, Field(pattern=r"^[A-Za-z0-9_.:-]{1,96}$")]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class Closed(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True,
                              revalidate_instances="always")


class Intent(Closed):
    endpoint_id: Id
    principal: Id
    effect_id: Id
    payload_digest: Digest


class Reservation(Closed):
    intent: Intent
    reservation_id: Id
    status: Literal["OUTCOME_UNCERTAIN"] = "OUTCOME_UNCERTAIN"


class Proof(Closed):
    intent: Intent
    reservation_id: Id
    endpoint_id: Id
    outcome: Literal["COMMITTED", "NOT_EXECUTED"]
    signature: Digest
