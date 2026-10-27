# Bounded reconciliation checkpoint

The eleven reviewer finding groups and one supervisor replay-precondition case are closed within their declared test boundaries. Integration remains on HOLD. No remaining integration instructions were inferred, and no domain feature or external operation was added during this campaign.

| Case | Bounded correction |
| --- | --- |
| RC-HOST-01 | Reject relative grant roots before provisioning and on persisted-grant reads. |
| RC-CUSTODY-01 | Preserve input identity across cancelled reservations and fresh reservation IDs. |
| RC-VOICE-01 | Nonblocking audio open and same-descriptor regular-file validation, including replacement race. |
| RC-VOICE-02 | Clean the process group after successful parent exit. |
| RC-VOICE-03 | Preserve the typed timeout contract after pipe closure. |
| RC-LEDGER-01 | Reject normalized invariant collisions before creating a ledger destination. |
| RC-LANE-01 | Recognize gate-evidence and missing-source drift without permitting scope escape. |
| RC-LANE-02 | Reject historical invalidated change references. |
| RC-LANE-03 | Discover all affected causes, route to earliest owner, and retain architect authority for policy drift. |
| RC-LANE-04 | Require the bound successor for a pending stage reopening. |
| RC-COVERAGE-01 | Correct the changed-code denominator and measure the structural checker. |
| RC-HARNESS-01 | Reconstruct and verify executable source identities for cumulative replay. |

## Evidence and limits

All 195 tests pass with zero failures, errors, or skips. Changed first-party executable coverage is 206/222 branches (92.79%), across 26 files against parent `9a5eb22bb0f430449c5465a229b5c0205eabfd93`, including `scripts/check_structure.py`; no exclusions are used. The broader measured package/script total is 316/332 branches. Ruff, basic Pyrefly, and structural checks pass. Basic typing is not a strict-type qualification claim.

The full suite was replayed after each coherent source/test overlay: host 164, custody 170, voice 172/173/174, identity 176, lane 181/183/185/186/190, structural oracle 195. Every executable inventory matches its expected overlay and remained unchanged during its run. The independent reviewer verified all 102 executable source/test/script files against published commit `ce754d63cc9f8541da945e6636f519a17e04aefb`.

An initial custody replay accidentally used the baseline host model and failed four host regressions. That failure is retained. The cause is bounded to an unchecked replay precondition; no writer is attributed without evidence. The corrected host-only and cumulative replays retain the same failing tests, with exact source inventories. The earlier 164-pass XML alone lacked source binding and is not used as the exact-candidate closeout witness.

Historical `p1_assurance_final.json` incorrectly applied package-wide coverage to the changed-code gate. Its claim is withdrawn by the correction records; the original is retained. The >=90% branch condition now passes, while HMT-N11 as a whole remains unqualified because full applicable-assertion and critical-mutant obligations are incomplete.

The complete 10,556-row candidate ledger remains unchanged: 189 applicable and 10,367 NOT_APPLICABLE with predicates. This repair work does not mark those 189 target-oracle obligations satisfied. Manual RRCA case records do not qualify the future `rrca.compile` executable binding.

## Review path

Start with `evidence/reconciliation_closure_register.json` for each case's requirement, worker alias, causal record, candidate commit, regression and independent review. `evidence/reconciliation_commits.json` records the small commit sequence. The cumulative and RRCA ledgers contain 40 and 90 rows respectively, eight columns each with supervised attestations. Original parent ledgers are preserved in `evidence/reconciliation_history/`.

Use `evidence/reconciliation_archive_index.json` and each sequence record's archive entry to recover exact compressed witnesses. Archive hashes establish integrity, not signer authenticity. Independent assurance consumed source and recorded execution evidence; it did not execute or repair the target.

Historical qualification holds H01–H07 remain separately visible. Production identity/egress, actual endpoint behavior, complete target-oracle and mutation campaigns, domain/mission profiles, export qualification, and voice device/UI evidence cannot be replaced by local fixture results. Complete Forge acceptance remains INSUFFICIENT_EVIDENCE. Only the human owner can supply the reserved integration instructions and final architecture/release decisions.
