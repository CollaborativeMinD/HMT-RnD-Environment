"""Host-launched stdio entrypoint; configuration never comes from MCP messages."""
import asyncio
import os
import stat
import sys
from pathlib import Path

from .mcp_contracts import LaneBinding
from .mcp_server import LaneMCP
from .mcp_surface import LaneSurface


def read_launch(path: Path) -> bytes:
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
    with os.fdopen(os.open(path, flags), "rb") as source:
        info = os.fstat(source.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)):
            raise PermissionError("MCP_UNTRUSTED_LAUNCH_BINDING")
        content = source.read(65537)
    if len(content) > 65536:
        raise ValueError("MCP_BINDING_BOUND")
    return content


def load_binding(path: Path) -> LaneBinding:
    return LaneBinding.model_validate_json(read_launch(path))


def main() -> None:
    if len(sys.argv) != 2:
        raise PermissionError("MCP_HOST_BINDING_REQUIRED")
    binding = load_binding(Path(sys.argv[1]))
    asyncio.run(LaneMCP(LaneSurface(binding)).run_stdio_async())


if __name__ == "__main__":
    main()
