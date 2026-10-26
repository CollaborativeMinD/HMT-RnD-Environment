# HMT RnD Environment

Build workspace for lane-scoped MCP interfaces, skills, and authenticated role contracts over existing HMT kernels. Requirements baseline: `contracts/build_baseline.json` (0.2.0).

Preferred connected dictation: Wispr Flow. Local/offline transcription fallback: OpenAI Whisper through whisper.cpp. NVIDIA Parakeet is a future research candidate only.

Implementation is in progress. Repository-owned host, custody, voice, and verification derivatives are implemented. P1 adds real MCP stdio, generic 26-stage lifecycle sealing/reopening, atomic artifact-byte snapshots, and process-kill/causal witnesses. See `docs/build_plan.md`, `contracts/requirements.json`, and `Runbook.md`. No integrated mission-readiness or deployment claim is made.

All supplied HMT implementations are read-only references. This repository owns the derivatives and retains/extends the necessary behaviors and invariants; it does not depend on a separately deployed reference host.

Current cumulative checkpoint: 159 tests passed; 290/308 measured branches covered (94.16%), no exclusions; Ruff, Pyrefly basic, and structural gates passed. See `docs/p1_checkpoint.md` for scope and nonclaims. GitHub retains the planning-only workflow requested by the owner; software verification is run by the supervised build.
