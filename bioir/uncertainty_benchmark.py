from __future__ import annotations

from dataclasses import dataclass
import random

from .belief import BeliefValue
from .belief_compiler import compile_belief_objective
from .model import Objective, OpCode


@dataclass(frozen=True)
class BenchmarkResult:
    seed: int
    noisy: bool
    unsupported_directions: int
    waits: int
    oscillations: int
    converged: bool
    steps: int
    final_state: float


def run_closed_loop(
    *,
    seed: int,
    noisy: bool,
    initial_state: float = 0.2,
    target: float = 0.7,
    tolerance: float = 0.05,
    max_steps: int = 30,
    max_action_magnitude: float = 0.1,
    response_gain: float = 0.85,
    observation_noise: float = 0.08,
) -> BenchmarkResult:
    """Run one deterministic synthetic scalar-control episode.

    This benchmark exists only to falsify software/controller claims. It does
    not model biological sensing, dynamics, interventions, or clinical use.
    Exact and noisy conditions receive the same action and step budgets.
    """
    rng = random.Random(seed)
    state = initial_state
    objective = Objective("x", target, tolerance)
    unsupported = waits = oscillations = 0
    previous_direction: OpCode | None = None

    for step in range(max_steps + 1):
        if abs(target - state) <= tolerance:
            return BenchmarkResult(
                seed, noisy, unsupported, waits, oscillations, True, step, state
            )
        if step == max_steps:
            break

        if noisy:
            observed = max(0.0, min(1.0, state + rng.uniform(-observation_noise, observation_noise)))
            belief = BeliefValue(observed, observation_noise)
        else:
            belief = BeliefValue(state, 0.0)

        operations = compile_belief_objective(
            objective, belief, max_action_magnitude
        )
        decision = operations[1].opcode

        if decision == OpCode.WAIT:
            waits += 1
            continue

        if decision not in (OpCode.INCREASE, OpCode.DECREASE):
            continue

        true_direction = OpCode.INCREASE if state < target else OpCode.DECREASE
        if decision != true_direction:
            unsupported += 1

        if previous_direction is not None and decision != previous_direction:
            oscillations += 1
        previous_direction = decision

        magnitude = operations[1].magnitude or 0.0
        signed = magnitude if decision == OpCode.INCREASE else -magnitude
        state = max(0.0, min(1.0, state + signed * response_gain))

    return BenchmarkResult(
        seed, noisy, unsupported, waits, oscillations, False, max_steps, state
    )


def matched_suite(seeds: tuple[int, ...]) -> list[tuple[BenchmarkResult, BenchmarkResult]]:
    """Return exact/noisy pairs under identical deterministic seeds and budgets."""
    return [
        (
            run_closed_loop(seed=seed, noisy=False),
            run_closed_loop(seed=seed, noisy=True),
        )
        for seed in seeds
    ]
