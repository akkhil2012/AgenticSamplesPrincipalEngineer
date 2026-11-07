import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_reviewer_evidence(self): self.assertEqual(m.demo()['accountable_reviewer'],'bob')
    def test_changed_and_expired_action(self):
        a={'amount':10}; approval=m.approve(a,'alice','bob',100)
        with self.assertRaises(PermissionError): m.execute({'amount':20},approval,50)
        with self.assertRaises(PermissionError): m.execute(a,approval,100)
        with self.assertRaises(PermissionError): m.approve(a,'alice','alice',100)

if __name__ == '__main__':
    unittest.main()
