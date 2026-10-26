"""Host-supplied pins and draft-only local transcription contracts."""
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class VoiceModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


class LocalVoiceConfig(VoiceModel):
    executable: Path
    executable_sha256: Digest
    model: Path
    model_sha256: Digest
    audio_root: Path
    timeout_seconds: Annotated[float, Field(gt=0, le=120)] = 30.0
    max_output_bytes: Annotated[int, Field(ge=1, le=1048576)] = 65536
    max_audio_bytes: Annotated[int, Field(ge=1, le=16777216)] = 2097152
    max_audio_seconds: Annotated[float, Field(gt=0, le=60)] = 60.0
    max_asset_bytes: Annotated[int, Field(ge=1, le=4294967296)] = 4294967296
    threads: Annotated[int, Field(ge=1, le=4)] = 1


class TranscriptionRequest(VoiceModel):
    audio: Path
    selected_provider: Literal["whisper.cpp"]


class ProcessResult(VoiceModel):
    returncode: int
    stdout: bytes


class TranscriptDraft(VoiceModel):
    state: Literal["DRAFT"] = "DRAFT"
    provider: Literal["whisper.cpp"] = "whisper.cpp"
    text: Annotated[str, Field(min_length=1, max_length=65536)]
    audio_sha256: Digest
    model_sha256: Digest
    executable_sha256: Digest
    authority: Literal["NONE"] = "NONE"
