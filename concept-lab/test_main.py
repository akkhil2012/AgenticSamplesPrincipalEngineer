import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_revocation(self): self.assertEqual(m.demo()['after_revocation'],'denied')
    def test_discovery_filters_scopes(self):
        c=m.Catalog(); self.assertEqual(c.discover(set()),[])
        with self.assertRaises(PermissionError): c.call('count',2,[],{'count'})

if __name__ == '__main__':
    unittest.main()
