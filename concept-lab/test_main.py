import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_contract(self): self.assertEqual(m.demo()['output'],2)
    def test_incompatible_version(self):
        r=m.receive({'version':2,'task_id':'t','capability':'count','input':[]})
        self.assertEqual(r['error']['code'],'CONTRACT_INVALID')
        self.assertFalse(r['error']['retryable'])

if __name__ == '__main__':
    unittest.main()
