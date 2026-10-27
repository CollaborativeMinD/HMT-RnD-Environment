# Lane reopening reconciliation

Four review finding families were reproduced against `9f2d3bf7db042cd400b57ee78c288ca32342d9f3` before repair: nine failing observations and one passing scope control. The unchanged tests now pass. The final lane campaign has 43 passing tests, including all 29 historical lane tests and four additional negative controls; no skips. HMT-B07@1 and HMT-B10@1 remain unchanged.

| Case | Correction | Retained snapshot | Scoped regression |
| --- | --- | --- | --- |
| RC-LANE-01 / LANE-DRIFT-001 | Recognize evidence-only and missing in-scope source drift; preserve outside-root denial | `reconcile_lane_step1.json` | 34 passed |
| RC-LANE-02 / LANE-HISTORY-001 | Reject invalidated explicit change references before invalidation | `reconcile_lane_step2.json` | 36 passed |
| RC-LANE-03 / LANE-AUTHORITY-001 | Discover all causes independently of caller reason; enforce earliest owner and architect for policy drift | `reconcile_lane_step3.json` | 38 passed |
| RC-LANE-04 / LANE-SUCCESSOR-001 | Require the exact pending event and designated successor before old-ancestor permission | `reconcile_lane_step4.json` | 39 passed |
| LANE-CONTROLS-001 | Negative controls: duplicate current stage, wrong lane, wrong task grant, unreopened ancestry | `reconcile_lane_step5.json` | 43 passed |

The five snapshots retain exact file content and SHA-256 identities for sequential small commits. Source snapshots 1–4 are cumulative at their relevant paths, with explicit dependency IDs. Step 5 changes tests only. Original failed JUnit/logs and baseline source/test bodies remain in `evidence/reconcile_lane_before*`. No historical evidence file was modified.

`evidence/reconcile_lane_report.json` records each initiating observation, evidenced causal path, corrective task, original witness, candidate identity, and regression. Separate SQLite/CSV Reverse RCA and Cumulative Gate ledgers contain the required eighth worker-attestation column. Attestations assert worker provenance and are unsigned.

Validation commands, from the repository root:

```bash
uv run pytest tests/test_lane*.py tests/test_reconcile_lane*.py
uv run ruff check src/hmt_rnd/lane_*.py tests/test_reconcile_lane*.py
uv run pyrefly check src/hmt_rnd/lane_*.py
PYTHONPATH=src uv run python scripts/check_structure.py
```

Ruff, basic Pyrefly and structural checks passed. An initial structure invocation without `PYTHONPATH=src` failed to import the package; the corrected command above passed. The five changed lane modules cover 57/60 branches in this local lane-only campaign. This denominator is separate from the full PR changed-code denominator and establishes neither complete HMT-N11 nor full lifecycle qualification.

Disposition: INVESTIGATION_COMPLETE; SOLUTION_CANDIDATE_APPLIED; awaiting supervisory evidence reconciliation. No integration release, whole-system acceptance, or global HOLD clearance is asserted. Domain evaluators, production filesystem isolation, concurrent filesystem replacement, and history-growth qualification remain outside these repairs.
