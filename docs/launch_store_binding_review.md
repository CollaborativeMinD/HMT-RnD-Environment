# RC-LAUNCH-STORE-01 — reproduced; acceptance HOLD

Examined executable candidate: `608d6460384b841c8617dcda22b55fce2f2387a6`.
No production code, default routing, requirements, or acceptance status changed.

The closed launch digest binds the *text* of `LaneBinding.store`. That field accepts a
relative path. `LaneSurface.__init__` passes that text to `HostStore`, whose constructor
uses `path.resolve()` against the current working directory. Consequently identical
launch bytes can identify different authority databases when a surface is reconstructed
or its MCP process restarts in another directory. An already constructed HostStore
retains its resolved absolute path; this witness does not claim an existing instance
switches databases merely because its process changes directory.

The synthetic fixture provisions two separate SQLite databases from one authorized
fixture, then revokes the principal only in the intended authority database. Both
contain the same task, policy and epoch; the alternate retains its grant. Their common
resource root is absolute. This deliberately isolates the store-path binding from
root-path interpretation. There are no real credentials or external effects.

Eight bounded cases personally executed: direct and real SDK stdio, relative and
absolute store paths, original and alternate working directories. Each case first
executes the same launch in the original directory and observes denial. It then
reuses the unchanged launch after the directory selection. Both relative/alternate
cases violate the denial assertion: one native dispatch and one receipt in the
alternate database. The other six cases deny, with zero dispatch, zero receipts,
and unchanged full SQL snapshots of both databases. The intended database remains
unchanged in the two counterexamples too. Receipt tables are provisioned before the
snapshots so initialization is not mistaken for an operation effect.

Raw failures are intentional evidence of the unresolved contract, outside normal test
discovery. They must not be relabeled passes or skipped. Run from repository root:

```sh
PYTHONPATH=src:tests:evidence/launch_store uv run pytest evidence/launch_store/cases.py -q --junitxml=evidence/launch_store/baseline.xml
```

See `evidence/launch_store/baseline.xml`, `.log`, and the eight JSON exports containing
actual responses, independent native markers, exact receipt rows, unchanged launch
configuration, and before/after SQL dumps. First-run failures and the initial Ruff
unused-import finding remain preserved. The final fixture preinitializes receipt
tables; no denial expectation was relaxed. Ruff passes after removing that import.

HMT-F01's single resolved authority binding and HMT-F20's capability binding remain
unqualified at this seam. Owner: Host/IIEA; verification owner: root/WP-08. Failure
disposition: OPEN_REVIEW_HOLD on this binding milestone; no integration or promotion.
Prior absolute-path observations remain valid within their tested scope. A passing
historical cumulative suite is not a refutation of these new counterexamples.

This packet is a bounded reproduction, not a repair or independent acceptance.
Potential repair must establish store identity before launch sealing (or reject
relative stores), preserve direct/MCP behavior and native authority, and prove restart
and denial controls. Merely normalizing during surface construction still depends on
that construction's working directory and does not close this finding. Symlink/file
replacement, authenticated database provenance and broader root-path qualification
remain outside this witness; no claim of them being resolved is made.
