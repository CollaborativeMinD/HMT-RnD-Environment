"""Bound each stdio JSON-RPC frame before the SDK parses peer input."""
import io
from typing import BinaryIO


class BoundedInput(io.TextIOBase):
    def __init__(self, source: BinaryIO):
        self.source = source

    def readable(self) -> bool:
        return True

    def readline(self, size: int = -1) -> str:
        limit = 65536 if size < 0 else min(size, 65536)
        line = self.source.readline(limit + 1)
        if len(line) > limit:
            raise ValueError("MCP_FRAME_BOUND")
        return line.decode("utf-8", errors="strict")
