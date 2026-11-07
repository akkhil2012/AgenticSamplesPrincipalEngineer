import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_chain_retains_subject(self): self.assertEqual(m.demo()['subject'],'alice'); self.assertEqual(len(m.demo()['actors']),2)
    def test_no_reescalation(self):
        root=m.Identity('a','t',frozenset({'read','write'})); child=m.delegate(root,'agent',{'read'})
        with self.assertRaises(PermissionError): m.delegate(child,'worker',{'write'})

if __name__ == '__main__':
    unittest.main()
