# P1 integration checkpoint

All supplied HMT packages remain read-only references. No reference implementation is imported at runtime.

## Implemented and exercised

- Real MCP stdio sessions using pinned official SDK2.3.0, host-bound launch context, fresh tool visibility/invocation admission, closed tool schemas, bounded input before parsing, and role/task-bound handoff validation. Two public tools are exposed: inspect_context and validate_handoff. Lifecycle mutation is not exposed without a qualified domain evaluator.
- Generic eight-lane/26-stage lifecycle contracts, immutable SEALED/DENIED receipts, host-bound gate evaluator, current predecessor/policy/task checks, typed earliest-owner reopening, and atomic bounded content-addressed artifact/evidence snapshots.
- Six-arm authority causal family including alternate endpoint compensation, plus actual subprocess kills before dispatch and after endpoint commit. Revoked restart work is denied and fresh authority reconciles exact fixture proofs without repeating effects.
- Live local Whisper smoke sample via our voice adapter: 11-second public fixture, pinned base.en/whisper.cpp,22/22 normalized reference words,3.896seconds wall time on this worker, inherited selected-socket seccomp denial. No corpus or userhardware qualification inferred.

## Cumulative verification

159 tests passed;290/308 measured branches=94.1558%;zero coverage exclusions. Ruff, Pyrefly basic, and structural gates passed. Coverage includes attempted subprocess collection; remaining uncovered branches remain visible. See evidence/p1_supervisor_results.json and raw JUnit/coverage. Independent assurance remains scoped; complete integrated acceptance is INSUFFICIENT_EVIDENCE.

## Still open

Actual domain evaluators for all lifecycle stages, complete task-tool/role/skill derivatives, production identity/credential/clock and OS isolation, performance/history-growth campaigns, the full189-case target-oracle map, real vendor endpoints, complete voice corpus/microphone/UI qualification, and deployment/release. No model self-DONE or fixture substitution is permitted.
