"""Read bounded audio and verify trusted host-owned asset pins."""
import hashlib
import io
import wave
from pathlib import Path

from .voice_models import LocalVoiceConfig


def digest_file(path: Path, limit: int) -> str:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1048576), b""):
            total += len(chunk)
            if total > limit:
                raise ValueError("VOICE_ASSET_SIZE_LIMIT")
            digest.update(chunk)
    return digest.hexdigest()


def verify_assets(config: LocalVoiceConfig) -> None:
    for path, expected in ((config.executable, config.executable_sha256),
                           (config.model, config.model_sha256)):
        if not path.is_absolute() or not path.is_file():
            raise ValueError("VOICE_ASSET_UNAVAILABLE")
        if digest_file(path, config.max_asset_bytes) != expected:
            raise ValueError("VOICE_ASSET_PIN_MISMATCH")


def read_audio(path: Path, config: LocalVoiceConfig) -> bytes:
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(config.audio_root.resolve(strict=True)):
        raise ValueError("VOICE_AUDIO_ROOT_DENIED")
    with resolved.open("rb") as source:
        data = source.read(config.max_audio_bytes + 1)
    if len(data) > config.max_audio_bytes:
        raise ValueError("VOICE_AUDIO_LIMIT")
    with wave.open(io.BytesIO(data), "rb") as audio:
        shape = (audio.getnchannels(), audio.getsampwidth(), audio.getframerate())
        if shape != (1, 2, 16000) or audio.getcomptype() != "NONE":
            raise ValueError("VOICE_AUDIO_FORMAT")
        if audio.getnframes() / 16000 > config.max_audio_seconds:
            raise ValueError("VOICE_AUDIO_DURATION")
        if len(audio.readframes(audio.getnframes())) != audio.getnframes() * 2:
            raise ValueError("VOICE_AUDIO_TRUNCATED")
    return data
