from __future__ import annotations

from .belief import BeliefValue
from .model import Objective, OpCode, Operation


def compile_belief_objective(
    objective: Objective,
    belief: BeliefValue,
    max_action_magnitude: float,
) -> list[Operation]:
    """Lower one simulated objective using conservative belief semantics.

    Direction-changing operations are emitted only when the complete belief
    interval lies beyond the objective tolerance band. Ambiguous beliefs
    produce SENSE + WAIT instead of pretending a point estimate is certain.
    This is a simulation-only compiler primitive, not a biological controller.
    """
    ops = [Operation(OpCode.SENSE, variable=objective.variable)]

    if belief.target_guaranteed(objective.target, objective.tolerance):
        ops.append(
            Operation(
                OpCode.MAINTAIN,
                variable=objective.variable,
                target=objective.target,
                tolerance=objective.tolerance,
            )
        )
        return ops

    if belief.definitely_below(objective.target, objective.tolerance):
        distance = max(0.0, objective.target - belief.interval()[1])
        ops.append(
            Operation(
                OpCode.INCREASE,
                variable=objective.variable,
                magnitude=min(distance, max_action_magnitude),
            )
        )
    elif belief.definitely_above(objective.target, objective.tolerance):
        distance = max(0.0, belief.interval()[0] - objective.target)
        ops.append(
            Operation(
                OpCode.DECREASE,
                variable=objective.variable,
                magnitude=min(distance, max_action_magnitude),
            )
        )
    else:
        ops.append(Operation(OpCode.WAIT, variable=objective.variable, steps=1))

    ops.append(
        Operation(
            OpCode.MAINTAIN,
            variable=objective.variable,
            target=objective.target,
            tolerance=objective.tolerance,
        )
    )
    return ops
