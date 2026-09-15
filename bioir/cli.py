from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compiler import compile_program
from .model import Program
from .runtime import ToyRuntime
from .validator import ValidationError, validate_program


def load_program(path: str | Path) -> Program:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    program = Program.from_dict(data)
    validate_program(program)
    return program


def _compile(path: str) -> int:
    program = load_program(path)
    payload = {
        "version": program.version,
        "name": program.name,
        "operations": [op.to_dict() for op in compile_program(program)],
    }
    print(json.dumps(payload, indent=2))
    return 0


def _simulate(path: str) -> int:
    program = load_program(path)
    result = ToyRuntime().run(program)
    payload = {
        "name": program.name,
        "converged": result.converged,
        "steps": result.steps,
        "final_state": result.final_state,
        "max_error_history": [
            {"step": row.step, "max_error": round(row.max_error, 6)}
            for row in result.history
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0 if result.converged else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="bioir",
        description="Compile and simulate BioIR v0 programs.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    compile_cmd = sub.add_parser("compile", help="lower a program to BioIR operations")
    compile_cmd.add_argument("program")

    simulate_cmd = sub.add_parser("simulate", help="run the synthetic closed-loop runtime")
    simulate_cmd.add_argument("program")

    args = parser.parse_args()
    try:
        if args.command == "compile":
            return _compile(args.program)
        if args.command == "simulate":
            return _simulate(args.program)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError) as exc:
        parser.error(str(exc))
    return 1
