"""Explicit local selection yields a draft; no provider or task fallback exists."""
import hashlib
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from .voice_assets import read_audio, verify_assets
from .voice_models import LocalVoiceConfig, ProcessResult, TranscriptDraft, TranscriptionRequest
from .voice_process import run_local

Runner = Callable[[list[str], float, int], ProcessResult]
Guard = Callable[[TranscriptionRequest], Literal["ADMITTED", "HOLD", "DENIED"]]


def require_admission(request: TranscriptionRequest, guard: Guard) -> None:
    decision = guard(request)
    if decision not in ("ADMITTED", "HOLD", "DENIED"):
        raise ValueError("VOICE_INVALID_HOST_DECISION")
    if decision != "ADMITTED":
        raise PermissionError("VOICE_" + decision)


def command_for(config: LocalVoiceConfig, audio: Path) -> list[str]:
    return [str(config.executable), "--model", str(config.model), "--file", str(audio),
            "--no-timestamps", "--no-prints", "--no-gpu", "--language", "en",
            "--threads", str(config.threads)]


def transcribe(request: TranscriptionRequest, config: LocalVoiceConfig,
               *, guard: Guard, runner: Runner = run_local) -> TranscriptDraft:
    require_admission(request, guard)
    verify_assets(config)
    audio = read_audio(request.audio, config)
    with tempfile.TemporaryDirectory(prefix="hmt-voice-") as directory:
        private_audio = Path(directory) / "input.wav"
        private_audio.write_bytes(audio)
        require_admission(request, guard)
        result = runner(command_for(config, private_audio), config.timeout_seconds,
                        config.max_output_bytes)
    if result.returncode != 0:
        raise ValueError("VOICE_PROCESS_FAILED")
    if len(result.stdout) > config.max_output_bytes:
        raise ValueError("VOICE_OUTPUT_LIMIT")
    text = result.stdout.decode("utf-8", errors="strict").strip()
    return TranscriptDraft(text=text, audio_sha256=hashlib.sha256(audio).hexdigest(),
                           model_sha256=config.model_sha256,
                           executable_sha256=config.executable_sha256)
