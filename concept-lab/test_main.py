import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_valid_request(self): self.assertEqual(m.demo(),'allowed')
    def test_each_request_rechecks(self):
        i={'verified':True,'expires':10,'audience':'tools','tenant':'a','scopes':['read']}; r={'tenant':'a','action':'read'}
        m.verify(i,r,1)
        for changes in ({'verified':False},{'audience':'other'},{'tenant':'b'},{'scopes':[]}):
            with self.assertRaises(PermissionError): m.verify({**i,**changes},r,1)
        with self.assertRaises(PermissionError): m.verify(i,r,10)

if __name__ == '__main__':
    unittest.main()
