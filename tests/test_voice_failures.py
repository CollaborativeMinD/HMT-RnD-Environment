"""Bound malformed audio, subprocess results, and callback failure propagation."""
import sys

import pytest
from test_voice_support import make_voice

from hmt_rnd.voice_adapter import transcribe
from hmt_rnd.voice_models import ProcessResult
from hmt_rnd.voice_process import run_local


@pytest.fixture
def voice(tmp_path):
    return make_voice(tmp_path)

@pytest.mark.parametrize("code,data,error", [
    (2, b"", "VOICE_PROCESS_FAILED"),
    (0, b"x" * 65537, "VOICE_OUTPUT_LIMIT"),
])
def test_nonzero_or_excess_output_stays_failed(voice, code, data, error):
    request, config = voice
    with pytest.raises(ValueError, match=error):
        transcribe(request, config, guard=lambda request: "ADMITTED",
                   runner=lambda *args: ProcessResult(returncode=code, stdout=data))


def test_timeout_is_not_retried(voice):
    request, config = voice
    calls = []
    def timeout(*args):
        calls.append(args)
        raise TimeoutError("fixture timeout")
    with pytest.raises(TimeoutError):
        transcribe(request, config, guard=lambda request: "ADMITTED", runner=timeout)
    assert len(calls) == 1


def test_audio_size_boundary(voice):
    request, config = voice
    request.audio.write_bytes(b"x" * (config.max_audio_bytes + 1))
    with pytest.raises(ValueError, match="VOICE_AUDIO_LIMIT"):
        transcribe(request, config, guard=lambda request: "ADMITTED")


def test_audio_symlink_escape(voice, tmp_path):
    request, config = voice
    escaped = tmp_path.parent / "outside-voice.wav"
    escaped.write_bytes(request.audio.read_bytes())
    request.audio.unlink()
    request.audio.symlink_to(escaped)
    with pytest.raises(ValueError, match="VOICE_AUDIO_ROOT_DENIED"):
        transcribe(request, config, guard=lambda request: "ADMITTED")


def test_real_subprocess_timeout():
    with pytest.raises(TimeoutError, match="VOICE_PROCESS_TIMEOUT"):
        run_local([sys.executable, "-c", "import time;time.sleep(10)"], 0.05, 128)


def test_real_subprocess_output_bound():
    with pytest.raises(ValueError, match="VOICE_OUTPUT_LIMIT"):
        run_local([sys.executable, "-c", "print('x'*10000)"], 2.0, 128)


def test_real_subprocess_stderr_is_not_transcript():
    result = run_local([sys.executable, "-c",
                        "import sys;print('draft');print('diagnostic',file=sys.stderr)"],
                       2.0, 128)
    assert result.returncode == 0 and result.stdout == b"draft\n"
