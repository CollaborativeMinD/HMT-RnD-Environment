# P1 causal and process-interruption witnesses

This campaign exercises repository-owned host/custody derivatives. It imports no
HMT reference implementation and changes no production authority guard.

## Authority-edge experimental family

The tested dependency is the custody reservation's call-time authority callback.
Every arm starts from the same staged intent, task/credential/grant configuration,
clock value, effect identity, and revoked local/endpoint authority. Each arm uses
disposable separate directories to avoid cross-arm state contamination.

| Arm | Injected change | Expected local state | Endpoint effects |
| --- | --- | --- | --- |
| Intact | None | STAGED | 0 |
| Delete local | Test adapter omits reserve authorization | OUTCOME_UNCERTAIN | 0 |
| Restore local | Original callback reinstated | STAGED | 0 |
| Sham | Unrelated SELECT 1; guard retained | STAGED | 0 |
| Alternate on | Local deletion; endpoint authority retained | OUTCOME_UNCERTAIN | 0 |
| Alternate off | Both test callbacks omit authorization | OUTCOME_UNCERTAIN | 1 |

The local state observation exposes the deleted dependency even when endpoint
redundancy prevents an effect. Alternate-off demonstrates the compensating path's
role; restoration and sham match the intact control. These are controlled faulty
adapters, not evidence of production guards being absent. The claim is scoped to
this authority edge and these observations, not every system causal dependency.

## Actual subprocess termination

Two cut points are exercised: after durable local reservation, and after the local
resource endpoint commits while the source still has no receipt. The child signals
the cut only after the operation returns, using an atomically replaced marker.
The parent commits revocation, kills the actual process, waits for termination,
reopens the same SQLite domains, and verifies OUTCOME_UNCERTAIN persisted.

Revoked work cannot reserve again. Explicit trusted fixture provisioning restores
current local authority without replacing custody state. The endpoint then signs
an exact reservation-bound completion/nonexecution proof. Reconciliation is called
twice to exercise repeat delivery: endpoint effects remain exactly zero or one.
No second endpoint apply is used to discover the outcome.

This demonstrates process-kill/reopen behavior under the test filesystem's SQLite
contract. It does not establish power-loss durability, host-loss recovery, fleet
exactly-once execution, remote vendor proof support, trusted wall-clock custody,
or hardware actuation fidelity. The endpoint and keys are local test fixtures.

## Reproduction and evidence

```bash
uv run python -m pytest tests/test_causal_authority_family.py tests/test_temporal_process.py -q
uv run ruff check tests/test_causal_authority_family.py tests/test_temporal_process.py tests/test_temporal_support.py
```

`evidence/p1_causal_temporal.json` retains each arm, both process witnesses, exact
commands, source/requirement hashes, scope, and remaining limits. Requirements
supported in this bounded campaign: HMT-F02/F18, N05/N07, B01/B03/B06/B12.
Other causal edges, power-loss, and vendor reconciliation remain unqualified.
