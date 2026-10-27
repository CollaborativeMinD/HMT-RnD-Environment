"""Independent test observers and actual SDK process configuration."""
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

from hmt_rnd import mcp_surface
from hmt_rnd.lane_queries import receipt_digest


def watch(monkeypatch, path):
    original = mcp_surface.inspect_context

    def observed(decision, arguments):
        result = original(decision, arguments)
        with path.open("a") as stream:
            stream.write(json.dumps({"result_sha256": receipt_digest(result)}) + "\n")
        return result

    monkeypatch.setattr(mcp_surface, "inspect_context", observed)


def dispatches(path):
    return [] if not path.exists() else [json.loads(x) for x in path.read_text().splitlines()]


def receipts(store):
    with store.transaction() as db:
        return db.execute("SELECT id,body,digest FROM host_inspection_receipts "
                          "ORDER BY rowid").fetchall()


def client(binding, entries, root):
    config = root / "inspection-launch.json"
    config.write_text(json.dumps({"binding": binding.model_dump(mode="json"),
                                 "capabilities": list(entries)}))
    config.chmod(0o600)
    project = Path(__file__).parent.parent
    parameters = StdioServerParameters(command=sys.executable,
        args=[str(project / "tests/inspection_worker.py"), str(config), str(root / "mcp.jsonl")],
        env={"PYTHONPATH": str(project / "src")}, cwd=project)
    return Client(parameters, read_timeout_seconds=10)
