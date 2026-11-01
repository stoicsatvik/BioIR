"""Offline tests; published values are simulator references, not observations."""
import math
import unittest

from research.e466_sbml_nonlinear_oracle import derivative, predict_case_00004

# Source: official pinned SBML Test Suite case 00004 results.csv (not fitted).
PUBLISHED = (
    (0.0, 0.15, 0.0),
    (0.2, 0.1429760887550795, 0.01404782248984108),
    (0.4, 0.1418174101699119, 0.01636517966017622),
    (1.0, 0.141700544848195, 0.01659891030361024),
    (2.0, 0.1417004714814062, 0.01659905703718799),
    (5.0, 0.1417004714810643, 0.01659905703787158),
    (10.0, 0.1417004714810643, 0.01659905703787157),
)


def rk4_step(s1, s2, h):
    k1 = derivative(s1, s2)
    k2 = derivative(s1 + h*k1[0]/2, s2 + h*k1[1]/2)
    k3 = derivative(s1 + h*k2[0]/2, s2 + h*k2[1]/2)
    k4 = derivative(s1 + h*k3[0], s2 + h*k3[1])
    return (s1 + h*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6,
            s2 + h*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6)


class NonlinearSBMLTests(unittest.TestCase):
    def test_initial_state(self):
        self.assertEqual(predict_case_00004(0), (0.15, 0.0))

    def test_published_checkpoints(self):
        for t, s1, s2 in PUBLISHED:
            with self.subTest(t=t):
                p1, p2 = predict_case_00004(t)
                self.assertLess(abs(p1-s1), 3e-11)
                self.assertLess(abs(p2-s2), 3e-11)

    def test_independent_rk4_baseline(self):
        s1, s2 = 0.15, 0.0
        h = 0.0001
        for i in range(10000):
            s1, s2 = rk4_step(s1, s2, h)
            if i+1 in (2000, 4000, 10000):
                p1, p2 = predict_case_00004((i+1)*h)
                self.assertLess(abs(p1-s1), 3e-12)
                self.assertLess(abs(p2-s2), 3e-12)

    def test_stoichiometric_invariant_and_nonnegative(self):
        for t in (0, .001, .1, .2, .4, 1, 2, 5, 10, 100):
            s1, s2 = predict_case_00004(t)
            self.assertAlmostEqual(s1 + s2/2, 0.15, places=14)
            self.assertGreaterEqual(s1, 0)
            self.assertGreaterEqual(s2, 0)

    def test_nonfinite_and_negative_time_rejected(self):
        for t in (float('nan'), float('inf'), float('-inf'), -0.1):
            with self.assertRaises(ValueError):
                predict_case_00004(t)

    def test_nonzero_drift_in_naive_total(self):
        s1, s2 = predict_case_00004(10)
        self.assertGreater(abs(s1+s2-.15), .008)
        self.assertLess(abs(s1+s2/2-.15), 1e-14)


if __name__ == '__main__':
    unittest.main()
