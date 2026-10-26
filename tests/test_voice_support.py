"""Shared synthetic assets; no actual Whisper model or executable."""
import hashlib
import wave

from hmt_rnd.voice_models import LocalVoiceConfig, TranscriptionRequest


def make_voice(tmp_path):
    binary, model, audio = (tmp_path / n for n in ("whisper-cli", "model.bin", "audio.wav"))
    binary.write_bytes(b"fixture binary")
    model.write_bytes(b"fixture model")
    with wave.open(str(audio), "wb") as target:
        target.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        target.writeframes(b"\x00\x00" * 160)
    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()
    config = LocalVoiceConfig(executable=binary, executable_sha256=sha(binary),
                             model=model, model_sha256=sha(model), audio_root=tmp_path)
    request = TranscriptionRequest(audio=audio, selected_provider="whisper.cpp")
    return request, config

