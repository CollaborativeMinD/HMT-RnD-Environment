# Task revision issuance reconciliation

RC-LANE-07 confirms the reported writer/reader mismatch at baseline `c922345`. An origin sealed at task revision 1 could be reopened using a valid current revision-2 assignment and fresh grants. The writer persisted an event recording revision 2 and invalidated the origin. Both successor submission and architect reauthorization then denied the event with `LANE_REOPEN_TASK_BINDING`, because the immutable origin still recorded revision 1.

The scoped repair adds an origin-revision comparison before event insertion or invalidation. Unsupported cross-revision issuance now returns `LANE_REOPEN_REVISION_MISMATCH`. Existing fail-closed reader checks remain unchanged. This does not define or authorize a cross-revision migration workflow.

The retained baseline campaign has two failing issuance witnesses and five passing controls. All seven now pass. Denial checks compare every SQLite table's logical contents, including the host clock, before and after the rejected transaction and after reopening the database. Unchanged-revision reopening persists and its successor closes after fresh HostStore/LaneStore construction. Other-task, stale-grant and revoked-grant controls remain denied. These are database persistence checks, not process-kill or power-loss qualification.

The shared full-suite attempt recorded 231 passes and two failures in another worker's new FIFO-race tests, tracked under RC-ARTIFACT-01/02. That worker changed `lane_evidence.py` during the run. The entire result and before/after inventory remain retained; this mixed-worktree run does not qualify the exact RC-LANE-07 candidate.

The supervisor subsequently replayed the pinned `c922345c520db598f4b1f6afff2598c0770f0bba` baseline plus this exact three-file snapshot in an isolated checkout: **231 tests passed**, with zero failures, errors or skips. All three candidate hashes matched and the supervisor's source inventory remained unchanged during the run. `evidence/revision_issuance_final.json` links that execution without rewriting the historical mixed-run record.

Ruff, basic Pyrefly and structural checks passed for the scoped repair. Original failures, the executed causal trace, source/test bodies, candidate hashes and the exact mixed-run observations are linked by `evidence/revision_issuance_case.json`. `evidence/revision_issuance_snapshot.json` carries the exact files for one small commit.

From the repository root:

```bash
uv run pytest tests/test_revision_issuance_guards.py
uv run ruff check src/hmt_rnd/lane_reopen.py tests/test_revision_issuance*.py
uv run pyrefly check src/hmt_rnd/lane_reopen.py
PYTHONPATH=src uv run python scripts/check_structure.py
```

The retained `evidence/revision_issuance_trace.py` is a baseline-only diagnostic that demonstrates the original defect. Its successful completion is not a post-repair oracle.

Disposition: INVESTIGATION_COMPLETE; SOLUTION_CANDIDATE_APPLIED; scoped regression supported; HOLD pending outside review. HMT-B07@1 and HMT-B10@1 are unchanged. No integration progression or global HOLD clearance is asserted.
