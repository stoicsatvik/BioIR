from __future__ import annotations

from .model import OpCode, Operation, Program
from .validator import validate_program


def compile_program(program: Program) -> list[Operation]:
    """Lower high-level objectives into BioIR v0 semantic operations.

    This compiler targets a simulation-only semantic ISA. It does not map
    operations to laboratory procedures, molecules, sequences, or doses.
    """
    validate_program(program)
    ops: list[Operation] = []
    limit = program.constraints.max_action_magnitude

    for objective in program.objectives:
        current = program.state[objective.variable]
        error = objective.target - current
        ops.append(Operation(OpCode.SENSE, variable=objective.variable))

        if abs(error) > objective.tolerance:
            magnitude = min(abs(error), limit)
            opcode = OpCode.INCREASE if error > 0 else OpCode.DECREASE
            ops.append(
                Operation(
                    opcode,
                    variable=objective.variable,
                    magnitude=magnitude,
                )
            )

        ops.append(
            Operation(
                OpCode.MAINTAIN,
                variable=objective.variable,
                target=objective.target,
                tolerance=objective.tolerance,
            )
        )

    return ops
