# Live local Whisper smoke tracer

`WP-11-LIVE-WHISPER-SMOKE-001` executed the actual `voice_adapter.transcribe`
against a locally compiled CPU `whisper-cli`, using the official public 11-second
JFK WAV fixture. It returned a DRAFT with authority NONE. Both synthetic host
admission checks passed; no task or external effect was submitted.

Source: `ggml-org/whisper.cpp` commit
`231638a0717b7822784297e5980965ffcec05810` (MIT).
The exact source commit, license bytes, model instructions, and download script
were inspected. Code, build products, model weights and the public sample remain
outside the repository under sibling `whisper_tracer`; they were not vendored.

Model: ggml `base.en` at Hugging Face revision
`5359861c739e955e79d9a303bcbc70fb988958b1` (model metadata: MIT).
Its 147,964,211 bytes remain below the 200 MiB limit. SHA-256:
`a03779c86df3323075f5e796cb2ce5029f00ec8869eee3fdfb897afe36c6d002`.
The published upstream SHA-1 also matched. The executable hash is retained in
`evidence/whisper_live_tracer.json` alongside adapter/source pins and commands.

The expected reference was written before inference:

> And so my fellow Americans ask not what your country can do for you ask what you can do for your country.

Actual transcript:

> And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.

The predeclared lowercase word-token comparison ignores punctuation. All 22 words
matched: zero word errors. This familiar public example is a smoke test, not an
independent technical-vocabulary or generalization benchmark.

The adapter enforced two CPU threads, 30-second decode timeout, at most 30 seconds
of admitted audio, and binary/model SHA-256 pins. Observed adapter wall time was
3.896 seconds. Largest child-process peak RSS was 287,356 KiB; this excludes the
Python parent and is not a whole-system peak. No latency distribution is claimed.

## Network boundary

Model/runtime provisioning used the network before inference. `unshare -n` failed
with EPERM, so namespace isolation is unsupported in this environment. Instead,
a separately compiled native seccomp wrapper denied socket, connect, sendto and
sendmsg calls and inherited its filter over execution of the pinned CLI. Its
positive control attempted an IPv4 stream socket and observed EPERM. The ordinary
voice runner closed unrelated descriptors and launched without a shell. The exact
wrapper source/hash, probe output, and wrapped inference argv are in the evidence.

This demonstrates the selected socket-denial control for this trusted native
executable. It is not malicious-binary, alternative ABI, workstation-wide egress,
packet-capture, or general sandbox certification. CURL and CUDA were disabled in
the CPU build. No cloud transcription service was called.

No source/runtime account, microphone client, user workstation, shared build
configuration, or application code was changed. Full offline hydration/restart,
100-utterance corpus, microphone capture, noisy speech, accessibility, task-steering,
latency/resource distributions, and userhardware qualification remain open.

## Reconstruct the recorded replay

`evidence/whisper_live_replay_sources.json` preserves the exact UTF-8 sources of
the already executed `live_driver.py` and `no_network.c`, plus their original
`predeclared_plan.json` and `model_pin.json`. Script, C source, and predeclared-plan
SHA-256 values were checked against the original run record before preservation;
no source was reconstructed from memory and no new inference was run.

Reconstruct the four named files into an isolated replay working directory.
Separately provision the pinned CLI at `build/bin/whisper-cli`, base.en weights at
`models/ggml-base.en.bin`, and public fixture at `samples/jfk.wav`; their expected
hashes are in the replay artifact. Compile the retained helper with
`gcc -O2 -Wall -Wextra -o no_network no_network.c`. Set `PYTHONPATH` to a separately
provisioned matching HMT source/package and execute the retained driver through uv.
The driver resolves assets relative to its own location. Its expected reference
and exact source are historical evidence, not permission to weaken a later oracle.

These literal sources are replay evidence, not production sandbox code. Compiled
binaries, model weights, and the third-party source bundle remain excluded. A new
build may have a different binary hash; it needs its own explicit build identity
and qualification instead of overwriting the recorded asset pin.
