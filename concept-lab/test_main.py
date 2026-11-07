import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_different_lifetimes(self):
        r=m.demo()['after_ttl']; self.assertEqual(r['session'],[]); self.assertEqual(r['preferences']['language'],'English')
    def test_consent_and_user_scope(self):
        mem=m.Memory()
        with self.assertRaises(PermissionError): mem.remember('a','language','English')
        mem.remember('a','language','English',True); self.assertEqual(mem.context('b',0)['preferences'],{})

if __name__ == '__main__':
    unittest.main()
