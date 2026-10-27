# WP-01 local inspection binding milestone

The configured `InspectionSurface` exercises the existing `inspect_context`
operation through direct calls and actual SDK stdio sessions. HMT-F01/F20 are the
governing requirements; WP-08 supplies the falsifiers. The pinned work packet is
`contracts/WP-01-LOCAL-INSPECT-001.json`.

The native inspection body is extracted unchanged into one shared function.
The adapter validates a closed descriptor, its nine-file native/admission source
spine, native schema hashes, exact launch-context hash, credential reference,
local destination, policy/epoch, validity interval and resource limits. It calls
the existing `authorize_and_checkpoint` kernel within the existing host database.
No replacement authorizer or task store is introduced.

The native Decision response is unchanged and grants no effects. The operation
is classified LOCAL_MUTATION because it checkpoints the host clock and appends
an immutable inspection receipt in the same transaction. A separate test observer
records actual native dispatch/result hashes. Receipt failure rolls back database
state while preserving the observation that native inspection ran.

Missing, conflicting and stale bindings cause zero observed native dispatch and
zero committed invocation changes in direct/MCP tests. Discovery is a projection:
it performs admission clock bookkeeping but no native inspection or operation
receipt. Current host revocation/revision/policy checks still fence cached tools.

The original legacy tracer retains eight failures and one positive control against
the new binding requirement. This is a qualification gap in the earlier raw surface,
not a claim that its former native contract promised capability descriptors. The
test-only legacy backend is explicit; production has no such fallback.

The isolated suite passes 545 tests, retaining all prior 465 IDs. Eighty new cases,
27 existing verification unittest cases, static checks, four critical mutants and
six causal arms are recorded. Changed production/script branches are 296/314
(94.27%), zero exclusions. Complete N11 and full work-package acceptance remain open.

`evidence/inspection_positive_receipt_export.json` contains actual direct/MCP
results, native dispatch observations, synthetic launch/grant/assignment context,
exact receipt rows/digests and before/after clock state. These are public synthetic
fixtures with inert credential references. The producer is not independently
authenticated; hashes prove byte consistency, not authenticity.

The default launcher still routes to its existing LaneSurface. Its protected
descriptor reader is shared with the test-only configured launcher. No provider,
credential expansion, rollout or default activation occurs. The generic vendor
binding register is untouched. Production identity/clock, OS/network isolation,
latency/resources, recovery and complete mission qualification remain unproved.
All eleven full work packages remain open. No integration, merge or deployment.
