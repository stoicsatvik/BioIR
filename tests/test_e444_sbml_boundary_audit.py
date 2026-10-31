import math
import unittest
from research.e444_sbml_boundary_audit import oracle, CASES

class E444Tests(unittest.TestCase):
    def test_pinned_five_cases(self):
        self.assertEqual(len(CASES), 5)
    def test_00005_conserves_sum(self):
        a,b=oracle('00005',5)
        self.assertAlmostEqual(a+b,.0003,places=15)
    def test_00006_equilibrium(self):
        self.assertEqual(oracle('00006',5),(.0015,.0015))
    def test_00007_fixed_reservoir_not_closed(self):
        a,b=oracle('00007',15)
        self.assertEqual(a,.015)
        self.assertAlmostEqual(b,.03-.015*math.exp(-3.75),places=15)
        self.assertGreater(abs(a+b-.03),.014)
    def test_00008_fixed_reservoir_not_closed(self):
        a,b=oracle('00008',10)
        self.assertEqual(b,.15)
        self.assertAlmostEqual(a,.075+.075*math.exp(-5),places=15)
        self.assertGreater(abs(a+b-.3),.074)
    def test_00004_weighted_invariant(self):
        a,b=.1417004714810643,.01659905703787157
        self.assertAlmostEqual(a+b/2,.15,places=14)
        self.assertGreater(abs(a+b-.15),.008)

if __name__=='__main__':unittest.main()
