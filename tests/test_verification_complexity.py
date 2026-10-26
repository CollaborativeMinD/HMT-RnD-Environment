"""Exact boundaries, decorator counting, and mutation controls."""
import unittest

from hmt_rnd.verification_complexity import band, inspect_source


class ComplexityTests(unittest.TestCase):
    def test_function_boundaries(self) -> None:
        for value, expected in ((0, "NOMINAL"), (44, "NOMINAL"), (45, "WATCH"),
                                (49, "WATCH"), (50, "REFACTOR_REQUIRED"),
                                (59, "REFACTOR_REQUIRED"), (60, "BLOCK")):
            self.assertEqual(band(value, function=True), expected)

    def test_module_boundaries(self) -> None:
        for value, expected in ((79, "NOMINAL"), (80, "WATCH"), (100, "WATCH"),
                                (101, "REFACTOR_REQUIRED"), (120, "REFACTOR_REQUIRED"),
                                (121, "BLOCK"), (180, "BLOCK"), (181, "BLOCK")):
            self.assertEqual(band(value, function=False), expected)

    def test_decorated_function_comments_and_blanks_count(self) -> None:
        source = "@decorator\ndef f():\n    # commentary\n\n    return 1\n"
        report = inspect_source(source)
        self.assertEqual(report["functions"][0]["loc"], 5)

    def test_nested_function_is_also_measured(self) -> None:
        source = "def outer():\n    def inner():\n        return 1\n    return inner()\n"
        report = inspect_source(source)
        self.assertEqual([f["loc"] for f in report["functions"]], [4, 2])

    def test_syntax_and_negative_counts_fail(self) -> None:
        with self.assertRaises(SyntaxError):
            inspect_source("def broken(:")
        with self.assertRaisesRegex(ValueError, "NEGATIVE_LOC"):
            band(-1, function=True)


if __name__ == "__main__":
    unittest.main()
