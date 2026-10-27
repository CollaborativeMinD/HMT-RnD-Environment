# Artifact FIFO reconciliation

Both reported read paths are independently reproduced and repaired. Owner HOLD remains pending out-of-band supervisor review; integration and whole-requirement acceptance remain unavailable.

| Case | Boundary | Baseline witness | Candidate witness |
| --- | --- | --- | --- |
| RC-ARTIFACT-01 | Digest verification (`lane_evidence.py`) | Regular file replaced by FIFO immediately before native open; subprocess exceeds 3 seconds while competing host writer is locked | Same injected FIFO rejected as `LANE_ARTIFACT_SCOPE`; transaction rolls back, revocation proceeds, restarted revoked request rejects `HOST_GRANT_DENIED` |
| RC-ARTIFACT-02 | Byte snapshot (`lane_artifacts.py`) | Independent post-stat FIFO replacement exceeds the same watchdog with the shared host transaction held | Same injected FIFO rejected as `LANE_SNAPSHOT_SCOPE`; identical rollback, revocation and restart checks |

The frozen baseline is `c922345c520db598f4b1f6afff2598c0770f0bba`. The last witnessed causal edge is the path check/open gap: the check observes a regular inode, pathname replacement occurs, and blocking open waits on the new FIFO before any byte limit or final authority check can run. No further attacker-origin or arbitrary filesystem-latency claim is inferred.

`lane_reader.py` walks directories with `O_NOFOLLOW`, opens the final component with `O_NONBLOCK | O_NOFOLLOW`, checks regular-file type with `fstat()` on that descriptor, reads at most the remaining byte limit plus one, and closes descriptors on both acceptance and denial. Digest verification uses the original 16 MiB per-file cap; preservation supplies the remaining 16 MiB aggregate budget and retains hash verification and content-addressed byte checks.

This intentionally tightens path semantics: **all symlink components now reject**, including in-scope links that the old resolve-based reader accepted. Tests preserve exact regular-file bytes, digest identity, zero/exact-limit/overflow behavior, stored snapshot bytes, rollback, and authority. Static and injected late final/parent symlink replacements fail closed. A pathname changed after descriptor opening still reads the originally opened regular inode.

The race harness hooks the original `Path.open` and repaired `os.open` seams independently. It requires an observed `regular-to-FIFO` event and an observed competing-writer lock; removing the earlier stat check cannot silently remove the injection. The watchdog runs in a disposable subprocess and kills a blocked child. Existing failure records remain unchanged.

Two coherent source snapshots are provided: `artifact_fifo_step1.json` introduces the shared reader and digest caller, with snapshot repair explicitly still on HOLD; `artifact_fifo_step2.json` routes the snapshot caller and adds both-path tests. They support separate requirement-linked repair commits without mixing unrelated feature work.

Validation: 10 focused cases and 241 full-suite cases at step 1; 27 focused cases and 255 full-suite cases at step 2. Ruff, basic Pyrefly, and structural gates pass. Raw JUnit/logs, exact observed events, source hashes, and eight-column RRCA/cumulative exports accompany the summary. These runs use POSIX/Linux local storage, controlled path replacement, and synthetic host fixtures; they do not qualify arbitrary blocking filesystems, production isolation, broader latency distributions, or complete HMT-N02/N03/N04/N05/B01/B14.

Replay from the repository root: `uv run pytest -q tests/test_artifact_fifo*.py tests/test_lane_artifacts.py`, then `uv run pytest -q`. Expected failure disposition is typed scope/bound denial with rollback, never fallback or promotion. Human release remains outside the worker.
