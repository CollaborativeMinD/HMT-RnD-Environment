"""R-COVERAGE-001: exercise the actual structural gate on bounded source trees."""
import contextlib
import io
import runpy
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_structure.py"


def run_gate(source: str, run_name: str = "__main__") -> str:
    with tempfile.TemporaryDirectory() as directory:
        with contextlib.chdir(directory):
            Path("src").mkdir()
            Path("src/candidate.py").write_text(source)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                runpy.run_path(str(SCRIPT), run_name=run_name)
            return output.getvalue()


class StructuralGateTests(unittest.TestCase):
    def test_nominal_source_has_no_warning(self) -> None:
        result = run_gate("def bounded():\n    return 1\n")
        self.assertNotIn("STRUCTURAL_WATCH", result)
        self.assertIn("Known suppression syntax: zero findings", result)

    def test_watch_warns_without_rejecting(self) -> None:
        self.assertIn("MODULE_LOC_WATCH", run_gate("# bounded\n" * 80))

    def test_refactor_required_rejects_candidate(self) -> None:
        with self.assertRaisesRegex(SystemExit, "STRUCTURAL_LIMIT.*MODULE_LOC_REFACTOR_REQUIRED"):
            run_gate("# too large\n" * 101)

    def test_suppression_rejects_candidate(self) -> None:
        source = "import unittest\n@unittest.skip('hidden')\ndef test_case():\n    pass\n"
        with self.assertRaisesRegex(SystemExit, "TEST_SUPPRESSION:src/candidate.py"):
            run_gate(source)

    def test_import_does_not_claim_a_gate_run(self) -> None:
        self.assertEqual(run_gate("# too large\n" * 121, "uninvoked_gate"), "")


if __name__ == "__main__":
    unittest.main()
