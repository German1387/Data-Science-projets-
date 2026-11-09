import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import unittest
import numpy as np
from main import cuped,allocation_pvalue
class Tests(unittest.TestCase):
    def test_allocation(self):self.assertAlmostEqual(allocation_pvalue(50,100),1);self.assertLess(allocation_pvalue(0,100),1e-20)
    def test_cuped_linear(self):
        x=np.arange(100,dtype=float);adj,theta=cuped(3*x+2,x);self.assertAlmostEqual(theta,3);self.assertLess(np.var(adj),1e-20)
    def test_constant_covariate(self):
        y=np.arange(5,dtype=float);adj,_=cuped(y,np.ones(5));np.testing.assert_array_equal(y,adj)
