from __future__ import annotations

from dataclasses import dataclass
import random

from .belief import BeliefValue, fuse_observation
from .belief_compiler import compile_belief_objective
from .model import Objective, OpCode
from .uncertainty_benchmark import run_closed_loop


@dataclass(frozen=True)
class FusionResult:
    seed: int
    converged: bool
    unsupported_directions: int
    waits: int
    steps: int
    final_state: float


@dataclass(frozen=True)
class MatchedFusionVerdict:
    baseline_converged: int
    fusion_converged: int
    baseline_unsupported: int
    fusion_unsupported: int
    regressed_seeds: tuple[int, ...]
    recovered_seeds: tuple[int, ...]


def run_fused_closed_loop(
    *, seed: int, initial_state: float = 0.2, target: float = 0.7,
    tolerance: float = 0.05, max_steps: int = 30,
    max_action_magnitude: float = 0.1, response_gain: float = 0.85,
    observation_noise: float = 0.08,
) -> FusionResult:
    """Test one minimal temporal-fusion intervention in the synthetic backend.

    The intervention reuses the existing deterministic fuse_observation primitive.
    It receives exactly one observation per step and no extra step/action budget.
    This is software falsification only, not a biological controller.
    """
    rng = random.Random(seed)
    state = initial_state
    objective = Objective("x", target, tolerance)
    prior: BeliefValue | None = None
    unsupported = waits = 0

    for step in range(max_steps + 1):
        if abs(target - state) <= tolerance:
            return FusionResult(seed, True, unsupported, waits, step, state)
        if step == max_steps:
            break
        observed = max(0.0, min(1.0, state + rng.uniform(-observation_noise, observation_noise)))
        belief = BeliefValue(observed, observation_noise)
        if prior is not None:
            belief = fuse_observation(prior, observed, observation_noise)
        prior = belief
        operation = compile_belief_objective(objective, belief, max_action_magnitude)[1]
        if operation.opcode == OpCode.WAIT:
            waits += 1
            continue
        if operation.opcode not in (OpCode.INCREASE, OpCode.DECREASE):
            continue
        true_direction = OpCode.INCREASE if state < target else OpCode.DECREASE
        if operation.opcode != true_direction:
            unsupported += 1
        magnitude = operation.magnitude or 0.0
        signed = magnitude if operation.opcode == OpCode.INCREASE else -magnitude
        state = max(0.0, min(1.0, state + signed * response_gain))
    return FusionResult(seed, False, unsupported, waits, max_steps, state)


def fixed_1000_fusion_verdict() -> MatchedFusionVerdict:
    """Compare fusion with the frozen controller on exactly seeds 0..999."""
    baseline = tuple(run_closed_loop(seed=s, noisy=True) for s in range(1000))
    fusion = tuple(run_fused_closed_loop(seed=s) for s in range(1000))
    return MatchedFusionVerdict(
        baseline_converged=sum(x.converged for x in baseline),
        fusion_converged=sum(x.converged for x in fusion),
        baseline_unsupported=sum(x.unsupported_directions for x in baseline),
        fusion_unsupported=sum(x.unsupported_directions for x in fusion),
        regressed_seeds=tuple(b.seed for b, f in zip(baseline, fusion) if b.converged and not f.converged),
        recovered_seeds=tuple(b.seed for b, f in zip(baseline, fusion) if not b.converged and f.converged),
    )
