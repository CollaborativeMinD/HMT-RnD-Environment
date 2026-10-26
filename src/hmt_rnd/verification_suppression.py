"""Known syntax detector; collection/result reconciliation remains mandatory."""
import ast

FORBIDDEN = {"skip", "skipif", "xfail", "expectedFailure", "SkipTest", "skipTest"}


def violations(source: str) -> tuple[str, ...]:
    tree = ast.parse(source)
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for name in node.names:
                aliases[name.asname or name.name] = name.name
    findings: set[str] = set()
    for node in ast.walk(tree):
        name = node.attr if isinstance(node, ast.Attribute) else None
        if isinstance(node, ast.Name):
            name = aliases.get(node.id, node.id)
        if name in FORBIDDEN:
            findings.add(f"TEST_SUPPRESSION:{node.lineno}:{name}")
    return tuple(sorted(findings))


def reconcile_collection(
    declared: tuple[str, ...], collected: tuple[str, ...],
    executed: tuple[str, ...], suppressed: tuple[str, ...],
) -> None:
    if not declared or len(set(declared)) != len(declared):
        raise ValueError("INVALID_DECLARED_TEST_SET")
    if suppressed:
        raise ValueError("TEST_SUPPRESSION")
    for actual in (collected, executed):
        if len(actual) != len(declared) or set(actual) != set(declared):
            raise ValueError("TEST_COLLECTION_OR_EXECUTION_DRIFT")
