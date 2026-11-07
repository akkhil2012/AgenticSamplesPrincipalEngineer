import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_route(self): self.assertEqual(m.demo()['value'],2)
    def test_agent_scope_not_sufficient(self):
        g=m.Gateway()
        with self.assertRaises(PermissionError): g.call('count',[],set(),{'count'})
        self.assertFalse(g.audit[-1]['allowed'])

if __name__ == '__main__':
    unittest.main()
