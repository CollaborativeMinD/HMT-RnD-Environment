# Reservation conflict lookup: RC-CUSTODY-INDEX-01

Review finding 4384097209 is reproduced. The actual endpoint apply/cancel query
scanned every reservation while holding its owning SQLite write transaction.
Twelve retained baseline cases show SCAN; 10,000 unrelated rows add 40,000 measured
VM steps. Impact on real host revocation latency was not measured.

The production change adds one covering index on `(principal, effect, digest)`
during the existing Domain schema transaction. New and legacy-compatible databases
receive it on construction. Repeated construction preserves rows. There is no
query, authority, retry, cancellation, proof, or retention-policy change.

The supervisor inspected the actual query, schema transaction/rollback, unchanged
identity checks, required assertions and raw evidence. The 28 focused cases cover
new/existing provisioning, real apply/cancel queries with 0/512/10,000 unrelated
reservations, four provisioning rollback cuts, and the six-arm causal family.
The isolated cumulative run passes 415 cases and retains every prior 387 ID.
The verification unittest entrypoint passes 27 cases; it is not a separate runner
for the new pytest cases. Static gates pass. Deleting index provisioning kills all
12 required lookup/index cases.

Two experimental failures are retained. The initial whole-transition constancy
hypothesis failed eight cases. Isolating lookup work also refuted strict constancy:
the unmatched corpus needs 24 versus 25 lookup VM steps. That original claim is
withdrawn, not reported satisfied by a newer passing test.

The final causal experiment explicitly matches index-range termination using one
fixed later-key sentinel in both corpus sizes. Intact, restored, sham and alternate
index arms use 25 lookup VM steps in both sizes. Deletion and alternate-off arms
rise from 34 to 40,034. All arms preserve the expected effect/proof outcomes. The
alternate index compensates for the deleted optimization; unchanged effect safety
does not make the performance dependency irrelevant. The unmodified main corpus
still retains its observed 24/25 boundary difference.

This is a finite query-plan/work experiment. It does not qualify N01 latency,
N02 complete resource/isolation limits, N03 deadlines, N06 recovery, unlimited
same-effect history, disk-full/power-loss behavior, or production migration cost.
Index construction itself touches retained history under a write fence; target
maintenance/startup budgets remain unqualified. No tombstone is removed to improve
the measurement. Existing production/governance/operational HOLDs remain.

`evidence/custody_index_case.json` binds requirements, assertions, commands, source
identities, original failures and regression receipts. The sole executable delta
is two DDL source lines in `custody_database.py`. This is bounded engineering under
disposition 6432712455; no integration, merge, deployment or full-package acceptance.
