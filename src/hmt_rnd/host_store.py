"""Single derivative authority/task store; SQLite fences every host mutation."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from . import host_admin
from .host_models import Assignment, Grant
from .host_schema import SCHEMA


class HostStore:
    def __init__(self, path: Path):
        self.path = path.resolve()
        if not self.path.is_file():
            raise PermissionError("HOST_STORE_UNBOUND")

    @classmethod
    def create(cls, path: Path, policy: str) -> "HostStore":
        if not policy or len(policy) > 256:
            raise ValueError("HOST_POLICY_INVALID")
        with sqlite3.connect(path) as connection:
            connection.executescript(SCHEMA)
            connection.execute("INSERT OR IGNORE INTO host_meta VALUES(1,?,1,0)", (policy,))
            if connection.execute("SELECT policy FROM host_meta").fetchone()[0] != policy:
                raise PermissionError("HOST_POLICY_COLLISION")
        return cls(path)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5)
        try:
            connection.execute("BEGIN IMMEDIATE")
            with connection:
                yield connection
        finally:
            connection.close()

    def assign(self, task: Assignment) -> None:
        with self.transaction() as connection:
            host_admin.assign(connection, task)

    def grant(self, authority: Grant) -> None:
        with self.transaction() as connection:
            host_admin.grant(connection, authority)

    def revoke(self, principal: str) -> None:
        with self.transaction() as connection:
            connection.execute("UPDATE host_grants SET revoked=1 WHERE principal=?", (principal,))

    def set_policy(self, policy: str) -> None:
        if not policy or len(policy) > 256:
            raise ValueError("HOST_POLICY_INVALID")
        with self.transaction() as connection:
            connection.execute("UPDATE host_meta SET policy=?,epoch=epoch+1", (policy,))
