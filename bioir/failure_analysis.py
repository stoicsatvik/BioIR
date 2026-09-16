from __future__ import annotations

from dataclasses import dataclass
import random
from statistics import mean, median

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


@dataclass(frozen=True)
class FailureMechanismSummary:
    """Aggregate diagnostics over the frozen failure population.

    These are software/simulation diagnostics, not biological measurements.
    """
    failure_count: int
    mean_waits: float
    median_waits: float
    mean_actions: float
    median_actions: float
    mean_longest_wait_streak: float
    max_longest_wait_streak: int
    wait_dominated_count: int
    action_dominated_count: int
    tied_count: int
    exhausted_budget_count: int
    failure_seeds: tuple[int, ...]


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


def summarize_fixed_1000_failures() -> FailureMechanismSummary:
    """Quantify whether frozen failures are dominated by conservative deferral.

    Classification is deliberately mechanical: wait-dominated means WAIT count is
    greater than directional-action count; action-dominated is the reverse.
    No causal claim is inferred from this descriptive partition.
    """
    trajectories = fixed_1000_failure_trajectories()
    if not trajectories:
        raise ValueError("frozen mixture contains no failures to diagnose")

    waits = tuple(item.waits for item in trajectories)
    actions = tuple(item.actions for item in trajectories)
    streaks = tuple(item.longest_wait_streak for item in trajectories)
    return FailureMechanismSummary(
        failure_count=len(trajectories),
        mean_waits=mean(waits),
        median_waits=median(waits),
        mean_actions=mean(actions),
        median_actions=median(actions),
        mean_longest_wait_streak=mean(streaks),
        max_longest_wait_streak=max(streaks),
        wait_dominated_count=sum(w > a for w, a in zip(waits, actions)),
        action_dominated_count=sum(a > w for w, a in zip(waits, actions)),
        tied_count=sum(a == w for w, a in zip(waits, actions)),
        exhausted_budget_count=sum(item.waits + item.actions == 30 for item in trajectories),
        failure_seeds=tuple(item.seed for item in trajectories),
    )
