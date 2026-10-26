# HMT RnD Environment

Build workspace for lane-scoped MCP interfaces, skills, and authenticated role contracts using repository-owned derivatives of read-only HMT references. Requirements baseline: `contracts/build_baseline.json` (0.2.0).

Preferred connected dictation: Wispr Flow. Local/offline transcription fallback: OpenAI Whisper through whisper.cpp. NVIDIA Parakeet is a future research candidate only.

Implementation is in progress. Repository-owned host, custody, voice, and verification derivatives are implemented. P1 adds real MCP stdio, generic 26-stage lifecycle sealing/reopening, atomic artifact-byte snapshots, and process-kill/causal witnesses. See `docs/build_plan.md`, `contracts/requirements.json`, and `Runbook.md`. No integrated mission-readiness or deployment claim is made.

All supplied HMT implementations are read-only references. This repository owns the derivatives and retains/extends the necessary behaviors and invariants; it does not depend on a separately deployed reference host.

Current out-of-band reconciliation checkpoint: 224 tests passed with zero failures/errors/skips. Changed first-party executable code covers 235/252 branches (93.25%) across 30 changed files, with zero exclusions. Ruff, Pyrefly basic, and structural gates passed. Global successor reservations and reopening policy/epoch authority have bounded repairs in commits `8a3f93a` and `0892ba2`. See `docs/oob_lane_reconciliation.md` and `evidence/oob_case_register.json`. Reconciliation HOLD remains pending the out-of-band supervisor's review of the exact candidate.

The previous twelve scoped case closures remain historical evidence in `docs/reconciliation_checkpoint.md` and `evidence/reconciliation_closure_register.json`. The two new findings explicitly reopen affected requirement evidence; passing prior scenarios does not establish their boundaries.

Integration remains on HOLD pending the owner's remaining instructions and outstanding qualification evidence. Full requirement assertion/mutation, domain, operational, vendor, and voice/UI qualification remain open. The earlier package-wide coverage claim did not establish the changed-code gate and is explicitly corrected; its historical evidence is retained. GitHub retains the owner's planning-only workflow; software verification runs under supervised local policy gates.
