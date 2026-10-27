"""Observe attempted store construction before running real configured MCP."""
import runpy
import sys
from pathlib import Path

from hmt_rnd.host_store import HostStore

original = HostStore.__init__
marker = Path(sys.argv.pop(1))


def observed(self, path):
    with marker.open("a") as stream:
        stream.write(str(path) + "\n")
    original(self, path)


HostStore.__init__ = observed
runpy.run_path(str(Path(__file__).with_name("inspection_worker.py")), run_name="__main__")
