> Current user clarification: all packages/frameworks below are read-only reference implementations. The runtime-reuse decision in this historical source review is superseded. The clean derivative lives in host_*.py and owns one SQLite authority/task store composed with derivative custody. Source observations remain valid as observations; source runtime entrypoints below are not admitted integration surfaces. See host_derivative.md.

# Historical P0 source observations — runtime reuse superseded

WP-01 identifies the existing canonical host as `CollaborativeMinD/Multi-agent-Framework`
at commit `d9d5ae26f1351d87ffd19d2281bc14c103b39ee3`. Reuse its host authority and
`hmt_notebook_mcp.storage.BoardStore` at `<host-root>/state/hmt_state.sqlite3`.
The lane adapter must not provision a competing authorizer or task database.
This is a source-fit decision. Runtime qualification remains open.

## Exact namespace boundary

| Surface | Source-observed contract | Integration treatment |
| --- | --- | --- |
| Framework native | `tasks_list`, `memory_search`, `task_update`, `verify_task_board`, `working_agreement`, `rrca` | Wrap `hmt_notebook_mcp.endpoint.ToolEndpoint.call`; preserve native schemas and statuses. |
| Standalone baseline 1.1.0 | Twelve frozen tools in `hmt_baseline_tools.contracts.FROZEN_NAMES` | Reference implementations and explicitly admitted imports; not a second live task store. |
| Imported capabilities | `local://<name>` and `mcp://<server>/<tool>` | Bind through `CapabilityRuntime` with exact current contract/descriptor hashes and actual host actor. |
| Catalog additions | `git_lane`, `reference_build` | Separate resolved entrypoints; not native names merely because listed in the broader fourteen-entry catalog. |

Native task submission already requires `expected_revision` and `operation_id`.
Standalone `task_get` claims a task and therefore mutates state. The native RRCA
surface also has operation-dependent effects; opening/advancing a case is not a
read. Neither case activity nor completion submission grants DONE or repair authority.

## Existing admission path to retain

`ToolEndpoint.call` performs source/reference integrity checks and strict input
validation, then uses the projected scanner and Watchdog. Its isolated tool
process consumes signed admission and validates current projection/reservation;
the shared service checks projection again. The host owns principals, assignments,
leases, policy epoch, board revision, and task evidence. Transport does not provision them.

The imported capability runtime already checks current actor, current contract,
descriptor identity, and schema, and records UNKNOWN custody before invocation.
An unresolved matching fingerprint prevents a second claim. These are useful
reusable seams; they do not alone satisfy this build's stronger proof contracts.

## Blocking coupling gaps

| Gap | Evidence and required closure |
| --- | --- |
| `GAP-RECONCILE-PROOF-001` | `src/hmt_framework/capability_claims.py:reconcile` checks outcome enum and truthy evidence, then finishes. It does not authenticate endpoint proof or evaluate fresh authority. Reopen integration satisfaction claims HMT-B03/B04/F02. Do not expose this function as an agent/user API. Bind the existing transactional custody reserve/reconcile and endpoint `lookup_or_cancel` protocol with exact effect/reservation proof. Requirements remain unchanged. |
| `GAP-LANE-INTERSECTION-001` | Bind eight-lane/26-stage context, task ownership, actual credentials, roots, egress, and evidence into the existing host path; prove direct/MCP and hidden-call parity. |
| `GAP-POST-EFFECT-HOLD-001` | Standalone dispatcher audits after invocation. Audit failure may return HOLD after effect. Both completion paths deliver corrective files after task/receipt commit. Preserve effect identity and uncertainty, persist required delivery intent in the owning transaction, and never repeat a write because its wrapper returned HOLD. |
| `GAP-STANDALONE-AUTH-001` | Standalone mission-free reads return before scope checks; mission identifiers are caller-presented. Host-authenticated principal and evidence/root scope must fence every lane operation. |
| `GAP-REPLAY-RANGE-001` | Standalone event-chain verification is limited to 4096 rows. Report the verified range and continuation/total bound; never infer full-chain integrity. |
| `GAP-RESOURCE-PROFILE-001` | Existing capability payload bound is 16 KiB and subprocess address-space limits are 1–2 GiB. Preserve stricter valid request bounds; distinguish address space from RSS and qualify operation-specific profiles rather than silently weakening constraints. |

## Narrow tracer order

1. Bind actual existing host root, immutable source, principal, and one assigned task.
2. Exercise one native read through direct and MCP paths; revoke/change scope and
   prove denied calls produce no target effect.
3. Submit one exact candidate through native task_update, retaining operation ID,
   expected revision, native repair budget, actual gate invocation, and no self-DONE.
4. Inject effect-before-audit-failure and restart. Preserve the unresolved effect;
   require authenticated custody proof before reconciliation or any new attempt.
5. Exercise upstream/downstream changed-hash invalidation and report exact replay range.

## Evidence and nonclaims

`contracts/host_source_map.json` pins 32 inspected source artifacts. Twenty-one
remote source blobs were read at the exact commit and their Git blob SHA-1 values
were independently recomputed and matched; SHA-256 content identities are also
recorded. `evidence/host_reconciliation.json` separates observations, gaps, and unknowns.

No target code, host deployment, or command embedded in evidence was executed.
Actual deployment keys, principals, assignments, source installation/dependency
closure, and runtime witnesses remain unbound. This report establishes source
reconciliation for HMT-F01/F02/F03/F17/F20; it establishes no runtime satisfaction,
security certification, public redistribution clearance, or integrated readiness.
