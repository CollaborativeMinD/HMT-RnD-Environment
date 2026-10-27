"""RC-VOICE-01: descriptor guard after deterministic regular-to-FIFO swap."""
import os
import subprocess
import sys

from test_voice_support import make_voice


def test_audio_replaced_by_fifo_at_open_is_rejected(tmp_path):
    request, config = make_voice(tmp_path)
    config_path = tmp_path / "config.json"
    config_path.write_text(config.model_dump_json())
    code = """import os, sys
from pathlib import Path
from hmt_rnd.voice_assets import read_audio
from hmt_rnd.voice_models import LocalVoiceConfig
config = LocalVoiceConfig.model_validate_json(Path(sys.argv[1]).read_text())
audio = Path(sys.argv[2])
real_open = os.open
def swap_then_open(path, flags, *args, **kwargs):
    if Path(path) == audio:
        audio.unlink()
        os.mkfifo(audio)
    return real_open(path, flags, *args, **kwargs)
os.open = swap_then_open
try:
    read_audio(audio, config)
except ValueError as error:
    print(str(error))
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(config_path), str(request.audio)],
        capture_output=True, timeout=2, check=True,
        env={**os.environ, "PYTHONPATH": "src"})
    assert result.stdout.strip() == b"VOICE_AUDIO_NOT_REGULAR"
