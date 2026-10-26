# Local voice binding — WP-11 tracer

Wispr Flow is the preferred online dictation surface. The selected local fallback
is OpenAI Whisper through whisper.cpp. NVIDIA Parakeet is recorded solely as a
future exploration candidate and has no routing entry or runtime invocation.

`voice_adapter.transcribe` accepts a strict request and host-supplied asset pins.
It calls the trusted host guard before asset access and again immediately before
process invocation, verifies executable/model byte
identities, reads bounded mono 16 kHz 16-bit PCM WAV from the admitted audio root,
and snapshots the bytes into a temporary private directory. The CPU CLI receives
fixed arguments with no shell. A POSIX process group has bounded total output and
deadline; timeout/output overflow kills and reaps it. The output is UTF-8 text in
a `DRAFT` carrying audio/model/executable digests and authority `NONE`.

Admission is not a request field. Extra-field validation rejects a forged wire
`admission=ADMITTED`. The required keyword-only guard callback is supplied by the
canonical authenticated host, not deserialized from a request. It returns the
current admission decision; invalid decisions and guard exceptions stop the call.
The host must serialize revocation against dispatch under its own authority
contract: a callback check alone is not a transaction or operating-system sandbox.
There is no task mutation, voice-to-command parser, provider retry, download,
cloud credential, or automatic alternate routing here.
An unavailable local engine returns failure for the composer to display.

The `--no-timestamps`, `--no-prints`, `--no-gpu`, `--model`, `--file`, `--language`,
and `--threads` spellings were inspected in the upstream CLI implementation:
https://github.com/ggml-org/whisper.cpp/blob/master/examples/cli/cli.cpp
This mutable reference is not a release pin. The deployed build and model must be
pinned by the host; library/backend dependencies also require qualification.

The adapter's code has no network operation. This does not prove the supplied
binary or shared libraries cannot use a network. Qualification requires an
OS-enforced egress denial and captured no-egress experiment. Host-owned executable,
model, parent directories, and dynamically loaded backends must be immutable during
hash-check/use; this adapter does not close asset-path replacement races itself.
Per-process memory/CPU/filesystem restrictions remain host responsibilities.

Same-utterance fallback needs a separately authorized HMT capture buffer. Audio
captured only by the Wispr client is not assumed accessible: a visible switch to
local mode may require dictating again. No Wispr embedding API is invented.

## Verification and remaining claims

Twenty-seven adapter/runner/host-guard tests pass, including terminal HOLD/DENIED, changed model,
unknown fields/provider, output/nonzero/timeout failure, bounded audio, symlink
escape, and real disposable subprocess timeout/output/stderr behavior. Synthetic
asset and transcript fixtures prove adapter behavior only. No real Whisper model,
microphone session, speech accuracy, no-egress capture, or latency corpus ran.

Run from the repository root with the configured uv environment:

```bash
uv run python -m pytest tests/test_voice*.py -q
```

HMT-V01/V02/V04/V05/V08 receive only partial adapter evidence. The command composer,
authenticated host binding, accessible controls, real model corpus, provider outage
sequence, and HMT-V03/V06/V07 task steering/custody proofs remain required.

## Derivative ownership

This implementation owns the HMT voice contracts, asset checks, process controls,
and draft behavior in this repository. It does not import or call a live HMT
reference bundle or reference service. Those HMT packages are read-only design
references for derivative behavior. The user-selected Whisper model and
whisper.cpp executable are explicitly bound operational software assets, not HMT
reference runtimes. They must be provisioned and qualified as normal third-party
engine dependencies; no model or executable is installed by this module.

The initial thirteen-test result remains in `evidence/voice_tracer.json`.
The admission-field correction and five additional guard cases are recorded in
`evidence/voice_guard.json`; previous passing cases were rerun without suppression.

## Input-boundary follow-up

Nine additional negative cases exercise unavailable/relative and oversized assets,
incompatible WAV channel/rate metadata, excessive duration, truncated frame data,
an unqualified process platform, and cleanup after a child has already exited.
All four voice modules have 100% measured branch coverage in this bounded campaign.
That measurement does not establish actual speech accuracy, model invocation,
platform portability, egress isolation, or production authority integration.
`evidence/voice_coverage.json` contains the raw report; its all-package total is not
an integration coverage claim because this campaign executes voice tests only.
Previous thirteen-test and eighteen-test evidence remains historically preserved.
