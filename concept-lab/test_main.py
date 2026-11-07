import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_pipeline(self):
        self.assertEqual(m.demo()['trace'][-1], 'executed')
    def test_contract_and_policy(self):
        with self.assertRaises(ValueError): m.handle({'intent':'ticket_status'}, {'scopes':[]})
        with self.assertRaises(PermissionError): m.handle({'intent':'ticket_status','ticket':'7'}, {'scopes':[]})

if __name__ == '__main__':
    unittest.main()
