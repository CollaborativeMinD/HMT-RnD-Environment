"""One local domain; host revokes must serialize in this same SQLite file."""
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

Authority = Callable[[sqlite3.Connection, str, str, str], None]


class CustodyFault(Exception):
    """Explicit boundary condition; no automatic fallback handler."""


class Domain:
    def __init__(self, path: Path, authority: Authority) -> None:
        self.path, self.authority = path, authority
        with self.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS custody_intents(principal TEXT,effect TEXT,"
                       "digest TEXT,target TEXT,status TEXT,reservation TEXT,"
                       "PRIMARY KEY(principal,effect))")
            columns = {row[1] for row in db.execute("PRAGMA table_info(custody_intents)")}
            if "target" not in columns:
                raise CustodyFault("SCHEMA_REVISION_REQUIRED")
            db.execute("CREATE TABLE IF NOT EXISTS custody_endpoint_reservations("
                       "id TEXT PRIMARY KEY,principal TEXT,effect TEXT,digest TEXT,status TEXT)")
            db.execute("CREATE INDEX IF NOT EXISTS custody_reservation_identity "
                       "ON custody_endpoint_reservations(principal,effect,digest)")
            db.execute("CREATE TABLE IF NOT EXISTS custody_endpoint_effects("
                       "principal TEXT,effect TEXT,digest TEXT,PRIMARY KEY(principal,effect))")

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()
