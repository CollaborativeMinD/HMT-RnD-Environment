"""Reject unusable pinned assets and corrupted or incompatible WAV input."""
import wave
from pathlib import Path

import pytest
from test_voice_support import make_voice

from hmt_rnd.voice_adapter import transcribe
from hmt_rnd.voice_models import LocalVoiceConfig


@pytest.mark.parametrize("replacement", [Path("relative-model.bin"), "missing"])
def test_unavailable_asset_stops_before_dispatch(tmp_path, replacement):
    request, config = make_voice(tmp_path)
    model = tmp_path / "missing.bin" if replacement == "missing" else replacement
    config = LocalVoiceConfig(**(config.model_dump() | {"model": model}))
    def forbidden(*args):
        raise AssertionError("unavailable asset dispatched")
    with pytest.raises(ValueError, match="VOICE_ASSET_UNAVAILABLE"):
        transcribe(request, config, guard=lambda _: "ADMITTED", runner=forbidden)


def test_oversized_asset_stops_before_dispatch(tmp_path):
    request, config = make_voice(tmp_path)
    config = LocalVoiceConfig(**(config.model_dump() | {"max_asset_bytes": 1}))
    def forbidden(*args):
        raise AssertionError("oversized asset dispatched")
    with pytest.raises(ValueError, match="VOICE_ASSET_SIZE_LIMIT"):
        transcribe(request, config, guard=lambda _: "ADMITTED", runner=forbidden)


@pytest.mark.parametrize("channels,rate", [(2, 16000), (1, 8000)])
def test_incompatible_wav_requires_explicit_conversion(tmp_path, channels, rate):
    request, config = make_voice(tmp_path)
    with wave.open(str(request.audio), "wb") as audio:
        audio.setparams((channels, 2, rate, 0, "NONE", "not compressed"))
        audio.writeframes(b"\x00\x00" * 160 * channels)
    with pytest.raises(ValueError, match="VOICE_AUDIO_FORMAT"):
        transcribe(request, config, guard=lambda _: "ADMITTED")


def test_declared_duration_is_enforced_before_inference(tmp_path):
    request, config = make_voice(tmp_path)
    config = LocalVoiceConfig(**(config.model_dump() | {"max_audio_seconds": 0.001}))
    with pytest.raises(ValueError, match="VOICE_AUDIO_DURATION"):
        transcribe(request, config, guard=lambda _: "ADMITTED")


def test_truncated_wav_is_not_silently_partial_transcription(tmp_path):
    request, config = make_voice(tmp_path)
    request.audio.write_bytes(request.audio.read_bytes()[:-1])
    with pytest.raises(ValueError, match="VOICE_AUDIO_TRUNCATED"):
        transcribe(request, config, guard=lambda _: "ADMITTED")
