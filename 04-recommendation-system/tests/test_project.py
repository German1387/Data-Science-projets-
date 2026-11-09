import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import unittest
from main import generate,split
class Tests(unittest.TestCase):
    def test_split_isolation(self):
        df=generate();a,b,c=split(df);self.assertFalse(set(a.index)&set(b.index));self.assertFalse(set(a.index)&set(c.index));self.assertFalse(set(b.index)&set(c.index));self.assertEqual(len(a)+len(b)+len(c),len(df))
    def test_warm_start(self):
        a,b,c=split(generate());self.assertTrue(set(c.user_id)<=set(a.user_id));self.assertTrue(set(c.item_id)<=set(a.item_id))
    def test_rating_bounds(self):self.assertTrue(generate().rating.between(1,5).all())
