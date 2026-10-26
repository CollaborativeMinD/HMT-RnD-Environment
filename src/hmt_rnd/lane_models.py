"""Strict lifecycle wire records and host gate-evaluation context."""
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from .host_models import Strict, Text
from .lane_stages import Stage

Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class Candidate(Strict):
    candidate_id: Text
    lineage_id: Text
    stage: Stage
    artifact: Path
    artifact_sha256: Digest
    predecessor_id: Text | None = None
    reopen_id: Text | None = None


class Evidence(Strict):
    path: Path
    sha256: Digest


class GateContext(Strict):
    candidate: Candidate
    predecessor_sha256: Digest | None
    policy: Text
    epoch: int
    principal: Text
    task_id: Text
    task_revision: int


class GateResult(Strict):
    stage: Stage
    artifact_sha256: Digest
    predecessor_sha256: Digest | None
    policy: Text
    epoch: int
    outcome: Literal["SEALED", "DENIED"]
    evidence: Annotated[tuple[Evidence, ...], Field(min_length=1, max_length=32)]
    reasons: Annotated[tuple[Text, ...], Field(max_length=32)] = ()


class Receipt(Strict):
    candidate: Candidate
    gate: GateResult
    principal: Text
    task_id: Text
    task_revision: int
    issued_at: float
    receipt_sha256: Digest


class Reopen(Strict):
    event_id: Text
    lineage_id: Text
    changed_candidates: Annotated[tuple[Text, ...], Field(min_length=1, max_length=26)]
    successor_candidate_id: Text
    reason: Literal["ARTIFACT_DRIFT", "POLICY_DRIFT", "DENIED_REPAIR"]
    termination_condition: Annotated[str, Field(min_length=8, max_length=256)]


class ReopenEvent(Strict):
    request: Reopen
    required_stage: Stage
    required_lane: Text
    origin_receipt_sha256: Digest
    invalidated_candidates: tuple[Text, ...]
    issued_by: Text
    issued_at: float
