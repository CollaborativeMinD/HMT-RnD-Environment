# RC-PATH-01: original pathname identity

The reported identity split is reproduced at `3492b6f2f86f7757706d470a0f5e119c1069d013`. This bounded repair remains on HOLD pending out-of-band review. It does not close the separate ancestor-assignment or drift-resolution findings.

With `scope/jump` linked to `outside/child`, the original `scope/jump/../source` reads the synthetic outside bytes. The old guarded reader first applied `abspath()`, erased the parent component, and read `scope/source`. Independent digest and snapshot calls selected the inside bytes. An actual `LaneStore.submit` passed the original pathname to a controlled evaluator, which observed outside bytes and returned `SEALED`; the receipt's artifact snapshot contained inside bytes. Exact byte strings, hashes, database counts, source and test identities are preserved in `path_identity_baseline.json` and the three failing test records.

The evidenced causal frontier is the two interpretations of the original pathname. No filesystem race is required. The repair adds two lines in `lane_reader.scoped_descriptor`: reject literal `..` components in the original input path **or root before normalization or descriptor opening**. Existing no-follow traversal, regular-file checking, byte limits, caller-native scope reasons, and snapshot digest checks remain.

This deliberately rejects ordinary parent traversal as well, even when it would reach the same in-scope file. Canonical paths and relative paths without parent components remain supported. No caller input is silently rewritten into an apparently safe identity.

| Gate | Required observation | Worker evidence |
| --- | --- | --- |
| G-PATH-IDENTITY-001 | Symlink-plus-parent path denied by digest and snapshot | Retained two baseline failures; matching repaired typed scope denials |
| G-PATH-SUBMISSION-002 | Artifact denial precedes evaluator; no receipt/blob/closure or clock mutation | Retained baseline wrong-byte seal; repaired evaluator count zero and identical before/after state |
| G-PATH-POLICY-003 | Original path and root parent components rejected before normalization/open | Plain-directory and symlink fixtures; forbidden normalization/open witnesses |
| G-PATH-PARITY-004 | Canonical and relative artifact/evaluator/snapshot bytes remain identical | Successful actual submissions and snapshot rereads after restart |
| G-PATH-REVOKE-005 | Host revoke proceeds after denial; revoked restart remains denied | Exact `HOST_GRANT_DENIED`, no evaluator call or lifecycle mutation |

The initial implementation and tests passed 270 tests, including the prior 255, with an unchanged source inventory across that run. Ruff then identified one 101-column import layout issue in the tracer. Its failure and original frozen snapshot are retained. V2 changes only that import layout, passes 15 focused cases, all-source Ruff, and structural checks; production Pyrefly basic passes. The supervisor independently replayed exact V2: 270 tests pass with unchanged source inventory and zero skips. Changed-code branch coverage is 241/256 (94.14%), with zero exclusions; full HMT-N11 remains unqualified. The source commit is `fa8161270454ec3697bcaa5a1e26d0a6ad62e6c9`; this replay is distinct from the retained pre-format run.

`path_identity_snapshot_v2.json` contains the frozen candidate and references the original snapshot hash. `path_identity_summary.json`, raw observations, source inventories, and eight-column RRCA/cumulative exports bind the evidence. No test oracle was weakened or superseded. Replay the focused cases with `uv run pytest -q tests/test_path_identity*.py`.

Requirements are linked only at their observed boundaries: HMT-F01 identity consistency, HMT-F03 pre-evaluation rejection, HMT-N04 root scope, and HMT-B07 sealed artifact identity. These tests do not establish complete requirements satisfaction or general filesystem sandboxing. Findings `4383956251` and `4383956285` remain separate `OPEN_REVIEW_HOLD` items; their source files are unchanged by this case.
