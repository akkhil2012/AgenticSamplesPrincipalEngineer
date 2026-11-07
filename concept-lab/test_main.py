import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_reservation(self): self.assertEqual(m.demo()['remaining_cents'],2)
    def test_timeout_and_budget(self):
        with self.assertRaises(TimeoutError): m.asyncio.run(m.bounded(m.slow,m.Budget(1,5),1,0.001))
        with self.assertRaises(RuntimeError): m.asyncio.run(m.bounded(m.ready,m.Budget(0,5),1,0.1))

if __name__ == '__main__':
    unittest.main()
