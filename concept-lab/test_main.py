import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_replay(self):
        c=m.Channel(); e=c.sign({'aud':'w','expires':10,'nonce':'n','task':'read'}); c.receive(e,'w',1)
        with self.assertRaises(PermissionError): c.receive(e,'w',1)
    def test_tamper_audience_expiry(self):
        c=m.Channel(); e=c.sign({'aud':'w','expires':10,'nonce':'n','task':'read'})
        with self.assertRaises(PermissionError): c.receive(e,'other',1)
        with self.assertRaises(PermissionError): c.receive(e,'w',10)
        e['body']+=' '
        with self.assertRaises(PermissionError): c.receive(e,'w',1)

if __name__ == '__main__':
    unittest.main()
