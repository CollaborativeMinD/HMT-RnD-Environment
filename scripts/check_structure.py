"""Fail on required refactor/block bands or known test suppression syntax."""
from pathlib import Path

from hmt_rnd.verification_complexity import inspect_source
from hmt_rnd.verification_suppression import violations


def main() -> None:
    for root in (Path("src"), Path("tests")):
        for path in sorted(root.rglob("*.py")):
            source = path.read_text()
            report = inspect_source(source)
            reasons = [report["module_reason"]] + [f["reason"] for f in report["functions"]]
            if any(str(x).endswith(("REFACTOR_REQUIRED", "LIMIT_EXCEEDED")) for x in reasons):
                raise SystemExit(f"STRUCTURAL_LIMIT:{path}:{reasons}")
            if any(str(x).endswith("WATCH") for x in reasons):
                print(f"STRUCTURAL_WATCH:{path}:{reasons}")
            if violations(source):
                raise SystemExit(f"TEST_SUPPRESSION:{path}")
    print("Known suppression syntax: zero findings")


if __name__ == "__main__":
    main()
