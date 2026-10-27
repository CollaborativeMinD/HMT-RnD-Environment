"""VOICE-DESCENDANT-001 process-group lifetime witness."""
import sys
import time

from hmt_rnd.voice_process import run_local


def test_successful_parent_does_not_leave_running_descendant(tmp_path):
    marker = tmp_path / "survived"
    code = """import os, sys, time
from pathlib import Path
pid = os.fork()
if pid == 0:
    os.close(1)
    os.close(2)
    time.sleep(0.3)
    Path(sys.argv[1]).write_text('VOICE_DESCENDANT_SURVIVED_SUCCESS')
    os._exit(0)
print(pid, flush=True)
"""
    result = run_local([sys.executable, "-c", code, str(marker)], 2.0, 1024)
    time.sleep(0.6)
    assert not marker.exists(), "VOICE_DESCENDANT_SURVIVED_SUCCESS"
    assert result.returncode == 0
