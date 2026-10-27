# Voice reconciliation checkpoint

Three bounded defects were reproduced against `9f2d3bf` before repair. `evidence/reconcile_voice_before_valid.xml` retains all three failures. Initial harness errors remain in `reconcile_voice_before.*` and are explicitly excluded as defect proof in the case report.

| Case | Initiating condition | Correction | Requirement |
| --- | --- | --- | --- |
| RC-VOICE-01 | Scoped audio path is a FIFO with no writer | Nonblocking open and regular-file check on opened descriptor | HMT-V09, N02, N03 |
| RC-VOICE-02 | Successful parent exits; same-group child continues | Always terminate process group after drain | HMT-V09, N02 |
| RC-VOICE-03 | Child closes both pipes, then sleeps past deadline | Normalize wait timeout to VOICE_PROCESS_TIMEOUT | HMT-V09, N03 |

Thirty-one scoped voice tests pass with zero skipped/error/failing cases. Ruff and Pyrefly basic pass; structural check passes. The case JSON and eight-column RRCA CSV bind causal investigation, exact snapshots, test identities and evidence hashes. Source snapshots preserve coherent intermediate states for one case per commit. No prior failure was deleted or marked irrelevant.

The descendant test observes a delayed filesystem write, avoiding an invalid initial observer that treated a nested process PID as an established host `/proc` identity. Closed-pipe test moved unchanged to its own module to permit scoped commits; it did not supersede or weaken the assertion.

Limits: POSIX process-group cleanup is not isolation against a hostile process that detaches sessions. A deterministic regular-to-FIFO swap immediately before real descriptor open is also rejected. FIFO rejection is not a general storage I/O deadline or hostile-directory race qualification. Full voice qualification, production credentials/OS isolation, corpus, microphone/UI and integration remain unestablished. This checkpoint proposes closure of these three defect cases only; it cannot release mission or integration HOLDs.
