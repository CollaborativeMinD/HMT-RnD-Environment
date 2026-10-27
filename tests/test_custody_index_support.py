"""Measure actual endpoint SQL; synthetic retained history is never compacted."""
import hashlib
import sqlite3

from hmt_rnd import custody_database

INDEX = "custody_reservation_identity"


def table_state(path):
    with sqlite3.connect(path) as db:
        names = db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return {name: sorted(db.execute('SELECT * FROM "' + name + '"').fetchall(), key=repr)
                for (name,) in names.fetchall()}


def seed_history(path, count):
    rows = [(f"unrelated-{i}", "bob" if i % 2 else "alice", f"unrelated-{i}",
             "b" * 64, "NOT_EXECUTED") for i in range(count)]
    rows += [(f"old-{i}", "alice", "effect1", "a" * 64, "NOT_EXECUTED") for i in range(3)]
    with sqlite3.connect(path) as db:
        db.executemany("INSERT INTO custody_endpoint_reservations VALUES(?,?,?,?,?)", rows)


def observe(endpoint, operation, reservation, monkeypatch):
    records = []

    class Measured(sqlite3.Connection):
        def start(self):
            self.steps, self.statements = 0, []
            self.lookup_steps, self.in_lookup = 0, False
            self.set_trace_callback(self.trace)
            self.set_progress_handler(self.progress, 1)

        def trace(self, sql):
            self.statements.append(sql)
            self.in_lookup = sql.startswith("SELECT 1 FROM custody_endpoint_reservations ")

        def progress(self):
            self.steps += 1
            self.lookup_steps += int(self.in_lookup)
            return 0

        def close(self):
            records.append({"steps": self.steps, "lookup_steps": self.lookup_steps,
                            "statements": self.statements})
            super().close()

    original = sqlite3.connect

    def connect(*args, **kwargs):
        db = original(*args, factory=Measured, **kwargs)
        db.start()
        return db

    with monkeypatch.context() as patch:
        patch.setattr(custody_database.sqlite3, "connect", connect)
        proof = getattr(endpoint, operation)(reservation)
    assert len(records) == 1
    conflict = [q for q in records[0]["statements"]
                if q.startswith("SELECT 1 FROM custody_endpoint_reservations ")]
    assert len(conflict) == 1
    with sqlite3.connect(endpoint.domain.path) as db:
        plan = [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + conflict[0])]
    return proof, {"query": conflict[0], "plan": plan, "vm_steps": records[0]["steps"],
                   "lookup_vm_steps": records[0]["lookup_steps"]}


def state_digest(value):
    return hashlib.sha256(repr(value).encode()).hexdigest()
