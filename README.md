# HMT RnD Environment

Build workspace for lane-scoped MCP interfaces, skills, and authenticated role contracts over existing HMT kernels. Requirements baseline: `contracts/build_baseline.json` (0.1.3).

Preferred connected dictation: Wispr Flow. Local/offline transcription fallback: OpenAI Whisper through whisper.cpp. NVIDIA Parakeet is a future research candidate only.

Implementation is in progress. Host reconciliation, custody tracers, verification gates, and the local voice adapter are being built before broader lane integration. See `docs/build_plan.md`, `contracts/requirements.json`, and `Runbook.md`. No integrated mission-readiness or deployment claim is made.

All supplied HMT implementations are read-only references. This repository owns the derivatives and retains/extends the necessary behaviors and invariants; it does not depend on a separately deployed reference host.
