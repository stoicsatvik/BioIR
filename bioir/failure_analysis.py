from __future__ import annotations

from dataclasses import dataclass
import random

from .belief import BeliefValue
from .belief_compiler import compile_belief_objective
from .model import Objective, OpCode
from .uncertainty_benchmark import run_closed_loop


@dataclass(frozen=True)
class FailureTrajectory:
    seed: int
    waits: int
    actions: int
    longest_wait_streak: int
    final_state: float
    converged: bool


def trace_noisy_episode(
    seed: int,
    *,
    initial_state: float = 0.2,
    target: float = 0.7,
    tolerance: float = 0.05,
    max_steps: int = 30,
    max_action_magnitude: float = 0.1,
    response_gain: float = 0.85,
    observation_noise: float = 0.08,
) -> FailureTrajectory:
    """Replay one synthetic noisy episode and retain deferral structure.

    Software/simulation diagnostic only. This is not a biological model.
    """
    rng = random.Random(seed)
    state = initial_state
    objective = Objective("x", target, tolerance)
    waits = actions = wait_streak = longest_wait_streak = 0

    for step in range(max_steps + 1):
        if abs(target - state) <= tolerance:
            return FailureTrajectory(seed, waits, actions, longest_wait_streak, state, True)
        if step == max_steps:
            break

        observed = max(0.0, min(1.0, state + rng.uniform(-observation_noise, observation_noise)))
        belief = BeliefValue(observed, observation_noise)
        decision = compile_belief_objective(objective, belief, max_action_magnitude)[1]

        if decision.opcode == OpCode.WAIT:
            waits += 1
            wait_streak += 1
            longest_wait_streak = max(longest_wait_streak, wait_streak)
            continue

        wait_streak = 0
        if decision.opcode not in (OpCode.INCREASE, OpCode.DECREASE):
            continue
        actions += 1
        magnitude = decision.magnitude or 0.0
        signed = magnitude if decision.opcode == OpCode.INCREASE else -magnitude
        state = max(0.0, min(1.0, state + signed * response_gain))

    return FailureTrajectory(seed, waits, actions, longest_wait_streak, state, False)


def fixed_1000_failure_trajectories() -> tuple[FailureTrajectory, ...]:
    """Preserve every non-converging trajectory from the frozen 0..999 mixture."""
    failures = []
    for seed in range(1000):
        result = run_closed_loop(seed=seed, noisy=True)
        if not result.converged:
            failures.append(trace_noisy_episode(seed))
    return tuple(failures)
