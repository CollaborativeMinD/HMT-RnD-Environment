# Path identity assurance

**HOLD remains.** Read-only review supports the bounded RC-PATH-01 repair at `fa8161270454ec3697bcaa5a1e26d0a6ad62e6c9`. The original witness sealed inside bytes after the evaluator read different outside bytes. The repair rejects original parent components in either path or root before normalization or opening.

The final candidate has 15 matching focused controls and a source-bound supervisor run of 270 passing tests. All 126 executable files match the published candidate. Changed-code coverage is 241/256 branches across 31 files, with no exclusions; full N11 remains unqualified. Original failures and the preformat static failure remain retained.

The cumulative and RRCA ledgers contain 60 and 124 rows, match SQLite, preserve the prior 52/116-row prefixes and retain all nine worker rows. Findings 4383956251 (ancestor task assignment) and 4383956285 (drift path resolution) remain separate `OPEN_REVIEW_HOLD` records, unexecuted in this campaign.

The detailed findings, exact hashes, limitations and outside-release condition are in `evidence/path_identity_assurance_final.json`. No target code or tests were executed by this assurance review. Continuation, integration and deployment remain unreleased.
