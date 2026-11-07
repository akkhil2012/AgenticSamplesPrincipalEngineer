import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_dependencies_and_aggregation(self):
        r=m.demo(); self.assertEqual(r['total'],10); self.assertEqual(len(r['children']),2)
    def test_parallel_results_keep_input_order(self):
        self.assertEqual([c['agent'] for c in m.demo()['children']],['sales','support'])

if __name__ == '__main__':
    unittest.main()
