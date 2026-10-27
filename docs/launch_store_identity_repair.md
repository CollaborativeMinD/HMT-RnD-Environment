# RC-LAUNCH-STORE-01 — repair candidate; outside acceptance pending

Host/IIEA owns this repair under HMT-F01/F20. The existing requirement is one
unambiguous serialized authority/resource identity, checked before opening a store.
HMT-F02/B01 cover fresh authority across restart; HMT-B10/B11/B12 and N11/N12 govern
retained contradictions, matched falsification, causal evidence, and source custody.
No requirement acceptance threshold or authority owner changes.

`LaneBinding` now requires both `store` and `root` to be absolute paths. It returns
valid paths unchanged and rejects relative values with
`MCP_BINDING_PATH_NOT_ABSOLUTE`. It performs no filesystem lookup or cwd-dependent
normalization. Serialization therefore contains only admitted absolute identities.
Both the protected default launch loader and configured inspection launch use this
shared model; `LaneSurface` revalidates its input before constructing `HostStore`,
including an instance forged with `model_construct`. There is no new authorizer,
store, fallback, or startup migration.

Provision explicit absolute store/root identities through the trusted host before
sealing the launch and capability digest. If an old launch is relative, keep it as
failure evidence and request a corrected host-owned launch. Do not guess a base,
resolve against startup cwd, rewrite receipts, or retry under a different store.
This narrows admitted input within the existing identity-binding requirement.

## Personally executed witnesses

The original stale-copy packet `evidence/launch_store/*` remains byte-for-byte
unchanged from `f0f6115b745a26071650c5a8b6c54c65c39aa5bd`: same launch text, intended
revoked database, alternate authorized copy, two native executions/alternate
receipts after cwd reconstruction. Its original two denial failures and six
controls remain failures and controls in history. Nothing was overwritten.

New falsifiers retain that mechanism but inject raw serialized fields before model
admission. This is necessary because the repaired model rejects those fields before
the old witness helper can construct its previously accepted relative binding.
The `store=host.sqlite`, alternate-cwd, direct/MCP cases are the matched repair
assertions. They require zero attempted HostStore construction, zero native
dispatch, unchanged launch bytes, and unchanged full SQL snapshots of both stores.
The initial 32 failures are *pre-open contract failures*, not 32 demonstrated
successful exploits. All original stale-copy exploitation claims remain limited
to the two preserved cases.

The same assertions also cover root/store empty, dot, relative filename, and parent
spellings in both directories and transports. Four absolute controls each reuse
identical launch bytes through two fresh direct surfaces or real SDK processes.
Authorized controls return the same native Decision twice and create two receipts
only in the intended store. Revoked controls deny twice, with no dispatch, receipt,
or SQL state change; the alternate authorized copy stays untouched.

Shared-boundary cases cover Python and JSON input, forged model instances, the
protected default loader, and the actual default stdio entrypoint. They demonstrate
rejection before store creation or protocol output. These are bounded synthetic
fixtures, not production identity or OS containment qualification.

Replay the cumulative repair assertions from the repository root:

```sh
uv run pytest tests/test_launch_identity*.py -q
```

The causal family uses four matched alternate-directory cases: intact, deletion,
restoration, sham, independent boundary compensation on, and compensation off.
The compensation guard is a controlled fault-study overlay, not production code.
Its enabled arm shows redundancy can hide a removed primary guard. Disabling both
restores all four failures. Separate store-only/root-only deletion mutants each
fail the two corresponding cases while preserving the other two.
`evidence/launch_store_repair/causal_family.json` contains exact overlays and argv.

See `evidence/launch_store_repair/case.json` for final counts, source identities,
requirement/assertion/evidence links, retained development failures, and limits.
Native operation output, canonical admission, SQL transaction/receipt behavior,
protected file loading, and launcher routing remain unchanged. File replacement,
symlink races, database authenticity, migration, and distributed identity remain
outside this cwd-independence claim. All whole-package obligations stay open.
No integration, merge, deployment, or default adapter activation is authorized.
