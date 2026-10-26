# Changed-code coverage correction

R-COVERAGE-001 reopens the branch-threshold assessment under HMT-N11. The prior statement that 290/308 package branches establishes the changed-code threshold is unsupported and contradicted by the measured subset. Historical evidence remains unchanged.

Independent recursive Git-tree comparison of parent `9a5eb22bb0f430449c5465a229b5c0205eabfd93` and candidate `9f2d3bf7db042cd400b57ee78c288ca32342d9f3` identifies 20 changed first-party executable Python files. The 19 lane/MCP files cover 118/136 branches (86.7647%). The twentieth file, `scripts/check_structure.py`, is entirely absent from that coverage report. Unchanged package code supplied another 172 covered branches. Neither the subset nor the incomplete denominator supports the claimed gate pass.

The denominator manifest retains both exact source inventories and Git blob identities. The correction record binds the historical coverage digest and every selected file. It is a recalculation of existing observations, not a rerun of the old candidate.

Five new tests exercise the actual structural runner on nominal, WATCH, refactor-required, and suppressed source trees, plus import without execution. The scoped campaign observes all 12 structural-runner branches and all 56 current verification-module branches. It does not cover or qualify the complete lane/MCP system.

The supervisor must run the final candidate with `--source=hmt_rnd,scripts`, retain subprocess coverage, pin the changed source set against the same parent, and report measured/total branches and missing files separately. Missing files, exclusions, or less than 90% keep the branch gate on HOLD. Even a passing branch ratio leaves HMT-N11 assertion completeness and critical mutation obligations independently open.
