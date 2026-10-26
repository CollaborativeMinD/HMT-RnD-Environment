"""No ignored failure or declared-but-missing test is admitted."""
import unittest

from hmt_rnd.verification_suppression import reconcile_collection, violations


class SuppressionTests(unittest.TestCase):
    def test_alias_and_decorator_rejection(self) -> None:
        sources = (
            "from unittest import skip as hidden\n@hidden('x')\ndef f(): pass",
            "import pytest as p\n@p.mark.skipif(True)\ndef f(): pass",
            "import unittest\nraise unittest.SkipTest('x')",
            "self.skipTest('x')",
            "import pytest\npytest.xfail('x')",
        )
        for source in sources:
            self.assertTrue(violations(source))

    def test_fixture_text_is_not_a_suppression(self) -> None:
        self.assertEqual(violations("fixture = 'pytest.mark.skip'"), ())

    def test_missing_invocation_and_duplicate_execution_mutants(self) -> None:
        for collected, executed in (((), ()), (("A",), ()), (("A",), ("A", "A"))):
            with self.assertRaisesRegex(ValueError, "DRIFT"):
                reconcile_collection(("A",), collected, executed, ())

    def test_suppressed_result_mutant(self) -> None:
        with self.assertRaisesRegex(ValueError, "TEST_SUPPRESSION"):
            reconcile_collection(("A",), ("A",), ("A",), ("A",))

    def test_exact_collection_is_accepted(self) -> None:
        reconcile_collection(("A", "B"), ("B", "A"), ("A", "B"), ())

    def test_empty_declared_suite_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "INVALID_DECLARED_TEST_SET"):
            reconcile_collection((), (), (), ())


if __name__ == "__main__":
    unittest.main()
