# Standalone derivative host tracer

All existing packages and Multi-agent-Framework are **read-only reference
implementations**. They inform required behavior and failure semantics. The clean
repository imports and installs none of them. Earlier runtime-reuse selection is
superseded; original source observations remain in host_reconciliation.json.

The smallest derivative now lives in `host_models`, `host_store`, `host_admin`,
`host_schema`, `host_checks`, and `host_admission`. It owns one configured SQLite
authority/task store. Custody tables belong in the same database. No second task
ledger, substitute external authorizer, or reference-package execution is involved.

## Boundary

The trusted host constructs `Identity` and `Clock` from its authenticated session,
credential resolver, and trusted clock. They are separate Python parameters to
`admit_wire`; wire Request contains only task ID, expected revision, operation,
resource root, and destination. Unknown fields and coercions are rejected. Python
model construction is not itself transport authentication.

`HostStore.create` is an explicit trusted provisioning operation. Assignment,
grant, revocation, and policy updates use SQLite `BEGIN IMMEDIATE`. Assignment
revision must advance. Restart reloads task ownership, grant revocation, policy
epoch, and the last standalone admission clock checkpoint from the same database.

Admission intersects current assignment/revision, authenticated principal, role,
lane, stage, credential handle, operation, exact destination, confined filesystem
root, current policy/epoch, grant interval, and evidence expiry. The full clock
uncertainty interval must fit before exclusive expiry. Clock rollback is rejected.

## Atomic seam and authority ceiling

`host_checks.authorize(connection, identity, request, clock)` performs read-only
checks on an existing SQLite connection. Custody begins its own IMMEDIATE transaction
on the same configured file and invokes this function within that fence. A host
revocation/assignment write cannot interleave while that write transaction is held.
For effecting transactions use `host_admission.authorize_and_checkpoint` on that
same connection: the host helper verifies admission and updates its own trusted
clock checkpoint. Custody never writes host metadata directly.

`host_admission.admit` provides standalone direct admission and checkpoints observed
time in its own transaction. Its returned Decision has `effect_authority=NONE`.
It is an observation, not an effect token usable after the transaction releases.
No dispatcher or external effect is implemented; later effects must re-admit within
their custody transaction. A checked policy followed by an unfenced write is forbidden.

## Tracer evidence

The initial assignment/admit/revoke/restart test was run before implementation and
failed collection because host_admission did not exist. After the derivative was
implemented, 18 scoped tests passed. They include identity field substitution,
root/destination/operation widening, exact expiry/uncertainty, stale policy/revision,
clock rollback, strict wire fields/body size, direct/wire parity, read-only checks
inside an existing sqlite3.Row transaction, and revoke deletion/restoration with an
unrelated-principal matched control. Ruff and source Pyrefly checks also passed.

These results support the bounded host tracer, not full HMT-F01/F02/F03 satisfaction.
All 26 stages, completion firewall, durable distributed effects, runtime MCP server,
OS/network isolation, hardware clock trust, process credentials, egress enforcement,
and deployment remain separate qualification obligations. No target dispatch ran.
