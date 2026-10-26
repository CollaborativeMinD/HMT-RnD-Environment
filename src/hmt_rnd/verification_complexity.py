"""Conservative physical-line overlay; syntax errors cannot yield a passing report."""
import ast
from pathlib import Path
from typing import Literal, TypedDict

Band = Literal["NOMINAL", "WATCH", "REFACTOR_REQUIRED", "BLOCK"]


class FunctionReport(TypedDict):
    name: str
    loc: int
    reason: str


class ModuleReport(TypedDict):
    module_loc: int
    module_reason: str
    functions: list[FunctionReport]


def band(count: int, *, function: bool) -> Band:
    if count < 0:
        raise ValueError("NEGATIVE_LOC")
    watch, refactor, block = (45, 50, 60) if function else (80, 101, 121)
    if count >= block:
        return "BLOCK"
    if count >= refactor:
        return "REFACTOR_REQUIRED"
    return "WATCH" if count >= watch else "NOMINAL"


def inspect_source(source: str) -> ModuleReport:
    tree = ast.parse(source)
    functions: list[FunctionReport] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            first = min([node.lineno] + [d.lineno for d in node.decorator_list])
            assert node.end_lineno is not None
            count = node.end_lineno - first + 1
            disposition = band(count, function=True)
            reason = "NOMINAL" if disposition == "NOMINAL" else (
                "FUNCTION_LOC_LIMIT_EXCEEDED" if disposition == "BLOCK" else
                "FUNCTION_LOC_" + disposition
            )
            functions.append({"name": node.name, "loc": count, "reason": reason})
    count = len(source.splitlines())
    disposition = band(count, function=False)
    reason = "NOMINAL" if disposition == "NOMINAL" else (
        "MODULE_LOC_LIMIT_EXCEEDED" if disposition == "BLOCK" else
        "MODULE_LOC_" + disposition
    )
    return {"module_loc": count, "module_reason": reason, "functions": functions}


def inspect_file(path: Path) -> ModuleReport:
    return inspect_source(path.read_text(encoding="utf-8"))
