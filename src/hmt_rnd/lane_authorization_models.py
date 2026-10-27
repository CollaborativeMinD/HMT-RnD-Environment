"""Immutable explicit architect decision bound to an exact reopening event."""
from typing import Annotated

from pydantic import Field

from .host_models import Strict, Text
from .lane_models import Digest
from .lane_stages import Stage


class Reauthorization(Strict):
    event_id: Text
    event_sha256: Digest
    origin_receipt_sha256: Digest
    lineage_id: Text
    stage: Stage
    task_id: Text
    task_revision: Annotated[int, Field(ge=1)]
    policy: Text
    epoch: Annotated[int, Field(ge=1)]
    issued_by: Text
    issued_at: float
