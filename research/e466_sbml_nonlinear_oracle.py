"""Independent closed-form baseline for official SBML Test Suite case 00004.

This is a synthetic standards-test ODE, not an empirical biological model.
Pinned upstream: sbmlteam/sbml-test-suite@d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1
case 00004 Level 3 Version 2: S1 -> 2 S2, 2 S2 -> S1, rates 0.35*S1 and
180*S2**2, initial (S1, S2) = (0.15, 0). Unit compartment.
"""

from __future__ import annotations

import math

K1 = 0.35
K2 = 180.0
INITIAL_S1 = 0.15
INITIAL_S2 = 0.0
MASS = INITIAL_S1 + INITIAL_S2 / 2


def predict_case_00004(time: float) -> tuple[float, float]:
    """Solve Riccati equation dS2/dt = 2*K1*MASS - K1*S2 - 2*K2*S2^2.

    The positive and negative stationary roots are r_plus and r_minus.
    For S2(0)=0, S2(t)=r_plus*(1-exp(-lambda*t)) /
        (1-(r_plus/r_minus)*exp(-lambda*t)).
    S1 is then fixed by the exact stoichiometric invariant.
    """
    if not math.isfinite(time) or time < 0:
        raise ValueError("time must be finite and nonnegative")
    discriminant = K1 * K1 + 16.0 * K1 * K2 * MASS
    lam = math.sqrt(discriminant)
    r_plus = (-K1 + lam) / (4.0 * K2)
    r_minus = (-K1 - lam) / (4.0 * K2)
    decay = math.exp(-lam * time)
    s2 = r_plus * (-math.expm1(-lam * time)) / (1.0 - (r_plus / r_minus) * decay)
    s1 = MASS - s2 / 2.0
    return s1, s2


def derivative(s1: float, s2: float) -> tuple[float, float]:
    """Conventional mass-action ODE from the pinned SBML MathML kinetic laws."""
    forward = K1 * s1
    reverse = K2 * s2 * s2
    return -forward + reverse, 2.0 * forward - 2.0 * reverse
