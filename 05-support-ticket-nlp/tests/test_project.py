import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import unittest
import numpy as np
from main import generate,fit,probabilities
class Tests(unittest.TestCase):
    def test_family_isolation(self):self.assertEqual(generate().groupby('family').split.nunique().max(),1)
    def test_unknown_tokens(self):
        p=probabilities(fit(['invoice payment','password login'],['billing','account']),['unseenword']);self.assertTrue(np.isfinite(p).all());self.assertAlmostEqual(p.sum(),1)
    def test_vocab(self):self.assertNotIn('password',fit(['invoice'],['billing'])[0])
