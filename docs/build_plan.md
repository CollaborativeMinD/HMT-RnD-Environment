# Build execution plan

Baseline 0.1.2 adds the approved OpenAI Whisper local fallback to v0.1.1. NVIDIA Parakeet remains documentation-only. The clean repository is the integration delivery target; the existing framework remains the canonical host candidate.

Wave 1: WP-01 source/host reconciliation; WP-03 existing-custody adapter and tracer; WP-08 verification gates; WP-11 local transcription adapter. These independent source/tracer tasks may proceed together. No worker can claim dependent runtime integration before prerequisite source/authority qualification.

Next: bind canonical host interfaces and admitted source providers, per-lane MCP projections, role/skill derivatives, target-specific oracles and actual endpoint evidence. Preserve unresolved bindings explicitly; no fixture may satisfy a live-vendor/hardware claim.

The existing requirements, V&V, dependency and binding registers govern acceptance. Every contradiction reopens exact affected requirements; original failures and expectations remain.

## Authoritative correction CR-REFERENCE-DERIVATION-003

All supplied HMT artifacts are read-only reference implementations, not runtime services or installable build dependencies. Retain/extend needed behaviors and invariants into repository-owned derivatives. Earlier source-fit recommendations to call BoardStore/ToolEndpoint or import hmt_custody are superseded as runtime decisions; their source observations remain evidence. The derivative owns a single authority/task store and composes custody tables within the same local SQLite authority domain for atomic fencing. Endpoint domains remain separately scoped.

Per-attempt fresh guard and authenticated reconciliation are required derivative behaviors. A weakness in reference code is a delta to implement and prove, not a requirement waiver or a reason to require reference modification. Selected external engines/services (such as Whisper model inference) remain explicit functional dependencies under their operation contract; HMT reference packages do not.
