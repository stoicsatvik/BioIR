"""E509: frozen observation-design falsification on SBML Test Suite case 00004.

Synthetic simulator-reference dynamics only. No empirical biology, fit, or actuation.
Pinned source: sbmlteam/sbml-test-suite@d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1.
"""
from __future__ import annotations

import json
import math
import random
from research.e466_sbml_nonlinear_oracle import K1, K2, predict_case_00004

DESIGNS = {
    "transient_0p1_0p2": (0.1, 0.2),
    "later_transient_0p2_0p4": (0.2, 0.4),
    "relaxation_1_2": (1.0, 2.0),
    "equilibrium_5_10": (5.0, 10.0),
}
SCALE_PAIRS = ((0.5, 1.0), (1.0, 2.0))
SIGMAS = (0.001, 0.005)
SEED = 20261102
DRAWS = 100000


def prediction(scale: float, t: float) -> tuple[float, float]:
    if not (math.isfinite(scale) and scale > 0 and math.isfinite(t) and t >= 0):
        raise ValueError("scale must be positive and time nonnegative; both finite")
    return predict_case_00004(scale * t)


def separation(a: float, b: float, times: tuple[float, ...]) -> float:
    """Euclidean distance of two frozen model trajectories in observed S1/S2 space."""
    if not times:
        raise ValueError("at least one time required")
    return math.sqrt(sum((x-y)**2 for t in times for x,y in zip(prediction(a,t),prediction(b,t))))


def theoretical_error(distance: float, sigma: float) -> float:
    """Bayes error for equally likely, equal-covariance Gaussian binary hypotheses."""
    if not (math.isfinite(distance) and distance >= 0 and math.isfinite(sigma) and sigma > 0):
        raise ValueError("distance >= 0 and sigma > 0 must be finite")
    return 0.5 * math.erfc(distance / (2 * sigma * math.sqrt(2)))


def simulated_error(distance: float, sigma: float, draws: int = DRAWS, seed: int = SEED) -> float:
    """Independent seeded scalar sufficient-statistic null check, not physical data."""
    if draws <= 0:
        raise ValueError("draws must be positive")
    theoretical_error(distance, sigma)
    rng = random.Random(seed)
    # Signed log-likelihood difference for true hypothesis a: d²/2 + N(0, sigma*d).
    # For exact ties, break randomly rather than favoring a by arbitrary order.
    if distance == 0:
        return sum(rng.getrandbits(1) for _ in range(draws)) / draws
    return sum(distance * distance / 2 + sigma * distance * rng.gauss(0, 1) < 0 for _ in range(draws)) / draws


def log_scale_information(t: float, sigma: float = 0.001) -> float:
    """Local Fisher information for log(rate scale), observing both species.

    dS1/dlog(c) = -t*flux; dS2/dlog(c) = 2*t*flux, at c=1.
    """
    if not (math.isfinite(t) and t >= 0 and math.isfinite(sigma) and sigma > 0):
        raise ValueError("t >= 0, sigma > 0, finite")
    s1, s2 = prediction(1.0, t)
    flux = K1*s1 - K2*s2*s2
    return 5 * (t * flux / sigma) ** 2


def evaluate(draws: int = DRAWS) -> dict:
    rows=[]
    for pair in SCALE_PAIRS:
        for design, times in DESIGNS.items():
            d=separation(*pair,times)
            for sigma in SIGMAS:
                rows.append({
                    "scales": list(pair), "design": design, "times": list(times),
                    "sigma_per_component": sigma, "euclidean_distance": d,
                    "theoretical_equal_prior_error": theoretical_error(d,sigma),
                    "seeded_mc_error": simulated_error(d,sigma,draws,SEED),
                    "draws": draws,
                })
    return {
        "experiment": "E509", "source": "SBML Test Suite case 00004 @ d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1",
        "data_type": "synthetic standards simulator reference, NOT empirical biology",
        "observation_model": "independent zero-mean Gaussian noise per S1/S2 value; equal prior binary hypotheses; parameters frozen",
        "seed": SEED, "draws_per_row": draws,
        "fisher_log_rate_scale_sigma_0p001": {str(t):log_scale_information(t) for t in (0.05,0.1,0.2,0.4,1.0,2.0,5.0)},
        "rows": rows,
        "claim_boundary": "measurement-design sensitivity for one synthetic SBML ODE; no independent biology, BioIR novelty, or field validation",
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
