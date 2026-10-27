# Remaining findings assurance

**HOLD remains pending outside review.** Both requested findings have been reproduced and repaired within declared boundaries at `3a875e8eaf29bb767b63bf02b41fbf1d138200f9`.

RC-ANCESTOR-01 now checks every ancestor against its current principal/revision at submission and before reopening insertion. The additional writer/reader coupling was reproduced, retained and repaired through the existing validator. RC-DRIFT-01 keeps original paths intact and distinguishes genuine missing descendants from refused paths or unavailable roots. Neither repair adds assignment migration or rerouting authority.

Read-only inspection verified the exact 292 → 319 → 339 supervisor sequence, all 137 executable files plus configuration and lockfile against the published candidate, and changed-code coverage of 243/258 branches (94.19%, no exclusions). Full N11 remains unqualified.

The 67-row cumulative and 136-row RRCA ledgers match SQLite and preserve prior 60/124-row prefixes and all supplied worker rows. Requirement trace omissions identified during review were corrected without changing acceptance criteria or source. Original failures and historical statuses remain linked to current repaired/pending cases.

Detailed scope, observations, hashes and limitations are in `evidence/remaining_assurance_final.json`. Assurance executed no target code or tests. Outside review controls continuation; integration remains explicitly unauthorized.
