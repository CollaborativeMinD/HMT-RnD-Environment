"""Adapter fixtures prove boundaries, never speech-recognition accuracy."""
import pytest
from pydantic import ValidationError
from test_voice_support import make_voice

from hmt_rnd.voice_adapter import transcribe
from hmt_rnd.voice_models import ProcessResult, TranscriptionRequest


@pytest.fixture
def voice(tmp_path):
    return make_voice(tmp_path)

def test_draft_only_and_explicit_cli(voice):
    request, config = voice
    calls = []
    def runner(command, timeout, limit):
        calls.append((command, timeout, limit))
        return ProcessResult(returncode=0, stdout=b"Do not exceed 5 m/s.\n")
    draft = transcribe(request, config, guard=lambda request: "ADMITTED", runner=runner)
    assert draft.state == "DRAFT" and draft.authority == "NONE"
    assert draft.text == "Do not exceed 5 m/s."
    assert len(calls) == 1 and "--no-gpu" in calls[0][0]
    assert str(request.audio) not in calls[0][0]


@pytest.mark.parametrize("state", ["HOLD", "DENIED"])
def test_terminal_admission_never_calls_provider(voice, state):
    request, config = voice
    def forbidden(*args):
        raise AssertionError("provider called after terminal decision")
    with pytest.raises(PermissionError, match="VOICE_" + state):
        transcribe(request, config, guard=lambda request: state, runner=forbidden)


def test_changed_model_never_calls_runner(voice):
    request, config = voice
    config.model.write_bytes(b"changed model")
    def forbidden(*args):
        raise AssertionError("changed model executed")
    with pytest.raises(ValueError, match="VOICE_ASSET_PIN_MISMATCH"):
        transcribe(request, config, guard=lambda request: "ADMITTED", runner=forbidden)


def test_no_unselected_provider_or_unknown_field(voice):
    request, _ = voice
    with pytest.raises(ValidationError):
        TranscriptionRequest(audio=request.audio, selected_provider="nvidia")
    with pytest.raises(ValidationError):
        TranscriptionRequest(**request.model_dump(), execute=True)
