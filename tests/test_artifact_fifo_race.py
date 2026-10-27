"""RC-ARTIFACT-01/02: FIFO substitution cannot retain the shared host write lock."""
import json
import os
import subprocess
import sys

import pytest


@pytest.mark.parametrize("mode", ["digest"])
def test_fifo_replacement_denies_and_releases_host_fence(tmp_path, mode):
    environment = {**os.environ, "PYTHONPATH": "src:tests"}
    command = [sys.executable, "-m", "test_artifact_fifo_worker", str(tmp_path), mode]
    try:
        result = subprocess.run(command, env=environment, capture_output=True, text=True,
                                timeout=3, check=False)
    except subprocess.TimeoutExpired as error:
        pytest.fail(f"FIFO_DEADLINE_EXCEEDED: {error.stdout!r}")
    assert result.returncode == 0, (result.stdout, result.stderr)
    events = [json.loads(line) for line in result.stdout.splitlines()]
    assert events[0] == {"race": "regular-to-FIFO", "shared_host_locked": True}
    expected = "LANE_ARTIFACT_SCOPE" if mode == "digest" else "LANE_SNAPSHOT_SCOPE"
    assert events[1]["denial"] == expected
    assert events[1]["elapsed"] < 1.0
    assert events[1]["rollback"] and events[1]["revocation_proceeds"]
    assert events[1]["restart_denied"]
