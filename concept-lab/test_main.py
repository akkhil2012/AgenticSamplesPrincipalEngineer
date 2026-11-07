import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_cache_tenant_and_user(self):
        r=m.Retriever([{'id':'d','tenant':'a','readers':['alice'],'text':'x'}])
        self.assertEqual(r.search('a','alice','x',1),['d']); self.assertEqual(r.search('a','bob','x',1),[])
        self.assertEqual(r.search('b','alice','x',1),[])
    def test_revocation_changes_cache_key(self):
        docs=[{'id':'d','tenant':'a','readers':['alice'],'text':'x'}]; r=m.Retriever(docs)
        r.search('a','alice','x',1); docs[0]['readers']=[]
        self.assertEqual(r.search('a','alice','x',2),[])

if __name__ == '__main__':
    unittest.main()
