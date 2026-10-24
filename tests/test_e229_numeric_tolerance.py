"""E229: adversarial numeric-contract tests for the simulation-only v0 IR.

The current validator rejects nonfinite states/targets but previously accepted
nonfinite objective tolerances. An infinite tolerance can falsely certify
convergence at step zero even with maximal normalized error.
"""
import math
import unittest

from bioir.compiler import compile_program
from bioir.model import Program
from bioir.runtime import ToyRuntime
from bioir.validator import ValidationError, validate_program


def program_with_tolerance(tolerance: float) -> Program:
    return Program.from_dict(
        {
            "name": "e229_numeric_contract",
            "state": {"x": 0.0},
            "objectives": [
                {"variable": "x", "target": 1.0, "tolerance": tolerance}
            ],
            "constraints": {"max_steps": 8, "max_action_magnitude": 0.25},
        }
    )


class NonfiniteToleranceContractTests(unittest.TestCase):
    def test_positive_infinity_rejected_at_validation_boundary(self) -> None:
        with self.assertRaisesRegex(ValidationError, "tolerance"):
            validate_program(program_with_tolerance(math.inf))

    def test_nan_rejected_at_validation_boundary(self) -> None:
        with self.assertRaisesRegex(ValidationError, "tolerance"):
            validate_program(program_with_tolerance(math.nan))

    def test_nonfinite_tolerances_cannot_reach_compiler_or_runtime(self) -> None:
        for value in (math.inf, math.nan, -math.inf):
            with self.subTest(value=value):
                program = program_with_tolerance(value)
                with self.assertRaises(ValidationError):
                    compile_program(program)
                with self.assertRaises(ValidationError):
                    ToyRuntime().run(program)

    def test_valid_finite_tolerance_still_converges(self) -> None:
        program = program_with_tolerance(0.05)
        result = ToyRuntime().run(program)
        self.assertTrue(result.converged)
        self.assertGreater(result.steps, 0)
        self.assertLessEqual(abs(result.final_state["x"] - 1.0), 0.05)


if __name__ == "__main__":
    unittest.main()
