"""Append-only inspection evidence shares the existing host transaction domain."""
import json
import sqlite3
from typing import Literal, Self

from pydantic import Field, model_validator

from .host_models import Decision, Strict, Text
from .host_store import HostStore
from .lane_models import Digest
from .lane_queries import receipt_digest


class InspectionReceipt(Strict):
    call_id: Text
    capability_sha256: Digest
    source_manifest_sha256: Digest
    input_schema_sha256: Digest
    output_schema_sha256: Digest
    arguments_sha256: Digest
    result: Decision
    result_sha256: Digest
    clock_checkpoint: float = Field(ge=0)
    effect_class: Literal["LOCAL_MUTATION"] = "LOCAL_MUTATION"
    external_effects: Literal[0] = 0

    @model_validator(mode="after")
    def result_identity(self) -> Self:
        if self.result_sha256 != receipt_digest(self.result.model_dump(mode="json")):
            raise ValueError("CAP_RECEIPT_RESULT_IDENTITY")
        return self


def initialize(store: HostStore) -> None:
    with store.transaction() as db:
        db.execute("CREATE TABLE IF NOT EXISTS host_inspection_receipts("
                   "id TEXT PRIMARY KEY,body TEXT NOT NULL,digest TEXT NOT NULL)")
        for verb in ("UPDATE", "DELETE"):
            db.execute(f"CREATE TRIGGER IF NOT EXISTS inspection_no_{verb} BEFORE {verb} "
                       "ON host_inspection_receipts BEGIN "
                       "SELECT RAISE(ABORT,'INSPECTION_RECEIPT_IMMUTABLE'); END")


def persist(db: sqlite3.Connection, receipt: InspectionReceipt) -> None:
    body = receipt.model_dump(mode="json")
    db.execute("INSERT INTO host_inspection_receipts VALUES(?,?,?)",
               (receipt.call_id, json.dumps(body), receipt_digest(body)))


def read(store: HostStore, call_id: str) -> InspectionReceipt:
    """Trusted host diagnostic only; not an MCP tool or an admission grant."""
    with store.transaction() as db:
        row = db.execute("SELECT body,digest FROM host_inspection_receipts WHERE id=?",
                         (call_id,)).fetchone()
        if row is None:
            raise PermissionError("CAP_RECEIPT_MISSING")
        receipt = InspectionReceipt.model_validate_json(row[0])
        if receipt.call_id != call_id or receipt_digest(receipt.model_dump(mode="json")) != row[1]:
            raise PermissionError("CAP_RECEIPT_INTEGRITY")
        return receipt
