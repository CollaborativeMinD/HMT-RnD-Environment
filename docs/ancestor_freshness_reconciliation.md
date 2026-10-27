# Ancestor assignment freshness reconciliation

RC-ANCESTOR-01 reproduced downstream sealing against superseded task evidence at baseline `608e3bdf`. An intact sealed receipt retained its recorded principal and task revision, while the current host assignment advanced, changed principal, or disappeared. Existing ancestor checks verified receipt integrity, policy, ordering and bytes but did not compare that receipt with the authoritative current task assignment.

The repair adds four lines to `lane_queries.py`. Every ancestor traversal queries the existing `host_tasks` table on the same SQLite transaction and requires its principal/revision to equal the immutable receipt's recorded values. Missing or different assignments return `LANE_PREDECESSOR_ASSIGNMENT_STALE`. The existing checks before and after evaluator execution both enforce this condition. No additional task store, assignment policy or migration authority is introduced.

Baseline evidence retains 18 failing cases and four passing controls, plus eight direct observations of stale evidence producing `SEALED`. The unchanged 22-case suite now passes. The full local suite passes **292 tests**, with zero skips and no changes across 131 recorded source/config paths during the run. Ruff, basic Pyrefly and structural gates pass. Independent supervisory reconciliation remains separate from these worker observations.

Cases cover immediate and non-immediate ancestors, revision advancement, API reassignment, missing assignments, principal-only imported-state fixtures, database reopening, unchanged assignments and unrelated task changes. Preexisting drift prevents evaluator invocation. Rejected transactions preserve all SQLite logical table contents, including the host clock; historical receipts remain unchanged. A deliberate same-connection assignment change during evaluation demonstrates the existing post-evaluator recheck and database rollback. Temporary fixture evidence files written by that evaluator are not claimed to be rolled back.

Persistence here means constructing fresh HostStore/LaneStore objects over the durable SQLite database. It does not establish process-kill or power-loss recovery. Missing/principal-only states are trusted test fixtures, not newly supported assignment operations.

Dependent work remains HOLD when ancestor assignment changes. Cross-revision or principal migration is unsupported by this repair and requires explicit architecture recovery; no historical receipt is rewritten to appear current.

`evidence/ancestor_freshness_case.json` binds the causal chain, required observations, raw failures, candidate identity and results. `evidence/ancestor_freshness_snapshot.json` contains exact source/test content for one small commit. The retained trace script is a baseline diagnostic, not a post-repair pass oracle.

From the repository root:

```bash
uv run pytest tests/test_ancestor_freshness*.py
uv run ruff check src/hmt_rnd/lane_queries.py tests/test_ancestor_freshness*.py
uv run pyrefly check src/hmt_rnd/lane_queries.py
PYTHONPATH=src uv run python scripts/check_structure.py
```

Disposition: INVESTIGATION_COMPLETE; SOLUTION_CANDIDATE_APPLIED; HOLD pending independent supervisory reconciliation and outside review. No integration progression or global HOLD clearance is asserted.
