import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_valid_proposal(self): self.assertEqual(m.demo()['refunded'],40)
    def test_overspend_and_bad_type_have_no_effect(self):
        for amount in (101,-1,True,'40'):
            state={'refunded':0}
            with self.assertRaises(PermissionError): m.apply({'action':'refund','amount':amount},state)
            self.assertEqual(state['refunded'],0)

if __name__ == '__main__':
    unittest.main()
