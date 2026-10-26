# Standalone custody derivative

All supplied bundles are read-only reference implementations. Production imports
from those bundles have been removed. This derivative owns its `custody_*` tables;
it does not install a supplied package, create task authority, or dispatch effects.

`CustodyStore(path, authority, endpoint_keys)` stages immutable Intent, reserves an
external effect, and reconciles exact authenticated Proof. Host callbacks have the
signature `authority(connection, operation, principal, effect_id)` and execute after
`BEGIN IMMEDIATE`, before mutations. They must bind authenticated host identity,
current task revision/grant/clock, and policy; they must not accept self-asserted roles.

Use the same SQLite file as `host_*` authority tables. Host assignment, grant,
revocation, and policy mutations must also use `BEGIN IMMEDIATE`. The callback uses
the supplied connection; no nested writer or separate-database precheck is safe.
Current host clock checkpoint must be committed inside this same transaction when
using the transaction-aware path. Use `host_admission.authorize_and_checkpoint` on the supplied connection; it owns
its host-meta clock update. The read-only `host_checks.authorize` helper alone is
insufficient when this operation bypasses standalone host admission.

Stage rejects changed-input collisions. Reserve atomically writes reservation ID
and OUTCOME_UNCERTAIN before returning to any dispatcher. A second reserve is blocked
until a trusted exact-reservation proof resolves the old one. Reconciliation checks
endpoint trust/signature, principal/effect/input identity, exact reservation, state,
and fresh host authority. No generic retry or provider fallback exists.

The local simulated Endpoint owns a separate SQLite authority domain. Apply and
lookup-or-cancel serialize there. Durable cancellation fences delayed original
reservations. Completion proofs close the original effect; a nonexecution proof
permits a new reservation only after another fresh admission under the same intent.
There is no claim of instantaneous revocation across independent endpoint domains.

## Current witnesses

Seventeen ordinary pytest cases run with zero private-source requirements:

```bash
uv run --group dev python -m pytest tests/test_custody*.py \
  -q --junitxml=/tmp/custody_derivative.xml
```

They exercise persisted uncertainty through store reopen, blocked repeat reserve,
idempotent proof-bound completion, durable cancellation against delayed execution,
stale-reservation proof rejection, fresh reconciliation authority, tampered proof,
input collision, closed wire shape, serialized host-revoke ordering, and rejection
of another trusted endpoint at both endpoint dispatch and store reconciliation.
The target endpoint is part of the immutable Intent and the stored custody identity. The seventeen
case names are in `evidence/custody_qualification_manifest.json`; every case must
collect. `evidence/custody_derivative.json` retains raw JUnit and code identities.

The earlier five canonical-source tests remain in
`evidence/custody_reference_parity.json` as historical reference observations only.
They are not the derivative's qualification or an external runtime prerequisite.

`GAP-FRESH-GUARD-001` remains a source-reference finding: the inherited fallback
algorithm guards once before cache but not at every provider attempt. The new
custody derivative has no such fallback loop. Future read-only fallback derivatives
must demonstrate fresh guards without changing B02 or resetting a shared budget.

Deployment remains blocked on real host/clock composition, endpoint trust roots,
process-kill and rollback custody, disk/resource/pressure campaigns, and full causal
and target-oracle coverage. Reopen testing is not power-loss or process-kill proof.

The expanded boundary campaign rejects short trust roots, unknown/completed effects,
incompatible storage schema, reservation/payload collisions, unknown endpoint and
self-inconsistent proofs, authenticated wrong input, and invalid persisted state.
Isolated custody coverage reports 44/44 branches; this metric covers these seven
production modules only and does not satisfy the remaining target qualification.
