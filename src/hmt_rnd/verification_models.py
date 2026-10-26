"""Strict planning inputs; target satisfaction is not represented by these models."""
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Invariant(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    requirement_id: str = Field(pattern=r"^[A-Z0-9-]+$", max_length=64)
    gate_id: str = Field(pattern=r"^[A-Z0-9-]+$", max_length=64)
    mechanisms: tuple[str, ...] = Field(min_length=1)
    acceptance: str = Field(min_length=1, max_length=65536)


class Dimensions(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    invariants: tuple[Invariant, ...] = Field(min_length=1)
    mechanisms: tuple[str, ...] = Field(min_length=1)
    gates: tuple[str, ...] = Field(min_length=1)
    maximum_rows: int = Field(default=100000, ge=1, le=100000)

    @model_validator(mode="after")
    def validate_domains(self) -> "Dimensions":
        ids = [item.requirement_id for item in self.invariants]
        if len(set(ids)) != len(ids):
            raise ValueError("DUPLICATE_INVARIANT")
        if len(set(self.mechanisms)) != len(self.mechanisms):
            raise ValueError("DUPLICATE_MECHANISM")
        if len(set(self.gates)) != len(self.gates):
            raise ValueError("DUPLICATE_GATE")
        for item in self.invariants:
            if item.gate_id not in self.gates:
                raise ValueError("UNKNOWN_OWNING_GATE")
            if not set(item.mechanisms).issubset(self.mechanisms):
                raise ValueError("UNKNOWN_APPLICABLE_MECHANISM")
        if len(ids) * len(self.mechanisms) * len(self.gates) > self.maximum_rows:
            raise ValueError("CANDIDATE_SPACE_LIMIT_EXCEEDED")
        if sum(len(item.acceptance.encode()) for item in self.invariants) > 8388608:
            raise ValueError("DIMENSION_INPUT_LIMIT_EXCEEDED")
        return self
