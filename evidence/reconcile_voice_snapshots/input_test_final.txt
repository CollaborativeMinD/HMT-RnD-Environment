"""VOICE-FIFO-001: bounded rejection before decoder/process admission."""
import os
import subprocess
import sys

from test_voice_support import make_voice


def test_fifo_audio_rejected_without_writer(tmp_path):
    _, config = make_voice(tmp_path)
    fifo = tmp_path / "blocked.wav"
    os.mkfifo(fifo)
    config_path = tmp_path / "config.json"
    config_path.write_text(config.model_dump_json())
    code = """import sys
from pathlib import Path
from hmt_rnd.voice_assets import read_audio
from hmt_rnd.voice_models import LocalVoiceConfig
config = LocalVoiceConfig.model_validate_json(Path(sys.argv[1]).read_text())
try:
    read_audio(Path(sys.argv[2]), config)
except ValueError as error:
    print(str(error))
"""
    result = subprocess.run([sys.executable, "-c", code, str(config_path), str(fifo)],
                            capture_output=True, timeout=2, check=True,
                            env={**os.environ, "PYTHONPATH": "src"})
    assert result.stdout.strip() == b"VOICE_AUDIO_NOT_REGULAR"
