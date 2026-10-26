"""Host-owned callback is separate from wire and is refreshed before invocation."""
import pytest
from pydantic import ValidationError
from test_voice_support import make_voice

from hmt_rnd.voice_adapter import transcribe
from hmt_rnd.voice_models import TranscriptionRequest


def test_wire_cannot_mint_admission(tmp_path):
    request, _ = make_voice(tmp_path)
    with pytest.raises(ValidationError):
        TranscriptionRequest(**request.model_dump(), admission="ADMITTED")


def test_host_guard_is_required(tmp_path):
    request, config = make_voice(tmp_path)
    with pytest.raises(TypeError, match="guard"):
        transcribe(request, config)


def test_revocation_before_process_does_not_dispatch(tmp_path):
    request, config = make_voice(tmp_path)
    decisions = iter(["ADMITTED", "HOLD"])
    def forbidden(*args):
        raise AssertionError("process dispatched after revocation")
    with pytest.raises(PermissionError, match="VOICE_HOLD"):
        transcribe(request, config, guard=lambda request: next(decisions), runner=forbidden)


def test_invalid_host_guard_output_fails_closed(tmp_path):
    request, config = make_voice(tmp_path)
    def malformed(request):
        return True
    with pytest.raises(ValueError, match="VOICE_INVALID_HOST_DECISION"):
        transcribe(request, config, guard=malformed)


def test_guard_exception_is_not_a_fallback_signal(tmp_path):
    request, config = make_voice(tmp_path)
    def unavailable(request):
        raise RuntimeError("host authority unavailable")
    def forbidden(*args):
        raise AssertionError("process invoked with unavailable authority")
    with pytest.raises(RuntimeError, match="host authority unavailable"):
        transcribe(request, config, guard=unavailable, runner=forbidden)
