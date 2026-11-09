import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import unittest
import numpy as np
from main import generate,cost
from common import logistic,sigmoid,classification
class Tests(unittest.TestCase):
    def test_reproducible_data(self): self.assertTrue(generate(30).equals(generate(30)))
    def test_learning(self):
        x=np.c_[np.ones(100),np.linspace(-2,2,100)];y=(x[:,1]>0).astype(int)
        self.assertGreater(classification(y,sigmoid(x@logistic(x,y)))['roc_auc'],.99)
    def test_contact_cost(self): self.assertEqual(cost(np.array([1,0]),np.array([.9,.1]),.5),4.)
