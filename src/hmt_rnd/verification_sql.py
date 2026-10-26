"""SQL candidate product retains exclusions and cannot represent a target PASS."""
SCHEMA = """
CREATE TABLE invariants(requirement_id TEXT PRIMARY KEY, gate_id TEXT, acceptance TEXT);
CREATE TABLE mechanisms(id TEXT PRIMARY KEY, canonical_id TEXT UNIQUE);
CREATE TABLE gates(id TEXT PRIMARY KEY);
CREATE TABLE applicable(requirement_id TEXT, mechanism_id TEXT,
 PRIMARY KEY(requirement_id,mechanism_id));
CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT);
"""
PRODUCT = """
CREATE TABLE candidates AS
SELECT CASE WHEN i.requirement_id LIKE 'HMT-%'
 THEN 'I-'||substr(i.requirement_id,5) ELSE i.requirement_id END
 ||'__'||m.canonical_id||'__'||g.id AS candidate_id,
 i.requirement_id, m.id AS mechanism_id,g.id AS gate_id,
 CASE WHEN g.id<>i.gate_id THEN 'NOT_APPLICABLE'
 WHEN NOT EXISTS(SELECT 1 FROM applicable a WHERE
 a.requirement_id=i.requirement_id AND a.mechanism_id=m.id) THEN 'NOT_APPLICABLE'
 ELSE 'APPLICABLE' END AS applicability,
 CASE WHEN g.id<>i.gate_id THEN 'P_GATE_OWNER: gate must equal owning gate'
 WHEN NOT EXISTS(SELECT 1 FROM applicable a WHERE
 a.requirement_id=i.requirement_id AND a.mechanism_id=m.id)
 THEN 'P_MECHANISM: mechanism must belong to reviewed applicability set'
 ELSE '' END AS violated_predicate,
 CASE WHEN g.id=i.gate_id AND EXISTS(SELECT 1 FROM applicable a WHERE
 a.requirement_id=i.requirement_id AND a.mechanism_id=m.id)
 THEN 'NOT_EXECUTED' ELSE 'NOT_APPLICABLE' END AS evidence_status
FROM invariants i CROSS JOIN mechanisms m CROSS JOIN gates g;
CREATE UNIQUE INDEX candidate_identity ON candidates(candidate_id);
"""

MECHANISM_KEYS = ("control", "malformed", "auth", "cross", "egress", "timeout",
                  "crash", "duplicate", "drift", "tamper", "resource", "numerical",
                  "suppression", "complexity")
MECHANISM_IDS = {key: f"M{index:02}" for index, key in enumerate(MECHANISM_KEYS)}


def seal_sql() -> str:
    tables = ("invariants", "mechanisms", "gates", "applicable", "metadata", "candidates")
    return "\n".join(
        f"CREATE TRIGGER sealed_{table}_{operation} BEFORE {operation} ON {table} "
        "BEGIN SELECT RAISE(ABORT,'SEALED_LEDGER'); END;"
        for table in tables for operation in ("INSERT", "UPDATE", "DELETE")
    )
