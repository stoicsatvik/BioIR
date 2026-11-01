"""Independent computational checks of the E486 rate-scale identifiability null."""
import math
import unittest

from research.e466_sbml_nonlinear_oracle import K1, K2, MASS, predict_case_00004
from research.e486_sbml_rate_identifiability import (
    EARLY, LATE, PUBLISHED, SCALES, evaluate, max_oracle_error,
    max_published_error, predict_scaled,
)


def rk4_scaled(scale, t, h=0.0001):
    """Independent ODE integration; does not use the closed-form predictor."""
    steps = round(t / h)
    assert abs(steps * h - t) < 1e-12
    s1, s2 = 0.15, 0.0
    def f(a, b):
        flux = scale * (K1 * a - K2 * b * b)
        return -flux, 2 * flux
    for _ in range(steps):
        a1,b1 = f(s1,s2)
        a2,b2 = f(s1+h*a1/2,s2+h*b1/2)
        a3,b3 = f(s1+h*a2/2,s2+h*b2/2)
        a4,b4 = f(s1+h*a3,s2+h*b3)
        s1 += h*(a1+2*a2+2*a3+a4)/6
        s2 += h*(b1+2*b2+2*b3+b4)/6
    return s1,s2


class IdentifiabilityTests(unittest.TestCase):
    def test_frozen_source_matches_published(self):
        self.assertLess(max_published_error(1.0, tuple(PUBLISHED)), 3e-11)

    def test_scaled_kinetics_match_independent_rk4(self):
        for c in (0.5, 2.0, 4.0):
            for t in (0.2, 0.4):
                exact = predict_scaled(c,t)
                numeric = rk4_scaled(c,t)
                self.assertLess(max(abs(a-b) for a,b in zip(exact,numeric)), 2e-11)

    def test_late_only_cannot_identify_rate_scale(self):
        for c in (0.5, 1.0, 2.0, 4.0):
            self.assertLessEqual(max_published_error(c,LATE), 1e-10)
        self.assertGreater(max_published_error(0.25,LATE), 1e-10)

    def test_early_observations_discriminate_alternatives(self):
        for c in (0.25,0.5,2.0,4.0):
            self.assertGreater(max_oracle_error(c,EARLY), 0.002)
            self.assertGreater(max_published_error(c,EARLY), 0.002)

    def test_mass_invariant_cannot_discriminate_rate_scales(self):
        for c in SCALES:
            for t in (0.0,0.2,0.4,5.0,10.0):
                s1,s2=predict_scaled(c,t)
                self.assertLess(abs(s1+s2/2-MASS),1e-14)

    def test_bad_scales_rejected(self):
        for c in (0,-1,float('nan'),float('inf'),float('-inf')):
            with self.assertRaises(ValueError):
                predict_scaled(c,1.0)

    def test_receipt_deterministic_and_no_false_empirical_claim(self):
        receipt=evaluate()
        self.assertEqual(receipt,evaluate())
        self.assertEqual(len(receipt['results']),5)
        self.assertIn('not biological measurements',receipt['type'])
        self.assertEqual(sum(x['late_within_1e-10'] for x in receipt['results']),4)
        self.assertEqual(sum(x['early_within_1e-10'] for x in receipt['results']),1)


if __name__=='__main__':
    unittest.main()
