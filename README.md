# HMT RnD Environment

Build workspace for lane-scoped MCP interfaces, skills, and authenticated role contracts using repository-owned derivatives of read-only HMT references. Requirements baseline: `contracts/build_baseline.json` (0.2.0).

Preferred connected dictation: Wispr Flow. Local/offline transcription fallback: OpenAI Whisper through whisper.cpp. NVIDIA Parakeet is a future research candidate only.

Implementation is in progress. Repository-owned host, custody, voice, and verification derivatives are implemented. P1 adds real MCP stdio, generic 26-stage lifecycle sealing/reopening, atomic artifact-byte snapshots, and process-kill/causal witnesses. See `docs/build_plan.md`, `contracts/requirements.json`, and `Runbook.md`. No integrated mission-readiness or deployment claim is made.

All supplied HMT implementations are read-only references. This repository owns the derivatives and retains/extends the necessary behaviors and invariants; it does not depend on a separately deployed reference host.

Current bounded path-identity checkpoint: 270 tests passed with zero failures/errors/skips. Changed first-party executable code covers 241/256 branches (94.14%) across 31 changed files, with zero exclusions. Ruff, Pyrefly basic, and structural gates passed. The reader rejects literal parent components in the original path and root before normalization, preventing the demonstrated evaluator/verifier byte mismatch. See `evidence/path_identity_case_register.json` and `docs/path_identity_reconciliation.md`. Reconciliation HOLD remains active.

Two separate review findings remain OPEN_REVIEW_HOLD: ancestor assignment freshness (`4383956251`) and drift detection resolving away symlink components (`4383956285`). They were not reproduced or refuted in the bounded path-identity campaign. No broader continuation or integration clearance follows from these passing tests.

The earlier successor-reservation and reopening policy/epoch repairs remain recorded in `evidence/oob_case_register.json`. Both earlier pending cases remain visible alongside the three latest cases; internal evidence does not release continuation.

The previous twelve scoped case closures remain historical evidence in `docs/reconciliation_checkpoint.md` and `evidence/reconciliation_closure_register.json`. The two new findings explicitly reopen affected requirement evidence; passing prior scenarios does not establish their boundaries.

Integration remains on HOLD pending the owner's remaining instructions and outstanding qualification evidence. Full requirement assertion/mutation, domain, operational, vendor, and voice/UI qualification remain open. The earlier package-wide coverage claim did not establish the changed-code gate and is explicitly corrected; its historical evidence is retained. GitHub retains the owner's planning-only workflow; software verification runs under supervised local policy gates.
