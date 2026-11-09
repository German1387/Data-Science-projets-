import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import unittest
import numpy as np
from main import forecast,naive,errors
class Tests(unittest.TestCase):
    def test_recursive_baseline(self): np.testing.assert_array_equal(naive(np.arange(14),10),[7,8,9,10,11,12,13,7,8,9])
    def test_forecast(self):
        p=forecast(np.arange(400)*.1+100,28);self.assertEqual(len(p),28);self.assertTrue(np.isfinite(p).all())
    def test_error_identity(self):self.assertEqual(errors(np.array([1,2]),np.array([1,2]))['mae'],0)
