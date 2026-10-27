# HMT RnD Environment

Build workspace for lane-scoped MCP interfaces, skills, and authenticated role contracts using repository-owned derivatives of read-only HMT references. Requirements baseline: `contracts/build_baseline.json` (0.2.0).

Preferred connected dictation: Wispr Flow. Local/offline transcription fallback: OpenAI Whisper through whisper.cpp. NVIDIA Parakeet is a future research candidate only.

Implementation is in progress. Repository-owned host, custody, voice, and verification derivatives are implemented. P1 adds real MCP stdio, generic 26-stage lifecycle sealing/reopening, atomic artifact-byte snapshots, and process-kill/causal witnesses. See `docs/build_plan.md`, `contracts/requirements.json`, and `Runbook.md`. No integrated mission-readiness or deployment claim is made.

All supplied HMT implementations are read-only references. This repository owns the derivatives and retains/extends the necessary behaviors and invariants; it does not depend on a separately deployed reference host.

Current bounded reconciliation checkpoint: 339 tests passed with zero failures/errors/skips. Changed first-party executable code covers 243/258 branches (94.19%) across 31 changed files, with zero exclusions. Ruff, Pyrefly basic, and structural gates passed. Every ancestor's principal/revision must match its current assignment before/after evaluation and before reopening insertion. Drift detection sends original paths through the guarded reader and recognizes only missing descendants below a valid root as missing-source drift. See `evidence/remaining_holds_case_register.json` and the ancestor/drift reconciliation documents. Outside review remains pending; integration is blocked.

Review findings `4383956251` and `4383956285` are now reproduced and repaired as RC-ANCESTOR-01 and RC-DRIFT-01, with their original failures retained. Their status is REPAIR_VERIFIED_HOLD_PENDING_OUT_OF_BAND_REVIEW. Internal evidence does not release continuation or imply full requirement satisfaction. The prior path-identity checkpoint remains preserved as historical evidence.

Earlier repairs and their pending review states remain preserved in the historical case registers; the current register retains those records. Internal evidence does not release continuation.

The previous twelve scoped case closures remain historical evidence in `docs/reconciliation_checkpoint.md` and `evidence/reconciliation_closure_register.json`. The two new findings explicitly reopen affected requirement evidence; passing prior scenarios does not establish their boundaries.

Integration remains on HOLD pending the owner's remaining instructions and outstanding qualification evidence. Full requirement assertion/mutation, domain, operational, vendor, and voice/UI qualification remain open. The earlier package-wide coverage claim did not establish the changed-code gate and is explicitly corrected; its historical evidence is retained. GitHub retains the owner's planning-only workflow; software verification runs under supervised local policy gates.
