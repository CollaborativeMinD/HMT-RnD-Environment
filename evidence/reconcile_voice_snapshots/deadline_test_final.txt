"""VOICE-CLOSED-PIPE-001: one error contract across pipe/exit deadlines."""
import sys
import time

import pytest

from hmt_rnd.voice_process import run_local


def test_closed_pipes_preserve_typed_deadline_failure():
    code = "import os,time; os.close(1); os.close(2); time.sleep(30)"
    started = time.monotonic()
    with pytest.raises(TimeoutError, match="VOICE_PROCESS_TIMEOUT"):
        run_local([sys.executable, "-c", code], 0.1, 1024)
    assert time.monotonic() - started < 2
