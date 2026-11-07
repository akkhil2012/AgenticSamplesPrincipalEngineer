import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_ttl(self): self.assertEqual(m.demo(),{'active':['hello'],'expired':[]})
    def test_user_and_tenant_isolation(self):
        s=m.Sessions(); s.put('a','alice','s',['private'],0,10)
        self.assertEqual(s.get('b','alice','s',1),[]); self.assertEqual(s.get('a','bob','s',1),[])
        s.delete('a','alice','s'); self.assertEqual(s.get('a','alice','s',1),[])

if __name__ == '__main__':
    unittest.main()
