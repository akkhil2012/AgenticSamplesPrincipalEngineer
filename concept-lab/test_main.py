import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_trace_correlation(self):
        r=m.demo(); self.assertEqual({e['trace'] for e in r['events']},{r['result']['trace']})
    def test_denial_has_no_execution_event(self):
        events=[]; m.perform('delete',{'read'},events)
        self.assertEqual([e['event'] for e in events],['proposed','policy'])

if __name__ == '__main__':
    unittest.main()
