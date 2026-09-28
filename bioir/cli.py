from __future__ import annotations

import argparse
import json
from pathlib import Path

from .completion import plan_executable_completion
from .compiler import compile_program
from .model import Program
from .render import render_model_human, render_receipt_human
from .runtime import ToyRuntime
from .sbml_backend import to_sbml_xml
from .semantic_checks import (
    SemanticValidationError,
    check_semantic_model,
    require_valid_semantic_model,
)
from .semantic_model import SemanticModel
from .validator import ValidationError, validate_program


def load_program(path: str | Path) -> Program:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    program = Program.from_dict(data)
    validate_program(program)
    return program


def load_semantic_model(path: str | Path) -> SemanticModel:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return SemanticModel.from_dict(data)


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


def _check_model(path: str) -> int:
    model = load_semantic_model(path)
    report = check_semantic_model(model)
    payload = {
        "version": model.version,
        "name": model.name,
        **report.to_dict(),
    }
    print(json.dumps(payload, indent=2))
    return 0 if report.ok else 2


def _show_model(path: str) -> int:
    model = load_semantic_model(path)
    require_valid_semantic_model(model)
    print(render_model_human(model), end="")
    return 0


def _plan_completion(path: str, target: str, output_format: str) -> int:
    model = load_semantic_model(path)
    receipt = plan_executable_completion(model, target=target)
    if output_format == "text":
        print(render_receipt_human(receipt), end="")
    else:
        print(json.dumps(receipt.to_dict(), indent=2))
    return 0


def _export_sbml(path: str, output: str | None) -> int:
    model = load_semantic_model(path)
    require_valid_semantic_model(model)
    xml = to_sbml_xml(model)
    if output:
        Path(output).write_text(xml, encoding="utf-8")
    else:
        print(xml, end="")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="bioir",
        description=(
            "Validate partial biological models, expose unresolved mathematical "
            "commitments, render them in human/AI-readable form, and lower "
            "structural representations without silent inference."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check_cmd = sub.add_parser(
        "check-model",
        help="run structural/unit checks on a bioir/semantic/v1 model",
    )
    check_cmd.add_argument("model")

    show_cmd = sub.add_parser(
        "show-model",
        help="render the canonical structured model as deterministic plain text",
    )
    show_cmd.add_argument("model")

    completion_cmd = sub.add_parser(
        "plan-completion",
        help=(
            "list unresolved mathematical commitments before an executable "
            "Antimony/SBML/backend model can be produced"
        ),
    )
    completion_cmd.add_argument("model")
    completion_cmd.add_argument(
        "--target",
        default="antimony-or-sbml-executable",
    )
    completion_cmd.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        dest="output_format",
    )

    sbml_cmd = sub.add_parser(
        "export-sbml",
        help="lower a validated semantic model to non-inventive structural SBML",
    )
    sbml_cmd.add_argument("model")
    sbml_cmd.add_argument("--out", dest="output")

    compile_cmd = sub.add_parser(
        "compile",
        help="legacy: lower a bioir/v0 controller program to semantic operations",
    )
    compile_cmd.add_argument("program")

    simulate_cmd = sub.add_parser(
        "simulate",
        help="legacy: run the synthetic closed-loop controller runtime",
    )
    simulate_cmd.add_argument("program")

    args = parser.parse_args()
    try:
        if args.command == "check-model":
            return _check_model(args.model)
        if args.command == "show-model":
            return _show_model(args.model)
        if args.command == "plan-completion":
            return _plan_completion(args.model, args.target, args.output_format)
        if args.command == "export-sbml":
            return _export_sbml(args.model, args.output)
        if args.command == "compile":
            return _compile(args.program)
        if args.command == "simulate":
            return _simulate(args.program)
    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
        ValidationError,
        SemanticValidationError,
    ) as exc:
        parser.error(str(exc))
    return 1
