import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_revision(self): self.assertTrue(m.demo()['accepted']); self.assertEqual(m.demo()['revisions'],1)
    def test_non_improving_model_stops(self):
        r=m.reflect('bad',lambda d,c:d,2)
        self.assertFalse(r['accepted']); self.assertEqual(r['revisions'],2)

if __name__ == '__main__':
    unittest.main()
