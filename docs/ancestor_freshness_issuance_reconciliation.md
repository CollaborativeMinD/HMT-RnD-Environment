# Ancestor freshness at reopening issuance

This is an additive correction to RC-ANCESTOR-01. The original submission fix and its published `cdef1fd` evidence remain unchanged. The correction closes a writer/reader mismatch found during cross-spectrum review under HMT-F02@1 and HMT-B07@1.

After an upstream task assignment changed, a freshly authorized downstream stage could reopen its own changed artifact. Discovery selected that downstream artifact, and issuance persisted an event and invalidation. The designated successor then correctly failed the new current-ancestor check. Retained traces show this sequence at both CMAD2 and CMAD3: one event and invalidation persisted, successor denied, zero closures.

Issuance now calls the existing canonical `check_parent` on the earliest changed candidate, under the same transaction, after final host admission and immediately before inserting the event. Stale ancestry denies the operation and rolls back all SQLite changes, including the clock checkpoint. The repair adds one import and one call. It does not alter discovery, the reader check, assignment policy, routing authority or migration support.

The retained baseline campaign has 16 failures and four passing controls. The unchanged 20 tests now pass. They cover immediate/non-immediate ancestors, revision advancement, reassignment, missing and principal-only assignment fixtures, database reopening, unchanged ancestry and unrelated task changes. Rejected issuance leaves every SQLite table's logical contents unchanged and preserves all original receipts. Positive controls reopen and seal their designated successor after database reopening.

The cumulative local suite passes **339 tests**, with zero skips and no source/config changes across 139 recorded paths. Ruff, basic Pyrefly and structural checks pass. The full worktree includes a separately scoped drift repair, so the supervisor's ordered isolated replay remains a separate evidence requirement.

`evidence/ancestor_freshness_issuance_case.json` links the causal trace, original failures, exact candidate and regression records. `evidence/ancestor_freshness_issuance_snapshot.json` contains three files for a small follow-up commit. The original four-file submission snapshot was not rewritten.

From the repository root:

```bash
uv run pytest tests/test_ancestor_freshness_issuance.py
uv run ruff check src/hmt_rnd/lane_reopen.py tests/test_ancestor_freshness_issuance*.py
uv run pyrefly check src/hmt_rnd/lane_reopen.py
PYTHONPATH=src uv run python scripts/check_structure.py
```

Recovery across assignment/revision changes remains unsupported and explicitly HOLD. Persistence checks use fresh database objects, not process-kill or power-loss injection. No integration progression or global HOLD clearance is asserted.
