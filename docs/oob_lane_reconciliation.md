# Reserved successor and event authority reconciliation

Owner HOLD remains active pending outside review. These repairs do not authorize integration progression.

RC-LANE-05 reproduced cross-lineage consumption of a globally reserved successor ID. Every candidate now checks the reservation's exact event, lineage and stage before insertion. Event issuance also explicitly rejects an already-reserved successor. Duplicate issuance was already atomically rejected by SQLite; its correction provides a typed denial and does not claim a previously successful overwrite. Six focused reservation tests and 201 previous-good tests passed at the first source snapshot.

RC-LANE-06 reproduced four stale-event admissions using fresh current builder grants across policy change, epoch-only change and restart. ReopenEvent now binds issuance policy, epoch, task and revision. A current builder grant cannot replace stale event authority. Initial-stage successors are guarded independently of predecessor checks.

Recovery uses the trusted host `LaneStore.reauthorize(identity, request, event_id, clock)` interface. It requires a current grant for `lane.reauthorize`, the exact origin task/revision and owning stage, and the `human_architect` role. It appends an immutable decision binding the exact event digest, original receipt digest, lineage, stage, task/revision and current policy/epoch. The original event remains unchanged. Unknown and closed events are rejected. A later policy/epoch change requires another current explicit decision. This method is not exposed through MCP.

Legacy event bodies without the new authority bindings return `LANE_REOPEN_BINDING_MISSING` for both use and recovery. They remain held for explicit migration rather than receiving guessed authority.

Validation: 29 focused OOB tests and 224 full-suite tests passed, no skips. All 116 recorded Python/config/lock paths matched their pre-run hashes afterward. Ruff, basic Pyrefly and physical structure gates passed. Focused tests cover immutable history, wrong task/revision/stage/role/operation, revoked/stale/expired grants, closed/unknown events, legacy records, exact event identity, restart and post-approval policy changes.

The first recovery test run expected a generic host grant reason for a forged role. The host correctly emitted its more precise identity-scope denial. The original failing test record remains retained; only that expected reason was corrected, with the same denial boundary rerun successfully.

Evidence and small-commit sources:

- `evidence/oob_lane_before_sources.json`, `oob_lane_before_tests.json`, `oob_lane_before.xml`: baseline source/tests and six failures plus one passing control.
- `evidence/oob_lane_step1.json`, `oob_lane_step2.json`: exact sequential candidate snapshots.
- `evidence/oob_lane_case05.json`, `oob_lane_case06.json`: requirement-linked initiating observations, causal paths, corrective tasks, hashes, results and unsigned worker attestations.
- `evidence/oob_lane_runtime_inventory.json`, `oob_lane_full_regression.xml`: exact full-run inventory and cumulative observations.

Reproduce focused checks from the repository root:

```bash
uv run pytest tests/test_oob_lane*.py
uv run ruff check src/hmt_rnd/lane*.py tests/test_oob_lane*.py
uv run pyrefly check src/hmt_rnd/lane*.py
PYTHONPATH=src uv run python scripts/check_structure.py
```

Disposition: INVESTIGATION_COMPLETE; SOLUTION_CANDIDATE_APPLIED; pending supervisory reconciliation and the owner's outside review. No global HOLD clearance, domain qualification, production identity assurance or full HMT-N11 acceptance is claimed.
