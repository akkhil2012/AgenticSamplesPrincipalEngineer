import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_good_promotes(self): self.assertTrue(m.demo()['good']['promote'])
    def test_safety_regression_blocks(self):
        self.assertFalse(m.demo()['bad']['promote'])
        self.assertEqual(m.demo()['bad']['accuracy'],0.5)

if __name__ == '__main__':
    unittest.main()
