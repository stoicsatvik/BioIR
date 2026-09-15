from __future__ import annotations

from dataclasses import dataclass

from .model import Program
from .validator import validate_program


@dataclass(frozen=True)
class StepRecord:
    step: int
    state: dict[str, float]
    max_error: float


@dataclass(frozen=True)
class SimulationResult:
    converged: bool
    steps: int
    final_state: dict[str, float]
    history: list[StepRecord]


class ToyRuntime:
    """Closed-loop synthetic runtime for normalized state variables.

    The backend intentionally models only abstract scalar state transitions.
    It is useful for testing IR semantics and controller behavior, not for
    predicting real biological outcomes.
    """

    def __init__(self, response_gain: float = 0.85) -> None:
        if not 0 < response_gain <= 1:
            raise ValueError("response_gain must be in (0, 1]")
        self.response_gain = response_gain

    def run(self, program: Program) -> SimulationResult:
        validate_program(program)
        state = dict(program.state)
        history: list[StepRecord] = []
        limit = program.constraints.max_action_magnitude

        for step in range(program.constraints.max_steps + 1):
            errors = {
                objective.variable: objective.target - state[objective.variable]
                for objective in program.objectives
            }
            max_error = max(abs(v) for v in errors.values())
            history.append(StepRecord(step, dict(state), max_error))

            if all(
                abs(errors[o.variable]) <= o.tolerance
                for o in program.objectives
            ):
                return SimulationResult(True, step, state, history)

            if step == program.constraints.max_steps:
                break

            for objective in program.objectives:
                error = errors[objective.variable]
                if abs(error) <= objective.tolerance:
                    continue
                requested = max(-limit, min(limit, error))
                updated = state[objective.variable] + requested * self.response_gain
                state[objective.variable] = max(0.0, min(1.0, updated))

        return SimulationResult(False, program.constraints.max_steps, state, history)
