"""Closed host-owned descriptor for the already exposed native inspection."""
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from .host_models import Strict
from .inspection_policy import CredentialScope, InspectionLimits, RetryOwner
from .lane_models import Digest
from .mcp_contracts import LaneBinding


class InspectionCapability(Strict):
    operation_id: Literal["inspect_context"]
    owner: Literal["Host/IIEA"]
    effect_class: Literal["LOCAL_MUTATION"]
    implementation: Literal["hmt_rnd.mcp_surface.inspect_context"]
    binding_sha256: Digest
    epoch: Annotated[int, Field(ge=1)]
    source_pins: Annotated[dict[str, Digest], Field(min_length=1, max_length=32)]
    input_schema_pin: Digest
    output_schema_pin: Digest
    credential_scope_and_data_egress: CredentialScope
    retry_reconciliation_owner: RetryOwner
    limits: InspectionLimits
    valid_from: Annotated[float, Field(ge=0)]
    valid_until: Annotated[float, Field(gt=0)]
    resource_profile: Literal["LOCAL-CTRL-1"]
    evidence_contract: Literal["atomic clock checkpoint and immutable native-result receipt"]

    @model_validator(mode="after")
    def valid_interval(self) -> Self:
        if self.valid_until <= self.valid_from:
            raise ValueError("CAP_INVALID_INTERVAL")
        return self


class InspectionLaunch(Strict):
    binding: LaneBinding
    capabilities: Annotated[tuple[InspectionCapability, ...], Field(max_length=16)]
