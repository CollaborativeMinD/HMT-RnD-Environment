# Cancelled-effect input identity reconciliation

RC-CUSTODY-001 supports the input-identity boundary of HMT-B04, with HMT-B03/F10 regressions. It does not release the owner HOLD or qualify the complete requirement.

At parent `9f2d3bf7db042cd400b57ee78c288ca32342d9f3`, an admitted cancellation stored input A only against its reservation. A fresh reservation carrying input B bypassed that row and found no committed effect to compare. The endpoint then either committed B or recorded a conflicting cancellation. Four failing cases cover apply/cancel before and after endpoint restart; actual SQLite rows and exact original source are retained.

The derivative now checks historical reservation digests inside the same authority-fenced transaction before effect/cancellation mutation. The original cancellation fence, proof/reservation matching, endpoint scope, deduplication, and fresh authority checks remain. No reference implementation was changed or imported.

| Gate | Required observation | Result |
| --- | --- | --- |
| G-CUSTODY-INPUT-001 | Changed input rejects before a new effect or reservation row | Four formerly failing cases pass |
| G-CUSTODY-RETRY-002 | Same-input retry succeeds once after restart; old request/proof remain fenced | Pass |
| G-CUSTODY-AUTH-003 | Other effect independent; revoked endpoint retry denied, local uncertainty retained | Pass |
| G-CUSTODY-REGRESSION-004 | Existing custody, host seam, causal and process-kill tests retained | 34 total pass |

Focused replay: `uv run pytest -q tests/test_reconcile_custody_identity.py tests/test_custody*.py tests/test_host_custody_seam.py tests/test_causal_authority_family.py tests/test_temporal_process.py`.

`evidence/reconcile_custody_case.json` binds source hashes, commands, raw witnesses, causal trace, limits and worker attestation. The matching eight-column RRCA ledger is exported as CSV and SQLite. Ruff, basic Pyrefly and structural gates pass. Complete HMT-B04 deadline/budget behavior, production endpoints and large-history latency remain unqualified. Status: `INVESTIGATION_COMPLETE; SOLUTION_CANDIDATE_APPLIED; PENDING_SUPERVISOR_RECONCILIATION`.
