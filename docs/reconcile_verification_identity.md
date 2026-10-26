# Canonical candidate identity reconciliation

R-VERIFY-ID-001 supports the bounded identity/materialization portion of HMT-N10 and failure preservation under HMT-B11. It does not qualify the entire requirement set.

The original regression reproduced the review finding: raw `HMT-F01` and `I-F01` passed validation, then SQL normalized both to the same candidate identity and failed after creating the destination. The failing log, JUnit and exact pre-fix source snapshots are retained in `evidence/reconcile_verification_identity_before*`.

The derivative now rejects canonical collisions in `Dimensions`, before destination creation. Existing normalization and candidate IDs remain unchanged. All 29 focused verification tests pass, including the same formerly failing oracle. A regenerated full baseline product matches every historical candidate row: 10,556 candidates, 189 applicable, 10,367 inapplicable with predicates. No requirement is relabeled satisfied.

To reproduce, run `uv run pytest -q tests/test_verification_*.py tests/test_reconcile_verification_identity.py`. Inspect the case record and parity evidence; do not replace historical failed witnesses. A failure keeps this package on HOLD. Supervisor cumulative gates and independent evidence review remain necessary for closure.
