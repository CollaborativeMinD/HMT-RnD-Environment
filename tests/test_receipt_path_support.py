"""Issue relative/absolute path fixtures; preserve real evaluator and reader behavior."""
import json
import os
import subprocess
import sys
from pathlib import Path

from test_lane_tracer import execute_gate, make_candidate, setup_host

from hmt_rnd.host_models import Clock
from hmt_rnd.lane_store import LaneStore


def prepare(root, monkeypatch, artifact_relative, evidence_relative, outcome="SEALED"):
    scope = root / "scope"
    scope.mkdir()
    monkeypatch.chdir(root)
    host, owner, request = setup_host(scope)
    store = LaneStore(host)
    candidate = make_candidate(scope)
    if artifact_relative:
        candidate = candidate.model_copy(update={"artifact": Path("scope/first.txt")})
    seen = []

    def evaluator(context):
        seen.append(str(context.candidate.artifact))
        result = execute_gate(context)
        item = result.evidence[0]
        path = Path("scope/first.evidence") if evidence_relative else scope / "first.evidence"
        reasons = ("CONTROLLED_DENIAL",) if outcome == "DENIED" else ()
        return result.model_copy(update={"evidence": (item.model_copy(update={"path": path}),),
                                         "outcome": outcome, "reasons": reasons})

    first = store.submit(owner, request, candidate, lambda: Clock(now=10.0), evaluator)
    elsewhere = root / "elsewhere"
    elsewhere.mkdir()
    return scope, host, owner, request, store, first, candidate, seen, elsewhere


def observe(root, **values):
    (root / "receipt_path_observation.json").write_text(json.dumps(values, indent=2) + "\n")


def invoke(scope, mode, cwd, child):
    if not child:
        from receipt_path_worker import perform
        return perform(scope, mode)
    script = Path(__file__).with_name("receipt_path_worker.py").absolute()
    env = dict(os.environ, PYTHONPATH=str(script.parent.parent / "src"))
    result = subprocess.run([sys.executable, str(script), str(scope), mode], cwd=cwd,
                            env=env, text=True, capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)
