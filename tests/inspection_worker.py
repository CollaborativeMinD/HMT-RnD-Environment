"""Test-only configured stdio slice; no default production launcher activation."""
import asyncio
import json
import sys
from pathlib import Path

from hmt_rnd import mcp_surface
from hmt_rnd.inspection_models import InspectionLaunch
from hmt_rnd.inspection_surface import InspectionSurface
from hmt_rnd.lane_queries import receipt_digest
from hmt_rnd.mcp_server import LaneMCP
from hmt_rnd.mcp_stdio import read_launch


def main():
    config = InspectionLaunch.model_validate_json(read_launch(Path(sys.argv[1])))
    original = mcp_surface.inspect_context

    def observed(decision, arguments):
        result = original(decision, arguments)
        with Path(sys.argv[2]).open("a") as stream:
            stream.write(json.dumps({"result_sha256": receipt_digest(result)}) + "\n")
        return result

    mcp_surface.inspect_context = observed
    entries = tuple(item.model_dump(mode="json") for item in config.capabilities)
    surface = InspectionSurface(config.binding, entries, lambda: 20.0)
    asyncio.run(LaneMCP(surface).run_stdio_async())


if __name__ == "__main__":
    main()
