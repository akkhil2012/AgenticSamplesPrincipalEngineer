import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_same_key_different_tenant(self): self.assertEqual(m.demo(),{'a':'private-a','b':'private-b'})
    def test_quota_independent(self):
        s=m.TenantStore(1); s.put('a','k',1)
        with self.assertRaises(RuntimeError): s.put('a','j',2)
        s.put('b','j',3); self.assertEqual(s.get('b','j'),3); self.assertIsNone(s.get('b','k'))

if __name__ == '__main__':
    unittest.main()
