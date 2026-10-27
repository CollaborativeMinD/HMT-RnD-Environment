# Supervisory reconciliation: authority after ancestor reads

HOLD. PR #3 remains unmerged; integration and feature progression are blocked.
The current review record is `evidence/supervision_reconciliation.json`, with exact
runtime identities in `evidence/reopen_expiry_candidate.json`. Prior review records
are historical and remain intact. No new worker was assigned for this repair.

The supervisor missed the timing consequence of adding ancestor verification after
the final admission check. Source review alone did not qualify this ordering.
On published parent `3622a4b23faaeb9bfdd90e2018c99e19caac84fe`, 24 expiry cases
issued events and invalidations despite expired authority. The same 24 controls
at unchanged time or immediately below expiry passed. Real parent verification
was retained; a wrapper advanced only the trusted test clock after a real read.

The only production change swaps two existing calls: verify parents, then perform
current host admission, then insert the event and invalidations in the same host
transaction. No new authorizer, assignment migration, recovery route, or contract
relaxation is introduced. Full-table logical snapshots, immutable receipt equality,
and database-object reconstruction are asserted for the denied cases. These are
not process-kill, power-loss, live credential, or operating-system isolation claims.

The supervisor personally inspected the source diff, the two prior workers' scoped
tests/case records, this test's negative and positive assertions, and the preserved
execution records. The supervisor executed the focused before/after tests, isolated
cumulative suite, existing verification unittest entrypoint, static gates, and two
critical mutations. This is an implementation review, not independent assurance
or release approval. Both mutations are killed by the same 24 negative assertions.

The governing-source inventory records actual paths, versions and hashes, including
the private plan, implementation laws, high/low design views, interface contracts,
active requirements and V&V methodology. Only their identities are published.
The reference-only override governs older recommendations for live reference
services; the current stricter complexity policy governs older limits.

The work-package account covers WP-01 through WP-11. None is marked complete.
Local derivative witnesses do not qualify the planned lane skills, stage-specific
evaluators, vendor bindings, numerical/twin work, voice adoption surfaces, complete
assertion/mutation campaign, or operator acceptance. All 58 requirement statuses
and the complete candidate-space ledger remain unchanged.

The PR's existing 576-file/32-commit scope is recorded as review debt. This repair
is one coherent commit; existing history is not rewritten or represented as a
bounded PR. The original out-of-band reviewer must review this exact successor
candidate before continuation. No thread resolution, merge, deployment, or HOLD
release is inferred from this record.
