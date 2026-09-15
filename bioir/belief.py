from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class BeliefValue:
    """Bounded scalar belief used only by computational/simulation backends."""

    mean: float
    uncertainty: float

    def __post_init__(self) -> None:
        if not isfinite(self.mean) or not 0.0 <= self.mean <= 1.0:
            raise ValueError("mean must be finite and in [0, 1]")
        if not isfinite(self.uncertainty) or not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("uncertainty must be finite and in [0, 1]")

    def interval(self) -> tuple[float, float]:
        return (
            max(0.0, self.mean - self.uncertainty),
            min(1.0, self.mean + self.uncertainty),
        )

    def definitely_below(self, target: float, tolerance: float) -> bool:
        _, upper = self.interval()
        return upper < target - tolerance

    def definitely_above(self, target: float, tolerance: float) -> bool:
        lower, _ = self.interval()
        return lower > target + tolerance

    def target_guaranteed(self, target: float, tolerance: float) -> bool:
        lower, upper = self.interval()
        return lower >= target - tolerance and upper <= target + tolerance


def fuse_observation(
    prior: BeliefValue,
    observation: float,
    observation_uncertainty: float,
) -> BeliefValue:
    """Deterministically fuse normalized synthetic observations.

    The weighting rule is deliberately simple and documented. It exists to
    test uncertainty propagation and replay, not to model biological sensing.
    """
    observed = BeliefValue(observation, observation_uncertainty)
    prior_weight = 1.0 / max(prior.uncertainty, 1e-9)
    observation_weight = 1.0 / max(observed.uncertainty, 1e-9)
    total = prior_weight + observation_weight
    mean = (prior.mean * prior_weight + observed.mean * observation_weight) / total
    uncertainty = min(prior.uncertainty, observed.uncertainty)
    return BeliefValue(mean=mean, uncertainty=uncertainty)
