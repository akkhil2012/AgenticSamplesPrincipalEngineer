import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_degrade_and_recover(self): self.assertEqual([r['degraded'] for r in m.demo()],[True,True,False])
    def test_open_circuit_skips_upstream(self):
        c=m.Circuit(); c.call(m.unavailable,0)
        self.assertTrue(c.call(lambda:1/0,1)['degraded'])

if __name__ == '__main__':
    unittest.main()
