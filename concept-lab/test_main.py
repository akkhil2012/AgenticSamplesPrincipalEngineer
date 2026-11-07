import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_no_credential_in_output_or_audit(self):
        a=m.SecretAdapter(); secret=a._vault['service-token']; r=a.invoke('service-token',{'service:call'})
        self.assertNotIn(secret,str(r)+str(a.audit)); a.rotate(); self.assertNotEqual(secret,a._vault['service-token'])
    def test_denied_no_audit_call(self):
        a=m.SecretAdapter()
        with self.assertRaises(PermissionError): a.invoke('service-token',set())
        self.assertEqual(a.audit,[])

if __name__ == '__main__':
    unittest.main()
