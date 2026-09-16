from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from .uncertainty_benchmark import BenchmarkResult, matched_suite


@dataclass(frozen=True)
class SuiteMetrics:
    seeds: int
    exact_convergence_rate: float
    noisy_convergence_rate: float
    exact_unsupported_directions: int
    noisy_unsupported_directions: int
    mean_exact_steps: float
    mean_noisy_steps: float
    mean_noisy_waits: float
    noisy_oscillations: int
    failing_noisy_seeds: tuple[int, ...]


def summarize_matched_suite(seeds: tuple[int, ...]) -> SuiteMetrics:
    """Summarize a deterministic matched synthetic benchmark without hiding failures."""
    if not seeds:
        raise ValueError("at least one seed is required")
    pairs = matched_suite(seeds)
    exact = [pair[0] for pair in pairs]
    noisy = [pair[1] for pair in pairs]
    return SuiteMetrics(
        seeds=len(seeds),
        exact_convergence_rate=mean(result.converged for result in exact),
        noisy_convergence_rate=mean(result.converged for result in noisy),
        exact_unsupported_directions=sum(result.unsupported_directions for result in exact),
        noisy_unsupported_directions=sum(result.unsupported_directions for result in noisy),
        mean_exact_steps=mean(result.steps for result in exact),
        mean_noisy_steps=mean(result.steps for result in noisy),
        mean_noisy_waits=mean(result.waits for result in noisy),
        noisy_oscillations=sum(result.oscillations for result in noisy),
        failing_noisy_seeds=tuple(result.seed for result in noisy if not result.converged),
    )


def fixed_1000_seed_verdict() -> SuiteMetrics:
    """Return the preregistered software-only robustness mixture for seeds 0..999."""
    return summarize_matched_suite(tuple(range(1000)))
