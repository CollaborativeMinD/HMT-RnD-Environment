# First-wave independent mission-assurance review

**Primary disposition: INSUFFICIENT_EVIDENCE for integrated acceptance.**

The reviewed baseline is 0.1.3. This is a skill-guided manual source/evidence review, not a newly executed mission-assurance evaluator report, security certification, or release authorization. The reviewer read source, JSON, CSV, and submitted execution records; no target code or tests were executed. Exact reviewed SHA-256 identities and UTC as-of time are in `evidence/assurance_review.json`.

## Reproduced coupling finding and repair

`MA-001` identified an exact-target gap: the initial custody Intent/storage had no endpoint binding, while reconciliation trusted any configured endpoint key. Source inspection alone prompted a falsifiable wrong-endpoint scenario. The custody worker then reproduced the failure and preserved raw failing JUnit in `evidence/custody_endpoint_incident.json`.

The current derivative requires `Intent.endpoint_id`, retains the target with immutable intent identity, rejects a wrong endpoint before its effect, and rejects a correctly signed wrong-target proof at reconciliation. The same initially failing test now passes, a direct proof negative was added, and nine cumulative custody cases pass in the submitted worker report. The previous seven-case record is retained in `evidence/custody_derivative_before_endpoint_fix.json`; no failing test was skipped or superseded. This is **REPAIRED_WITH_SCOPED_EXECUTION_EVIDENCE**, not full custody qualification. The reviewer did not execute the test or independently authenticate its producer.

## Supported boundaries and remaining evidence

| Area | Source/evidence supports | Required before broader qualification |
| --- | --- | --- |
| Voice | Admission removed from wire fields; trusted callback checked before assets and process; 18 submitted tests; draft-only authority NONE. | Actual host identity/guard binding, serialized revoke/dispatch, immutable asset/backend mounts, OS no-egress, live model/corpus/UI and timing evidence. |
| Verification | Read-only CSV count confirms 10,556 candidates, 189 applicable, 10,367 retained exclusions; all target statuses NOT_EXECUTED/NOT_APPLICABLE. Current requirements pin matches. | Per-requirement executable oracles, required target runs, critical mutation and causal-family closure, declared coverage and cumulative regression. |
| Host | Trusted identity/clock separate from wire; strict scope/revision/lease intersection; effect-authority NONE decisions; 18 submitted host tests. | Actual authenticated transport, all stages and completion firewall, OS/credential/root/egress enforcement, process/clock/hardware campaigns. |
| Host/custody | Both own local derivative behavior and support IMMEDIATE transactions; host provides transaction-aware clock checkpoint. | Prove actual same-file/same-connection composition and revoke/clock ordering; then interruption, rollback-anchor, endpoint and pressure campaigns. Independent endpoint domains have no instantaneous global revoke guarantee. |

Voice hash checks occur before later path use and are not themselves an immutable filesystem or network sandbox. The voice documentation accurately retains those host obligations. Ledger triggers and hashes likewise prove neither authenticity nor resistance to an adversarial filesystem owner. Two runners sharing tests/oracles are not independent implementation evidence.

All supplied HMT packages/frameworks remain read-only design references. The current source review does not establish a requirement to install a live reference host. Historical reference-engine observations are provenance/parity evidence only.

## Disposition limits

No reviewed artifact supports a full 58-requirement or integrated mission-readiness claim. A repaired exact-target counterexample supports only the bounded repair and associated regression set. Existing explicit qualification limits should remain visible in the PR and handoff. Later source/evidence changes invalidate only the affected snapshot findings and require reevaluation through the pinned change path.

## Read-only supervisor evidence addendum

The original as-of assessment above remains preserved. The later supervisor evidence in `evidence/supervisor_results.json`, `supervisor_tests.xml`, `coverage.json`, and `build_checkpoint.json` was inspected without executing target code. Raw JUnit records **94 tests, zero failures, errors, or skips**. Coverage metadata records **172/172 measured branches, zero excluded lines, and zero missing branches**. That denominator concerns current derivative code; it is not complete requirements or whole-system coverage. Ruff, basic-preset Pyrefly, and structural gates report successful exits.

Two cross-worker tests in `tests/test_host_custody_seam.py` now support part of MA-004: current host revocation blocks reconciliation while preserving OUTCOME_UNCERTAIN; a backwards host clock prevents reservation and leaves STAGED. The composition uses the same SQLite file and `authorize_and_checkpoint` on the custody-owned transaction connection. This closes the previously unreviewed local composition witness within those two scenarios. The endpoint remains a local simulation with a permissive endpoint authority callback.

**Primary disposition remains INSUFFICIENT_EVIDENCE for integrated acceptance.** Actual transport/session authentication, live Whisper/UI/OS enforcement, independent real-endpoint authority, process-kill and rollback/hardware, full lifecycle, pressure, mutation, and causal families remain outside this scoped evidence. Exact addendum hashes and UTC time are retained in `evidence/assurance_review.json`.
