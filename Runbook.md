# Operator runbook

Use uv only. From this repository:

```bash
uv sync --group dev
uv run --group dev python -m pytest -q
uv run --group dev ruff check src tests
```

Read evidence and source maps before qualifying any adapter. Private inherited source packages are referenced through explicit paths and digest checks; they are not bundled or silently downloaded. Missing configured source blocks the dependent operation.

Whisper runtime/model are supplied and pinned by the host. No model download occurs during inference. Transcripts enter a draft; submission and task authority remain separate.

HOLD, revoked authority, and semantic denial stop fallback. External effect uncertainty requires exact-effect reconciliation. No operator should repeat a write merely because its receipt is missing.

Troubleshoot by preserving the failing command, candidate/source/policy identities, actual observations, and cumulative ledger. Contradictory assumptions reopen requirements through the controlled change path.

## External-source qualification

The portable test suite does not claim execution of the five canonical custody cases. Their complete required collection is listed in evidence/custody_qualification_manifest.json. Missing private source is HOLD for that qualification, never a skip or PASS. Bind HMT_CUSTODY_REFERENCE to the exact source reviewed in evidence/custody_tracer.json, then run:

```bash
PYTHONPATH="src:tests:$HMT_CUSTODY_REFERENCE/src" uv run --frozen --group dev python -m pytest tests/custody_uncertainty.py tests/custody_guards.py -q
```

Full source type checking likewise requires the canonical custody import root via Pyrefly --search-path. Initial missing-import failure is preserved in evidence/supervisor_results.json. No suppression resolves the missing dependency.
