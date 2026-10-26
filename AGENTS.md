# Build contract

User-authorized build in this repository. Read contracts/requirements.json and assigned package before coding. Reuse canonical kernels through explicit interfaces; do not invent a second task store or authorizer. Never publish source bundles, credentials, or proprietary method implementations. Record provenance and unresolved seams.

Functions physical span >=60 lines BLOCK; 50-59 refactor required; 45-49 WATCH. Modules >=121 physical lines BLOCK; 101-120 refactor required; 80-100 WATCH. Keep new modules under 80 lines where practical. uv only, strict Pydantic v2, Ruff/Pyrefly. No skip/xfail/expectedFailure or swallowed failure. Tracer first; actual negative/causal/restart witnesses before satisfaction claims.

Workers own only assigned paths; no shared-config edits, commits, pushes, or additional delegation without supervisor instruction. Host identity and current authority required before effects. HOLD never selects another provider; unresolved writes remain uncertain. Preserve effect identity, original deadline, and shared retry budget. RRCA/assurance evaluate evidence and cannot repair/promote.

Each worker returns task ID, source identities, changed paths, commands/results, requirements supported, unknowns, coupling contradictions, and artifact digests. Supervisor records eighth-column sub_agent_task_attestation. No model self-DONE or unsupported full-readiness claim.

USER OVERRIDE CR-REFERENCE-DERIVATION-003: all supplied HMT implementations are READ-ONLY REFERENCES. Form owned derivatives by retaining/extending needed behavior/invariants. No runtime imports from reference packages or required reference deployment. Preserve source provenance and matched observations. Canonical means one derivative implementation per shared capability, not the old live reference surface.
