# Operator runbook

Use uv only. From this repository:

```bash
uv sync --group dev
uv run --group dev python -m pytest -q
uv run --group dev ruff check src tests
```

Read evidence and source maps before qualifying any derivative. Supplied HMT implementations are read-only design references, with provenance retained separately. Their installation or availability is not a runtime requirement. Only explicitly selected operational dependencies, such as the Whisper binary/model, must be bound at use.

Whisper runtime/model are supplied and pinned by the host. No model download occurs during inference. Transcripts enter a draft; submission and task authority remain separate.

HOLD, revoked authority, and semantic denial stop fallback. External effect uncertainty requires exact-effect reconciliation. No operator should repeat a write merely because its receipt is missing.

Troubleshoot by preserving the failing command, candidate/source/policy identities, actual observations, and cumulative ledger. Contradictory assumptions reopen requirements through the controlled change path.

## Derivative qualification

All supplied HMT implementations are read-only references. Runtime imports from reference packages are forbidden; repository-owned derivatives retain and extend the admitted behaviors. No reference installation is required for the portable suite. See docs/host_derivative.md and docs/custody_adapter.md for the transaction and proof domains.

The five earlier engine tests in evidence/custody_reference_parity.json are historical reference observations only; current derivative tests live under tests/test_custody*.py. They do not establish vendor, process-kill, power-loss or hardware fidelity.

Run full source type checks with `uv run --group dev pyrefly check src`. The prior missing-reference-import failure is retained as historical evidence of the corrected dependency interpretation.
