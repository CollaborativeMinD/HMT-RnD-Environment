"""Direct/store and subprocess observers; no alternate runtime authorizer."""
import json
import subprocess
import sys
from pathlib import Path

from test_inspection_observer import watch
from test_launch_identity_support import marker_rows

from hmt_rnd.host_store import HostStore
from hmt_rnd.inspection_models import InspectionLaunch
from hmt_rnd.inspection_surface import InspectionSurface

PROJECT = Path(__file__).resolve().parents[1]


def direct(monkeypatch, config, root, cwd):
    store_marker, native = root / "stores", root / "native"
    original = HostStore.__init__

    def opened(self, path):
        with store_marker.open("a") as stream:
            stream.write(str(path) + "\n")
        original(self, path)

    monkeypatch.setattr(HostStore, "__init__", opened)
    watch(monkeypatch, native)
    monkeypatch.chdir(cwd)
    try:
        launch = InspectionLaunch.model_validate_json(config.read_bytes())
        entries = tuple(item.model_dump(mode="json") for item in launch.capabilities)
        surface = InspectionSurface(launch.binding, entries, lambda: 20.0)
        result = surface.invoke("inspect_context", {})
        return {"denied": False, "result": result}
    except ValueError as error:
        return {"denied": True, "error": str(error), "phase": "validation"}
    except PermissionError as error:
        return {"denied": True, "error": str(error), "phase": "authority"}


def startup(config, root, cwd, default=False):
    arguments = (["-m", "hmt_rnd.mcp_stdio", str(config)] if default else
        [str(PROJECT / "tests/launch_identity_worker.py"), str(root / "stores"),
         str(config), str(root / "native")])
    result = subprocess.run([sys.executable, *arguments], cwd=cwd,
        env={"PYTHONPATH": str(PROJECT / "src")}, input=b"", capture_output=True, timeout=10)
    return {"returncode": result.returncode, "stdout": result.stdout.decode(),
            "stderr": result.stderr.decode(), "stores": marker_rows(root / "stores"),
            "native": marker_rows(root / "native")}


def export(root, name, value):
    directory = PROJECT / "evidence/launch_store_repair"
    (directory / f"{name}.json").write_text(json.dumps(value, indent=2) + "\n")
