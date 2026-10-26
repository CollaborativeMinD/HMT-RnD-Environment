# Bounded verification utilities

WP-08 implements three bounded seams: conservative physical LOC classification,
known test-suppression/collection checks, and a complete SQL candidate ledger.
These utilities do not establish target requirement satisfaction.

## Source and authority

The implementation derives from the v0.1.1 planning policy and current repository
requirement records. `evidence/verification_results.json` binds the exact input hash.
The current requirement set has 58 invariants, 14 declared mechanisms, and 13 gates:
10,556 candidates, 189 applicable, and 10,367 retained exclusions.

Candidate identities preserve the existing `I-F01__M00__G-ARCH` convention.
Unbound mechanism identities fail before destination creation. Applicability is a
reviewed design predicate, not an experimental proof of irrelevance. Every applicable
candidate remains `NOT_EXECUTED`; no generic PASS flag is accepted or generated.

## Usage and verification

Run from the repository root with uv. The src package must be installed, or explicitly
placed on the import path:

```bash
PYTHONPATH=src uv run --with pytest --with pydantic python -m pytest tests/test_verification_complexity.py tests/test_verification_suppression.py tests/test_verification_ledger.py tests/test_verification_identity.py -q
PYTHONPATH=src uv run --with pydantic python -m unittest discover -s tests -p 'test_verification*.py' -v
uv run --with ruff ruff check src/hmt_rnd/verification_*.py tests/test_verification*.py
```

Tests exercise exact LOC boundaries, decorator/comment/blank/nested-function spans,
syntax failure, suppression aliases, absent/duplicate collection or execution,
retained Cartesian exclusions, deletion/update/fabricated-PASS mutations, tampered
bytes, existing destination refusal, preflight cardinality, and stable identities.
The two runners execute shared tests; agreement is not independent oracle evidence.

## Ledger custody

`create_ledger` requires validated frozen Pydantic dimensions and exclusively creates
a new path. It checks product cardinality before creation, bounds input acceptance
text, materializes the full SQL CROSS JOIN, verifies row count, and installs write
rejection triggers. A ledger exceeding 64 MiB returns failure. Failed creation may
leave a partial artifact: retain it as failed evidence and use a new path, never
accept it without a successful returned seal. It does not overwrite prior ledgers.

The SHA-256 must be held separately by a trusted owner. Triggers resist accidental
DML; an owner who can alter the schema/file can bypass them. Integrity hashes are
not signatures, authenticity, filesystem immutability, or protection from an
adversarial host. Reopen dimensions explicitly and create a successor artifact.

## Qualification gaps and contradiction handling

The baseline maps broad requirement acceptance prose to assertion IDs. It does not
yet supply requirement-specific executable oracles for every acceptance clause.
That remains a target-harness blocker; metadata completeness cannot close it.

The static suppression detector covers known syntax; dynamic monkeypatching or
disabled CI invocations require collection/result manifests and mutation tests.
Physical LOC checks do not replace inherited structural-engine checks.

Integration source review also identified guard freshness and reconciliation-proof
gaps: the fallback source does not recheck its guard on every attempt, while the
framework reconciliation surface accepts an enum plus truthy evidence. These are
upstream integration claims to reopen and prove, never grounds to waive requirements.

The initial unittest invocation lacked the src package path and failed import.
The corrected command above passed without changing or superseding any test.
Both failed and repaired invocation results are retained in verification evidence.
