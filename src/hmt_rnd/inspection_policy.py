"""Narrow local inspection policy; these fields can restrict, never mint grants."""
from typing import Annotated, Literal

from pydantic import Field, field_validator

from .host_models import Strict, Text


class CredentialScope(Strict):
    credential_ref: Text
    destination: Literal["local"]
    external_egress: Literal["DENY"]


class RetryOwner(Strict):
    owner: Literal["Host"]
    maximum_attempts: Annotated[int, Field(ge=1, le=1)]
    automatic_retry: bool
    uncertain: Literal["HOLD"]

    @field_validator("automatic_retry")
    @classmethod
    def no_retry(cls, value: bool) -> bool:
        if value:
            raise ValueError("INSPECTION_RETRY_FORBIDDEN")
        return value


class InspectionLimits(Strict):
    input_bytes: Annotated[int, Field(ge=1, le=65536)]
    output_bytes: Annotated[int, Field(ge=1, le=4096)]
    source_file_bytes: Annotated[int, Field(ge=1, le=65536)]
    source_total_bytes: Annotated[int, Field(ge=1, le=131072)]
    deadline_seconds: Annotated[int, Field(ge=1, le=30)]
