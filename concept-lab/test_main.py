import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_metrics(self):
        r=m.demo(); self.assertEqual(r['success_rate'],.5); self.assertEqual(r['cost_per_success'],3)
        self.assertEqual(r['p95_ms'],300)
    def test_no_successes(self):
        self.assertIsNone(m.metrics([{'success':False,'latency_ms':1,'cents':1,'delegations':1}])['cost_per_success'])
        with self.assertRaises(ValueError): m.metrics([])

if __name__ == '__main__':
    unittest.main()
