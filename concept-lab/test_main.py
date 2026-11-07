import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_relationship(self): self.assertEqual(m.traverse('alice',2),['project-x']); self.assertEqual(m.traverse('bob',2),[])
    def test_similarity_and_dimension(self):
        self.assertEqual(m.semantic([.9,.1])[0],'project-x')
        with self.assertRaises(ValueError): m.cosine([1],[1,2])

if __name__ == '__main__':
    unittest.main()
