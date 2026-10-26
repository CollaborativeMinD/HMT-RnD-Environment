"""Disposable host-provisioned binding and real stdio client fixtures."""
import sys
import time
from pathlib import Path

from mcp import Client, StdioServerParameters

from hmt_rnd.host_models import Assignment, Grant, Identity
from hmt_rnd.host_store import HostStore
from hmt_rnd.mcp_contracts import LaneBinding


def make_lane(tmp_path: Path):
    store = HostStore.create(tmp_path / "host.sqlite", "policy-1")
    identity = Identity(principal="worker-build", role="builder", lane="Build", stage="B3",
                        credential="host-bound-credential")
    store.assign(Assignment(task_id="task-1", principal=identity.principal, revision=1))
    for operation in ("inspect_context", "validate_handoff"):
        store.grant(Grant(**identity.model_dump(), task_id="task-1", revision=1,
                          operation=operation, root=str(tmp_path), destination="local",
                          policy="policy-1", epoch=1, not_before=time.time() - 5,
                          expires=time.time() + 90, evidence_expires=time.time() + 80))
    binding = LaneBinding(identity=identity, store=store.path, task_id="task-1", revision=1,
                          root=tmp_path, destination="local", policy="policy-1")
    return store, binding


def client_for(binding: LaneBinding, tmp_path: Path) -> Client:
    launch = tmp_path / "launch.json"
    launch.write_text(binding.model_dump_json())
    launch.chmod(0o600)
    root = Path(__file__).resolve().parents[1]
    parameters = StdioServerParameters(command=sys.executable,
                                       args=["-m", "hmt_rnd.mcp_stdio", str(launch)],
                                       env={"PYTHONPATH": str(root / "src")}, cwd=root)
    return Client(parameters, read_timeout_seconds=5)


def handoff_payload() -> dict[str, object]:
    return {"response": {"agent_role": "builder", "task_owned": "task-1",
                         "implementation": "candidate", "risks": [], "assumptions": [],
                         "follow_up_instructions": [], "validation_status": "pass",
                         "artifact_refs": [], "provenance_id": "synthetic-fixture"}}
