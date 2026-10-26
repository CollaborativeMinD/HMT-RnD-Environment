"""Unqualified platforms and exit-before-cleanup races remain explicit."""
import subprocess
import sys
from types import SimpleNamespace

import pytest

from hmt_rnd import voice_process


def test_unqualified_platform_never_starts_child(monkeypatch):
    monkeypatch.setattr(voice_process, "os", SimpleNamespace(name="nt"))
    with pytest.raises(ValueError, match="VOICE_PROCESS_PLATFORM_UNQUALIFIED"):
        voice_process.run_local(["must-not-execute"], 1.0, 128)


def test_already_exited_process_cleanup_is_safe():
    with subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True) as process:
        assert process.wait(timeout=2) == 0
        voice_process.terminate(process)
        assert process.poll() == 0
