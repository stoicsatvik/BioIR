from __future__ import annotations

from .model import Program


class ValidationError(ValueError):
    pass


def validate_program(program: Program) -> None:
    if program.version != "bioir/v0":
        raise ValidationError(f"unsupported version: {program.version}")
    if not program.state:
        raise ValidationError("state must contain at least one variable")
    if not program.objectives:
        raise ValidationError("program must contain at least one objective")
    if program.constraints.max_steps < 1 or program.constraints.max_steps > 10_000:
        raise ValidationError("max_steps must be between 1 and 10000")
    if not 0 < program.constraints.max_action_magnitude <= 1.0:
        raise ValidationError("max_action_magnitude must be in (0, 1]")

    seen: set[str] = set()
    for objective in program.objectives:
        if objective.variable not in program.state:
            raise ValidationError(
                f"objective references unknown state variable: {objective.variable}"
            )
        if objective.variable in seen:
            raise ValidationError(
                f"duplicate objective for variable: {objective.variable}"
            )
        seen.add(objective.variable)
        if objective.tolerance <= 0:
            raise ValidationError("objective tolerance must be positive")
        if not 0.0 <= objective.target <= 1.0:
            raise ValidationError("v0 targets must use normalized [0, 1] values")

    for name, value in program.state.items():
        if not 0.0 <= value <= 1.0:
            raise ValidationError(
                f"v0 state variable {name!r} must be normalized to [0, 1]"
            )
