"""Actual subprocess kill/reopen; process durability only, never power-loss proof."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from test_temporal_support import observed, open_domains, renew_local

from hmt_rnd.custody_models import Reservation
from hmt_rnd.host_store import HostStore

CHILD = """
from pathlib import Path
import os,sys,time
from test_temporal_support import prepare
root=Path(sys.argv[1]); local,endpoint,intent=prepare(root)
local.stage(intent); reservation=local.reserve('alice','effect1')
if sys.argv[2]=='after_endpoint_commit': endpoint.apply(reservation)
(root/'ready.tmp').write_text(reservation.model_dump_json())
os.replace(root/'ready.tmp', root/'ready.json')
while True: time.sleep(0.1)
"""


def kill_at_cut(root: Path, cut: str) -> dict:
    repo = Path(__file__).resolve().parents[1]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join((str(repo / "src"), str(repo / "tests")))
    process = subprocess.Popen([sys.executable, "-c", CHILD, str(root), cut],
                               env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 10.0
        while not (root / "ready.json").exists():
            if process.poll() is not None or time.monotonic() >= deadline:
                raise AssertionError("CHILD_DID_NOT_REACH_DURABLE_CUT")
            time.sleep(0.01)
        reservation = json.loads((root / "ready.json").read_text())
        HostStore(root / "local.sqlite").revoke("alice")
        process.kill()
        process.communicate(timeout=10)
        assert process.returncode != 0
        return {"reservation": reservation, "returncode": process.returncode, "cut": cut}
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=10)


@pytest.mark.parametrize("cut,effects", (("after_reserve", 0), ("after_endpoint_commit", 1)))
def test_kill_reopen_fresh_authority_and_exact_reconciliation(tmp_path, cut, effects):
    result = kill_at_cut(tmp_path, cut)
    local, endpoint, _ = open_domains(tmp_path)
    assert observed(tmp_path) == ("OUTCOME_UNCERTAIN", effects)
    with pytest.raises(PermissionError, match="HOST_GRANT_DENIED"):
        local.reserve("alice", "effect1")
    renew_local(tmp_path)
    reservation = Reservation.model_validate(result["reservation"])
    proof = endpoint.lookup_or_cancel(reservation)
    expected = "COMMITTED" if effects else "NOT_EXECUTED"
    assert local.reconcile(proof) == expected
    assert local.reconcile(proof) == expected
    assert observed(tmp_path) == (expected, effects)
