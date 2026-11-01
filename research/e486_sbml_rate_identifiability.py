"""E486: structural rate-scale non-identifiability from equilibrium-only SBML observations.

Uses official SBML Test Suite case 00004 parameters frozen in E466.
Published numbers are simulator reference outputs, not empirical biology.
No parameter fitting or biological inference is performed.
"""
from __future__ import annotations
import json
import math
from research.e466_sbml_nonlinear_oracle import K1, K2, MASS, predict_case_00004

# Pinned upstream: sbmlteam/sbml-test-suite@d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1
# cases/semantic/00004/00004-results.csv; selected source-published checkpoints.
PUBLISHED = {
    0.2: (0.1429760887550795, 0.01404782248984108),
    0.4: (0.1418174101699119, 0.01636517966017622),
    1.0: (0.141700544848195, 0.01659891030361024),
    2.0: (0.1417004714814062, 0.01659905703718799),
    5.0: (0.1417004714810643, 0.01659905703787158),
    10.0: (0.1417004714810643, 0.01659905703787157),
}
SCALES = (0.25, 0.5, 1.0, 2.0, 4.0)
EARLY = (0.2, 0.4)
LATE = (5.0, 10.0)


def predict_scaled(scale: float, time: float) -> tuple[float, float]:
    """Scale both kinetic constants by c: x_c(t)=x_1(c*t), exactly.

    The rate-ratio and equilibrium are unchanged. This is a model-specific
    mathematical identity, not a fitted observation or a general SBML claim.
    """
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError('scale must be finite and positive')
    return predict_case_00004(scale * time)


def max_published_error(scale: float, times: tuple[float, ...]) -> float:
    return max(
        abs(pred - reference)
        for t in times
        for pred, reference in zip(predict_scaled(scale, t), PUBLISHED[t])
    )


def max_oracle_error(scale: float, times: tuple[float, ...]) -> float:
    return max(
        abs(pred - reference)
        for t in times
        for pred, reference in zip(predict_scaled(scale, t), predict_case_00004(t))
    )


def evaluate() -> dict:
    rows = []
    for c in SCALES:
        rows.append({
            'scale': c,
            'k_forward': c * K1,
            'k_reverse': c * K2,
            'max_early_error_vs_published': max_published_error(c, EARLY),
            'max_late_error_vs_published': max_published_error(c, LATE),
            'max_early_error_vs_oracle': max_oracle_error(c, EARLY),
            'max_late_error_vs_oracle': max_oracle_error(c, LATE),
            'late_within_1e-10': max_published_error(c, LATE) <= 1e-10,
            'early_within_1e-10': max_published_error(c, EARLY) <= 1e-10,
        })
    return {
        'experiment': 'E486',
        'source': 'SBML Test Suite case 00004 @ d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1',
        'type': 'published simulator reference, not biological measurements',
        'invariant': MASS,
        'early_times': list(EARLY),
        'late_times': list(LATE),
        'absolute_tolerance': 1e-10,
        'results': rows,
    }


if __name__ == '__main__':
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
