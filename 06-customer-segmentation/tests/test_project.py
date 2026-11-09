import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import unittest
import numpy as np
from main import adjusted_rand,kmeans,silhouette
class Tests(unittest.TestCase):
    def test_ari_label_invariance(self):self.assertAlmostEqual(adjusted_rand(np.array([0,0,1,1]),np.array([7,7,3,3])),1)
    def test_known_clusters(self):
        x=np.array([[0.,0.],[.1,0.],[10.,10.],[10.1,10.]]);centers,labels,inertia=kmeans(x,2);self.assertEqual(labels[0],labels[1]);self.assertNotEqual(labels[0],labels[2]);self.assertGreater(silhouette(x,labels),.9)
    def test_finite_duplicate_centers(self):self.assertTrue(np.isfinite(kmeans(np.ones((10,2)),2)[0]).all())
