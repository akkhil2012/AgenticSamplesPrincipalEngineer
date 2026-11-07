import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_exact_change_and_replay(self):
        p=m.Production(); c={'expected_version':1,'value':'new'}; a={'id':'a','expires':10,'digest':m.fingerprint(c)}
        with self.assertRaises(PermissionError): p.apply({**c,'value':'other'},a,{'prod:write'},1)
        p.apply(c,a,{'prod:write'},1)
        with self.assertRaises(PermissionError): p.apply(c,a,{'prod:write'},1)
    def test_stale_resource_or_revoked_scope(self):
        p=m.Production(); c={'expected_version':0,'value':'new'}; a={'id':'a','expires':10,'digest':m.fingerprint(c)}
        with self.assertRaises(RuntimeError): p.apply(c,a,{'prod:write'},1)
        with self.assertRaises(PermissionError): p.apply(c,a,set(),1)
        self.assertEqual(p.value,'old')

if __name__ == '__main__':
    unittest.main()
