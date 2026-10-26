"""Host authority tables share one configured database with derivative custody."""
SCHEMA = """
CREATE TABLE IF NOT EXISTS host_meta(
 id INTEGER PRIMARY KEY CHECK(id=1),policy TEXT NOT NULL,epoch INTEGER NOT NULL,
 last_clock REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS host_tasks(
 task_id TEXT PRIMARY KEY,principal TEXT NOT NULL,revision INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS host_grants(
 principal TEXT NOT NULL,task_id TEXT NOT NULL,operation TEXT NOT NULL,
 body TEXT NOT NULL,revoked INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(principal,task_id,operation));
"""
