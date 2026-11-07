import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_action_has_evidence(self):
        audit=[]
        self.assertEqual(m.platform('close_ticket', {'close_ticket'}, audit)['status'], 'closed')
        self.assertEqual(len(audit), 1)
    def test_unauthorized_has_no_effect(self):
        audit=[]
        with self.assertRaises(PermissionError): m.platform('close_ticket', set(), audit)
        self.assertEqual(audit, [])

if __name__ == '__main__':
    unittest.main()
