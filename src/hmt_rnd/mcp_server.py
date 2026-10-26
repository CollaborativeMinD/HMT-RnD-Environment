"""Official SDK server with fresh discovery projection and invocation admission."""
import json
import sys
from typing import Any

import anyio
from mcp.server import MCPServer
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent

from .mcp_contracts import EmptyArguments, HandoffArguments
from .mcp_framing import BoundedInput
from .mcp_surface import LaneSurface


class LaneMCP(MCPServer):
    def __init__(self, surface: LaneSurface):
        super().__init__("HMT lane: " + surface.binding.identity.lane)
        self.surface = surface
        self.add_tool(self.inspect_context)
        self.add_tool(self.validate_handoff)

    async def list_tools(self):
        permitted = self.surface.visible()
        tools = []
        for tool in await super().list_tools():
            if tool.name in permitted:
                model = EmptyArguments if tool.name == "inspect_context" else HandoffArguments
                tools.append(tool.model_copy(update={"input_schema": model.model_json_schema()}))
        return tools

    async def call_tool(self, name: str, arguments: dict[str, Any], context=None):
        result = self.surface.invoke(name, arguments)
        return CallToolResult(content=[TextContent(type="text", text=json.dumps(result))],
                              structuredContent=result)

    async def run_stdio_async(self) -> None:
        async with stdio_server(stdin=anyio.wrap_file(BoundedInput(sys.stdin.buffer))) as streams:
            await self._lowlevel_server.run(*streams,
                                           self._lowlevel_server.create_initialization_options())

    def inspect_context(self) -> dict[str, object]:
        """Inspect the authenticated lane/task binding without granting effects."""
        return self.surface.invoke("inspect_context", {})

    def validate_handoff(self, handoff: dict[str, object]) -> dict[str, object]:
        """Validate a bounded handoff shape; never accept, promote, or execute it."""
        return self.surface.invoke("validate_handoff", {"handoff": handoff})
