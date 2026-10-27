# Generic lane lifecycle derivative

The clean implementation declares eight lifecycle lanes and their 26 ordered
stages. It implements generic host admission, predecessor identity, immutable
candidate evidence, and typed reopening. It does not copy proprietary method
content or execute any inherited reference package. RRCA retains an investigation
ceiling and mission assurance an evaluation ceiling; neither can progress stages.

## Contracts and transport seam

`LaneStore(host_store)` provisions only `lane_*` tables in the existing configured
host SQLite file. No task database or authorizer is added. All mutation methods
use the existing host IMMEDIATE transaction and authorization checkpoint helper.

`submit(identity, host_request, candidate, clock_provider, evaluator)` requires
operation `lane.seal`. The host identity must own the candidate's exact lane/stage;
its credential, assignment/revision, lease, policy/epoch, root and destination are
rechecked before and after gate evaluation. The clock provider and evaluator are
trusted server dependencies, never callable names or PASS flags from the wire.

`Candidate` binds candidate ID, lineage, stage, artifact path/hash, immediate
predecessor ID, and optional typed reopen event ID. `GateContext` supplies these
identities, actual parent receipt hash, current policy/epoch, principal, task ID,
and task revision to the host-bound evaluator. The evaluator must validate the
real stage-specific mission/task relationship and execute the required gates.

`GateResult` binds stage, artifact/parent hashes, policy/epoch, SEALED or DENIED,
bounded evidence file paths/hashes, and denial reasons. Missing evaluators fail
closed before progression. Candidate and evidence artifacts are rehashed; all
current predecessor receipts and their artifact/evidence identities are checked.
Evidence files are inert outputs, not instructions to execute.

`reopen(identity, host_request, event, clock_provider)` requires `lane.reopen`.
`Reopen` specifies changed candidate IDs, lineage, successor candidate ID, reason
(`ARTIFACT_DRIFT`, `POLICY_DRIFT`, or `DENIED_REPAIR`), and termination condition.
The server verifies change evidence and scans at most 26 current lineage records
to detect omitted earlier drift. It routes to the earliest changed stage owner
and originating task; policy changes also require trusted `human_architect` role.

The resulting `ReopenEvent` records the required stage/lane, origin receipt hash,
invalidated candidate IDs, issuer and time. Every downstream candidate is
invalidated by an append-only relation. Original SEALED/DENIED records remain
unchanged. The bound successor can close the event only by a newly evaluated
SEALED or terminal DENIED receipt. Regenerated descendants must trace to a closed
typed reopening ancestor, rather than reusing invalidated receipts.

`receipt(candidate_id)` and `snapshot(digest)` are trusted diagnostic lookups, not authorized wire
operations. Transport must retain its own authenticated, task-scoped read boundary.
Candidate and gate-evidence bytes are preserved content-addressed in `lane_artifacts` BLOBs within the same transaction as the receipt. The total new stage artifact/evidence payload is bounded at 16 MiB. Oversize, drift, or failure rolls back both receipt and snapshots. Prior bytes remain retrievable after path mutation; current external paths are still checked for drift and typed reopening.

The closed `Handoff`/`HandoffBody` shape preserves the supplied response fields and
pass/hold/fail vocabulary; extensions remain referenced artifacts.

## Evidence scope

The tracer began with a missing-module collection failure before implementation.
The executed controlled evaluator checks actual artifact bytes and writes a hashed
assertion record. It proves invocation/context/persistence mechanics only. It
does not stand in for CMAD, PMCT, DOKE, MR, CSSI, IIEA, Build, or OPS domain gates.
The scoped suite exercises upstream sealing and next-stage consumption, artifact
tamper, missing evaluator, gate-context substitution, revoke, expiry during gate,
immutable denial, skipped stages, closed handoff fields, role ceilings, earliest
reopen routing, typed successor resealing, and omitted upstream drift.

SQL mutation triggers reject updates/deletes to candidate, reopen, invalidation,
and closure rows. They are local integrity controls; privileged database/file
access remains a deployment trust boundary. File hashes identify observed bytes;
host-qualified evaluator/credential/clock sources and deployment protection of the
SQLite file remain integration obligations. No external artifact store is required. Concurrent arbitrary filesystem mutation is not
claimed to be prevented by this component.

No task is marked DONE. No effects are dispatched. No deployment, complete mission
execution, or satisfaction of all stage-domain requirements is claimed. Only the
linear initial 26-stage lineage is implemented; standalone MR branches, broader
authority change classes, and richer reopening semantics require separate pinned
contracts rather than inferred permission from these generic declarations.

## Assurance gap and repair

`GAP-LANE-ARTIFACT-PRESERVATION-001` identified that immutable metadata did not preserve original artifact bytes after a referenced path changed. The repaired derivative stores bounded content-addressed artifact/evidence BLOBs atomically in the same SQLite file, with immutable triggers and integrity checks on retrieval. Tests now mutate both original artifact and gate evidence paths, reopen the database, and recover exact prior bytes for both SEALED and DENIED receipts. A combined-payload overflow test proves no partial receipt or snapshot survives rollback. Pre-repair scoped results remain in evidence/lane_lifecycle_pre_artifact_fix.json and lane_tests_pre_artifact_fix.xml. This is an implementation repair under existing requirements, not a requirement change.

## Boundary campaign

The original 17-case witness is retained under lane_lifecycle_17case.json and lane_tests_17case.xml. Twelve additional boundary/negative cases exercise actual unauthorized/stale/cross-lineage reopening and corrupt/missing/raced artifact proofs without altering production code. The lane suite now has 29 passing cases. An isolated cumulative run passed 159 tests and observed 290/308 actual branches (94.16%) across src/hmt_rnd. Remaining uncovered branches stay visible in lane_boundary_coverage.json; no exclusions or suppressions were introduced. This aggregate is a software-branch metric, not evidence that all domain gates are qualified.
