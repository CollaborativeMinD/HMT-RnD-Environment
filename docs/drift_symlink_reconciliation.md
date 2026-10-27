# RC-DRIFT-01: preserve source denials during drift detection

At baseline `608e3bdf95e07ded956ef1b80a0d2e0376f8efbe`, the original guarded digest rejected a symlink, but drift detection resolved the pathname first. Four artifact/evidence live/dangling-link cases then returned drift and admitted a reopen with an invalidation and a clock update. Six further cases admitted invalidations when the forbidden source was undeclared earlier work, undeclared later work, or evidence following an already changed artifact. These failures and complete database-state fingerprints are retained. A separate baseline control showed that an unavailable root was also treated as a missing source.

The repair passes the **original path and root** to the guarded digest. Only a scope failure whose immediate underlying cause is a genuine `FileNotFoundError` can represent missing-source drift. Symlink, parent traversal, regular-file type, byte-bound and other scope denials propagate unchanged. Every artifact/evidence source is still evaluated, so an earlier change cannot mask a later denied source.

The supervisor approved a companion change in the existing descriptor walker: an absent component within the declared root prefix becomes a root-scope failure. Missing descendants strictly below a valid root retain their missing-file cause. Failed normalization context likewise remains a scope failure. This uses the existing no-follow traversal, with no additional racy stat/probe. A valid filesystem root `/` and absent nested directories beneath a valid root retain missing-source support.

| Gate | Observed boundary |
| --- | --- |
| G-DRIFT-DECLARED-001 | Original artifact/evidence symlink denials propagate through explicit reopening; all database state, snapshots and clock remain unchanged |
| G-DRIFT-DISCOVERY-002 | Undeclared earlier/later sources and later evidence cannot be masked by an earlier changed artifact |
| G-DRIFT-ROOT-003 | Invalid roots deny; genuine absent descendants under a valid root remain drift |
| G-DRIFT-POLICY-004 | Out-of-scope/final/parent links, original `..`, FIFO and directory sources remain denied |
| G-DRIFT-RECOVERY-005 | Actual missing artifact/evidence still routes to the earliest owner; restart, typed successor and downstream regeneration succeed while old snapshot bytes remain preserved |

The retained baseline has eleven failures and two valid missing-source controls. The repaired focused suite has 27 passes. Both the shared-workspace run and the supervisor's isolated step-B replay passed 319 tests with unchanged source/test inventory and zero failures/errors/skips; they include the separate ancestor worker's initial repair. All-source Ruff, basic Pyrefly and structural gates pass. The exact isolated record is `remaining_supervisor_drift_symlink_snapshot.json`. Subsequent ancestor issuance work is a separate change and is not qualified by this record.

`drift_symlink_snapshot.json` freezes the two source files and focused tests. Raw baseline and repaired observations, complete state fingerprints, source hashes, and eight-column RRCA/cumulative exports accompany the case report. Replay with `uv run pytest -q tests/test_drift_symlink*.py` and then the full suite.

These observations support bounded HMT-B07 drift/reopening, HMT-N04 root scope, HMT-F03 rejection and HMT-B14 host-write continuity checks. They do not qualify general filesystem sandboxing, an immutable filesystem, complete requirements, or other ancestor-authority findings. **HOLD remains pending out-of-band review; integration and deployment remain withheld.**
