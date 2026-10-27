"""Append-only lifecycle records in the same derivative host SQLite database."""
SCHEMA = """
CREATE TABLE IF NOT EXISTS lane_candidates(
 id TEXT PRIMARY KEY,lineage TEXT NOT NULL,stage TEXT NOT NULL,
 body TEXT NOT NULL,digest TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS lane_reopens(
 id TEXT PRIMARY KEY,lineage TEXT NOT NULL,stage TEXT NOT NULL,
 successor TEXT UNIQUE NOT NULL,body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS lane_invalidations(
 event TEXT NOT NULL,candidate TEXT NOT NULL,PRIMARY KEY(event,candidate));
CREATE TABLE IF NOT EXISTS lane_closures(
 event TEXT PRIMARY KEY,candidate TEXT NOT NULL,digest TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS lane_artifacts(digest TEXT PRIMARY KEY,body BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS lane_reauthorizations(
 event TEXT NOT NULL,policy TEXT NOT NULL,epoch INTEGER NOT NULL,body TEXT NOT NULL,
 PRIMARY KEY(event,policy,epoch));
"""


def immutable_triggers(table: str) -> str:
    return (f"CREATE TRIGGER IF NOT EXISTS {table}_no_update BEFORE UPDATE ON {table} "
            "BEGIN SELECT RAISE(ABORT,'IMMUTABLE_LIFECYCLE'); END;"
            f"CREATE TRIGGER IF NOT EXISTS {table}_no_delete BEFORE DELETE ON {table} "
            "BEGIN SELECT RAISE(ABORT,'IMMUTABLE_LIFECYCLE'); END;")
