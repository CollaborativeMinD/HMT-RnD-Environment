"""Reject malformed dimension sets before any ledger creation is possible."""
import unittest

from pydantic import ValidationError

from hmt_rnd.verification_models import Dimensions, Invariant


def invariant(identity: str = "HMT-F01", acceptance: str = "Pinned") -> Invariant:
    return Invariant(requirement_id=identity, gate_id="G-ARCH",
                     mechanisms=("control",), acceptance=acceptance)


class DimensionBoundaryTests(unittest.TestCase):
    def test_duplicate_invariant_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "DUPLICATE_INVARIANT"):
            Dimensions(invariants=(invariant(), invariant()),
                       mechanisms=("control",), gates=("G-ARCH",))

    def test_duplicate_mechanism_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "DUPLICATE_MECHANISM"):
            Dimensions(invariants=(invariant(),),
                       mechanisms=("control", "control"), gates=("G-ARCH",))

    def test_duplicate_gate_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "DUPLICATE_GATE"):
            Dimensions(invariants=(invariant(),), mechanisms=("control",),
                       gates=("G-ARCH", "G-ARCH"))

    def test_missing_owning_gate_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "UNKNOWN_OWNING_GATE"):
            Dimensions(invariants=(invariant(),), mechanisms=("control",),
                       gates=("G-OTHER",))

    def test_unknown_applicable_mechanism_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "UNKNOWN_APPLICABLE_MECHANISM"):
            Dimensions(invariants=(invariant(),), mechanisms=("crash",),
                       gates=("G-ARCH",))

    def test_total_input_acceptance_byte_limit(self) -> None:
        at_limit = tuple(invariant(f"HMT-F{n}", "a" * 65536) for n in range(128))
        accepted = Dimensions(invariants=at_limit, mechanisms=("control",),
                              gates=("G-ARCH",))
        self.assertEqual(sum(len(i.acceptance.encode()) for i in accepted.invariants), 8388608)
        over_limit = at_limit + (invariant("HMT-F128", "a"),)
        with self.assertRaisesRegex(ValidationError, "DIMENSION_INPUT_LIMIT_EXCEEDED"):
            Dimensions(invariants=over_limit, mechanisms=("control",), gates=("G-ARCH",))

    def test_strict_and_closed_inputs_reject_coercion_and_extra(self) -> None:
        with self.assertRaises(ValidationError):
            Dimensions.model_validate({"invariants": (invariant(),), "mechanisms": ("control",),
                                       "gates": ("G-ARCH",), "maximum_rows": "100"})
        with self.assertRaises(ValidationError):
            Dimensions.model_validate({"invariants": (invariant(),), "mechanisms": ("control",),
                                       "gates": ("G-ARCH",), "authorize": True})


if __name__ == "__main__":
    unittest.main()
