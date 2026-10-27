# Operator runbook

RC-LAUNCH-STORE-01 repair candidate: see `docs/launch_store_identity_repair.md`
and `evidence/launch_store_repair/case.json`. Store and root in host launch bindings
must be absolute before serialization/admission. A relative launch fails with
`MCP_BINDING_PATH_NOT_ABSOLUTE` before any HostStore opens. Preserve invalid
launches and request corrected host-owned absolute bindings; never infer a base
from the working directory, reroute, or rewrite historical receipts. Replay with
`uv run pytest tests/test_launch_identity*.py -q`. Outside acceptance is pending;
integration remains blocked.

Current bounded milestone: `docs/local_inspection_binding.md` and
`evidence/inspection_case.json`, under the committed out-of-band continuation
order. Replay its declared cases with `uv run --group dev python -m pytest
tests/test_inspection*.py -q`. Inspect exact receipt exports before accepting a
claim. CAP_BINDING_MISSING/CONFLICT, stale source/schema/scope, expiry and canonical
host denials block invocation; do not choose another provider or bypass the gate.
The configured adapter is not activated by the default launcher. Receipt diagnostics
are trusted-host reads, not a new MCP tool. Integration remains blocked.

Use uv only. From this repository:

```bash
uv sync --group dev
uv run --group dev python -m pytest -q
uv run --group dev ruff check src tests
```

Read evidence and source maps before qualifying any derivative. Supplied HMT implementations are read-only design references, with provenance retained separately. Their installation or availability is not a runtime requirement. Only explicitly selected operational dependencies, such as the Whisper binary/model, must be bound at use.

Whisper runtime/model are supplied and pinned by the host. No model download occurs during inference. Transcripts enter a draft; submission and task authority remain separate.

HOLD, revoked authority, and semantic denial stop fallback. External effect uncertainty requires exact-effect reconciliation. No operator should repeat a write merely because its receipt is missing.

Troubleshoot by preserving the failing command, candidate/source/policy identities, actual observations, and cumulative ledger. Contradictory assumptions reopen requirements through the controlled change path.

## Derivative qualification

All supplied HMT implementations are read-only references. Runtime imports from reference packages are forbidden; repository-owned derivatives retain and extend the admitted behaviors. No reference installation is required for the portable suite. See docs/host_derivative.md and docs/custody_adapter.md for the transaction and proof domains.

The five earlier engine tests in evidence/custody_reference_parity.json are historical reference observations only; current derivative tests live under tests/test_custody*.py. They do not establish vendor, process-kill, power-loss or hardware fidelity.

Run full source type checks with `uv run --group dev pyrefly check src`. The prior missing-reference-import failure is retained as historical evidence of the corrected dependency interpretation.

## Reconciliation and HOLD procedure

The active continuation record is `evidence/engineering_continuation.json`. Out-of-band disposition 6432712455 releases the scoped technical reconciliation HOLD at exact candidate `351d5081536e3a968dd449e874281e75475d22fd`. Previously authorized bounded engineering may resume with personal source/evidence verification. The older supervision/case registers retain their historical pending statuses. This release does not close production, governance, or operational HOLDs, qualify complete work packages, authorize integration, or approve merge/deployment.

Acceptance 6433215377 separately accepts the custody-index change at `f0e671acd513be3bfdb72e546d422839fdfbbf2e`. The latest source review packet is `evidence/receipt_path_case.json` for RC-RECEIPT-PATH-01; its acceptance is not inherited from that parent.

New lifecycle receipts store absolute artifact/evidence spellings after existing guarded checks and snapshot preservation, before final clock/admission. Relative request paths remain supported; symlinks and literal `..` remain denied. If a historical relative receipt fails after cwd change, preserve it and establish its original context through the owning recovery process; never guess a new base or rewrite immutable receipt rows. Unsupported migration remains HOLD. `uv run --group dev python -m pytest tests/test_receipt_path_*.py -q` replays the declared path and expiry cases; the separate causal-arm source copies and commands are recorded in `evidence/receipt_path_causal_family.json`.

When `LANE_PREDECESSOR_ASSIGNMENT_STALE` occurs, preserve the receipt and compare its recorded principal/revision with the current `host_tasks` assignment for every ancestor. Submission checks the chain before and after evaluation. Reopening verifies the chain, then rechecks current host authority immediately before inserting the event or invalidations. If grant/evidence expiry is reached during those reads, `HOST_LEASE_OR_EVIDENCE_EXPIRED` must leave the full database state unchanged. No assignment migration, rerouting, or receipt rewrite is inferred. Escalate unsupported recovery to the owning lane and architecture process while retaining HOLD.

For reservation lookup scaling, inspect `evidence/custody_index_case.json`. Trusted Domain construction provisions `custody_reservation_identity(principal,effect,digest)` for new and existing databases in its schema transaction. Provision before serving work; index creation may hold the write fence while reading history. On storage/schema failure preserve the original database and failure, keep the service unavailable, and diagnose under the owning maintenance authority. Do not delete reservations/tombstones or bypass authority to speed startup. Existing tests cover rollback, not production migration budgets. `uv run --group dev python -m pytest tests/test_custody_index*.py -q` replays the bounded query-plan, behavior and causal checks.

Drift detection must pass the original path and root to the guarded reader. Scope, symlink, parent-traversal, nonregular-file, and invalid-root errors remain denials. Only a direct `FileNotFoundError` cause strictly below a valid traversed root qualifies as missing-source drift. Do not resolve or stat the input first, or swallow another scope error as absence. A genuine missing artifact/evidence source can route to its earliest existing stage owner; repaired bytes and the designated successor still require normal admission and gate evidence. See `docs/drift_symlink_reconciliation.md` and the two ancestor reconciliation documents.

Artifact/evidence input paths and roots must contain no literal `..` components. The reader rejects them before normalization or opening; it never silently changes the input spelling for verification. Use explicit canonical paths or relative paths without parent components. This restriction also rejects otherwise benign parent traversal. Preserve the original spelling and typed denial in an RRCA record if an input needs correction; do not weaken the guard to admit it. See `docs/path_identity_reconciliation.md` for the native-read/evaluator/snapshot counterexample.

An origin/request task revision mismatch denies reopening issuance before any event or invalidation is committed. Cross-revision recovery is unsupported; do not create an event or infer migration authority. For artifact/evidence reads, both hashing and snapshot preservation require regular descriptors opened nonblocking with no symlink components. An artifact FIFO, directory, or scope violation yields the existing typed scope denial and transaction rollback. Preserve the witness and use the owning lane's correction process. Symbolic-link inputs are deliberately rejected. The reader preserves digest checks and byte limits; it is not a filesystem sandbox or a general I/O deadline guarantee.

For a pending reopening rejected with `LANE_REOPEN_AUTHORITY_STALE`, preserve the event and successor reservation. A currently authorized human architect may use the trusted-host `LaneStore.reauthorize` operation with a current `lane.reauthorize` grant for the exact original task/revision and stage. The append-only approval binds the immutable event digest, origin receipt, lineage, stage, policy, and epoch. A builder then needs its own current `lane.seal` grant to submit the designated successor. This recovery function has no MCP exposure. Missing legacy bindings, changed task revisions, or unproved authority remain HOLD; no migration or rebinding authority is inferred.

1. Read `evidence/reconciliation_closure_register.json` and the named case record before admitting further work. A closed scoped repair is not whole-requirement satisfaction or integration permission.
2. Preserve the original source identity, failing command/observation, and causal frontier when a tracer contradicts a claim. Reopen its case and affected requirement under `contracts/CR-RECONCILIATION-004.json`; never replace a failure with an unrelated passing test.
3. Inspect the eight-column `Cumulative_Gate_Ledger.csv` and `Reverse_RCA_Ledger.csv`. The identical tables are exported in `evidence/build_ledgers.sqlite.gz`. Keep worker attestations and previous rows intact.
4. Reproduce only in a disposable copy with explicitly pinned source overlays. Compare source inventories before and after execution. The initial replay-precondition failure is retained in `evidence/reconcile_sequence_custody_initial.json`.
5. Run the cumulative suite and local gates above. For branch measurement include both production code and executable scripts with `PYTHONPATH=src uv run coverage run --source=hmt_rnd,scripts -m pytest -q`; combine subprocess coverage and compare changed files to the pinned parent. Do not replace a changed-code denominator with the whole package percentage.
6. Have mission assurance review the recorded evidence read-only. Keep integration on HOLD until its separately stated evidence and human instructions are present. Never select fallback to bypass HOLD or retry an unresolved effect.
