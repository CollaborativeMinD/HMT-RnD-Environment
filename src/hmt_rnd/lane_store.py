"""Lifecycle facade over the single derivative host database; no task self-DONE."""
import sqlite3

from .host_models import Identity, Request
from .host_store import HostStore
from .lane_artifacts import preserved_bytes
from .lane_models import Candidate, Receipt, Reopen, ReopenEvent
from .lane_queries import read_receipt
from .lane_schema import SCHEMA, immutable_triggers
from .lane_submission import ClockProvider, Evaluator, submit


class LaneStore:
    def __init__(self, host: HostStore):
        self.host = host
        with sqlite3.connect(host.path) as db:
            db.executescript(SCHEMA)
            for table in ("lane_candidates", "lane_reopens", "lane_invalidations",
                          "lane_closures", "lane_artifacts"):
                db.executescript(immutable_triggers(table))

    def submit(self, identity: Identity, request: Request, candidate: Candidate,
               clock: ClockProvider, evaluator: Evaluator | None) -> Receipt:
        with self.host.transaction() as db:
            return submit(db, identity, request, candidate, clock, evaluator)

    def reopen(self, identity: Identity, request: Request, event: Reopen,
               clock: ClockProvider) -> ReopenEvent:
        from .lane_reopen import reopen_candidate
        with self.host.transaction() as db:
            return reopen_candidate(db, identity, request, event, clock)

    def receipt(self, candidate_id: str) -> Receipt:
        with self.host.transaction() as db:
            return read_receipt(db, candidate_id)

    def snapshot(self, digest: str) -> bytes:
        """Trusted diagnostic only; no wire read permission is implied."""
        with self.host.transaction() as db:
            return preserved_bytes(db, digest)
