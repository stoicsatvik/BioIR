"""E509 deterministic controls; synthetic simulator case, not empirical biology."""
import math
import unittest
from research.e509_sbml_measurement_design import (
    DESIGNS, evaluate, log_scale_information, prediction, separation,
    simulated_error, theoretical_error,
)

class MeasurementDesignTests(unittest.TestCase):
    def test_frozen_kinetics_and_mass(self):
        for t in (0.0,0.1,0.2,1.0,5.0):
            for c in (0.5,1.0,2.0):
                s1,s2=prediction(c,t)
                self.assertAlmostEqual(s1+s2/2,0.15,places=13)

    def test_transient_separation_beats_late(self):
        for a,b in ((0.5,1.0),(1.0,2.0)):
            early=separation(a,b,DESIGNS['transient_0p1_0p2'])
            late=separation(a,b,DESIGNS['equilibrium_5_10'])
            self.assertGreater(early,0.006-1e-8)
            self.assertLess(late,2e-14)

    def test_gaussian_decision_formula_and_chance_null(self):
        self.assertEqual(theoretical_error(0,0.001),0.5)
        self.assertLess(theoretical_error(0.007,0.001),0.001)
        self.assertAlmostEqual(theoretical_error(1e-15,0.001),0.5,places=10)

    def test_independent_seeded_monte_carlo_matches_theory(self):
        for d in (0.0,0.001,0.003,0.007):
            measured=simulated_error(d,0.001,20000,509)
            self.assertLess(abs(measured-theoretical_error(d,0.001)),0.012)
            self.assertEqual(measured,simulated_error(d,0.001,20000,509))

    def test_information_collapse_after_relaxation(self):
        self.assertGreater(log_scale_information(0.1),1e7*log_scale_information(1.0))
        self.assertLess(log_scale_information(5.0),1e-15)

    def test_invalid_inputs_rejected(self):
        for c,t in ((0,1),(-1,1),(1,-1),(float('nan'),1)):
            with self.assertRaises(ValueError):prediction(c,t)
        with self.assertRaises(ValueError):separation(1,2,())
        for d,s in ((-1,1),(1,0),(float('inf'),1)):
            with self.assertRaises(ValueError):theoretical_error(d,s)
        with self.assertRaises(ValueError):simulated_error(1,1,0)

    def test_receipt_reproducible_and_claim_bounded(self):
        a=evaluate(draws=100)
        self.assertEqual(a,evaluate(draws=100))
        self.assertEqual(len(a['rows']),16)
        self.assertIn('NOT empirical biology',a['data_type'])
        self.assertIn('no independent biology',a['claim_boundary'])

if __name__ == '__main__':unittest.main()
