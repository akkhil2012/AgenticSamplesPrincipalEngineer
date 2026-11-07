import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_policy_evidence(self): self.assertEqual(m.demo()['policy_version'],3)
    def test_unavailable_and_denied_no_effect(self):
        for service in (m.pdp,m.unavailable):
            effects=[]
            with self.assertRaises(PermissionError): m.pep({'tenant':'a','scopes':[]},'delete',{'tenant':'a'},service,effects)
            self.assertEqual(effects,[])

if __name__ == '__main__':
    unittest.main()
