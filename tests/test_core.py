import json
import tempfile
import unittest
from pathlib import Path

from bioir.cli import load_program
from bioir.compiler import compile_program
from bioir.model import OpCode, Program
from bioir.runtime import ToyRuntime
from bioir.validator import ValidationError, validate_program


class BioIRCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = {
            "version": "bioir/v0",
            "name": "test",
            "state": {"x": 0.1, "y": 0.9},
            "objectives": [
                {"variable": "x", "target": 0.7, "tolerance": 0.05},
                {"variable": "y", "target": 0.4, "tolerance": 0.05},
            ],
            "constraints": {"max_steps": 25, "max_action_magnitude": 0.2},
        }

    def test_compile_emits_directional_ops(self) -> None:
        program = Program.from_dict(self.payload)
        ops = compile_program(program)
        opcodes = [op.opcode for op in ops]
        self.assertIn(OpCode.INCREASE, opcodes)
        self.assertIn(OpCode.DECREASE, opcodes)

    def test_runtime_converges(self) -> None:
        program = Program.from_dict(self.payload)
        result = ToyRuntime().run(program)
        self.assertTrue(result.converged)
        self.assertLessEqual(abs(result.final_state["x"] - 0.7), 0.05)
        self.assertLessEqual(abs(result.final_state["y"] - 0.4), 0.05)

    def test_unknown_objective_variable_rejected(self) -> None:
        payload = dict(self.payload)
        payload["objectives"] = [{"variable": "missing", "target": 0.5}]
        with self.assertRaises(ValidationError):
            validate_program(Program.from_dict(payload))

    def test_json_loader(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "program.json"
            path.write_text(json.dumps(self.payload), encoding="utf-8")
            program = load_program(path)
            self.assertEqual(program.name, "test")


if __name__ == "__main__":
    unittest.main()
