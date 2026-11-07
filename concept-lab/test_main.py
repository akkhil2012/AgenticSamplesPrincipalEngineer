import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_latest_source(self): self.assertEqual(m.demo()['sources'],['new'])
    def test_expired_and_future_abstain(self):
        docs=[{'id':'x','key':'k','version':1,'updated':0,'expires':10}]
        self.assertEqual(m.answer(docs,10)['status'],'abstain')
        docs[0]['updated']=20; docs[0]['expires']=30
        self.assertEqual(m.answer(docs,10)['status'],'abstain')

if __name__ == '__main__':
    unittest.main()
