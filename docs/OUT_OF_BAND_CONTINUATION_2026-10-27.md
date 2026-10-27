# Bounded engineering continuation after out-of-band review

## Authority and disposition

Owner requested this committed continuation order on 2026-10-27 after review. Accepted source candidate: `75531706c4986536e88b2edfb49e42281ea954ef`, RC-RECEIPT-PATH-01. This documentation-only commit does not change executable code or requirement revisions. Earlier scoped acceptances 6432712455 and 6433215377 remain intact.

The new-receipt path repair is accepted for bounded engineering continuation. Original guarded reads and snapshot preservation precede absolute path spelling; final clock/admission still follows all of that work before mutation. Independent source/evidence review reconciled 30 retained original failures and 10 controls, 50 repaired targeted cases, 465 cumulative passes retaining all prior 415 IDs, and two critical mutants. Coverage is 245/260 branches across 32 changed executable files, zero exclusions. Cumulative/RRCA ledgers contain 75/153 rows with CSV/SQLite parity and intact 72/147-row historical prefixes. Source pins, archives and ledger integrity match.

Review consumed producer-executed raw evidence; reviewers did not execute the target suite or independently authenticate its runtime producer. Evidence: `evidence/receipt_path_case.json`, `evidence/receipt_path_ledger_manifest.json`, and their linked raw archives. Acceptance covers new receipts under stable-cwd operations, not legacy relative-receipt migration, cross-host portability or arbitrary concurrent filesystem mutation.

## Resume the existing plan, not a new architecture

1. Read this order, `AGENTS.md`, `Runbook.md`, `docs/build_plan.md`, active requirements/V&V/work-package/binding contracts, and the governing-source inventory in `evidence/supervision_reconciliation.json`. Reconcile actual revisions and precedence. Do not reconstruct missing criteria from memory or treat reference implementations as mutation/runtime surfaces.
2. Record this scoped acceptance in the next traceability update without rewriting original failures or historical dispositions. No full requirement or work package becomes complete merely because these regressions pass.
3. Continue the already-planned WP-01 Host/IIEA source-to-capability binding and admission slice under HMT-F01/HMT-F20, with WP-08 falsifiers. Select one existing local operation from the admitted scope; pin its exact implementation/schema, principal/task/policy/resource/effect bindings, owning files, budget, expected observation and definition of done before delegation. Preserve existing authority owners and native contracts. Do not activate unresolved providers or invent a replacement kernel.
4. Demonstrate the actual implementation -> admission -> observed result/effect -> receipt path. Missing, conflicting and stale bindings must cause zero dispatch; exercise direct/MCP decision parity and an admitted local positive control. Distinguish discovery/projection from executable capability, and configured adapters from qualified runtime behavior.

## Supervisor obligations and completion condition

- Personally inspect each scoped source diff, negative/positive assertions, raw results, source identities and upstream/downstream contracts before accepting worker completion. Worker status and aggregate counts are not verification.
- Retain original failure witnesses, linked RRCA, assertion identities, exact-candidate hashes, cumulative regression inclusion, fixed coverage denominators and all required mutation/causal evidence. No test suppressions, silent test replacement or weakened definition of done. Use the existing uv workflow and complexity policy.
- Commit one coherent scoped task at a time, with requirement/RRCA linkage and matching evidence. Keep fixes separate from unrelated features. Do not inflate the existing PR with unbounded work; preserve history rather than disguising its size.
- Continue unaffected authorized engineering between checkpoints. Stop affected progression for a real contradiction, missing authority or required evidence; record the precise dependency impact and reopen route. Do not restart the entire review loop merely because an old bot alias remains open, or treat a green commit as full release.
- Finish this bounded milestone with a concise handoff: exact source candidate, operation actually exercised, governing requirements, original failures and repaired controls, independently inspectable receipts, observed effects, unexecuted claims and remaining blockers. Return for out-of-band review at that meaningful milestone, not after every administrative step.

## Boundaries that remain in force

All 11 full work-package acceptance obligations remain open. Production identity/clock, credential custody, OS/network isolation, actual external endpoints/providers, hardware budgets, full voice/accessibility and complete mission acceptance remain unqualified where already recorded. Missing sealed original interface-design provenance remains a recorded governance limit; pinned binding contracts are not a claim of complete design qualification.

**No integration, merge, deployment, credential/access expansion, live provider activation or whole-build promotion is authorized by this order.** The owner retains architecture changes, separate integration-stage instructions and final closeout. Preserve scoped engineering progress without erasing production/governance/operational HOLDs.
