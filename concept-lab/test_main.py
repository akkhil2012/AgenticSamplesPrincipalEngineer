import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_partial_success_retained(self): self.assertEqual(m.demo()['first']['results'],{'sales':10})
    def test_resume_skips_completed(self):
        self.assertEqual(m.demo()['recovered']['results'],{'sales':10,'support':3})
        self.assertEqual(m.demo()['recovered']['status'],'completed')

if __name__ == '__main__':
    unittest.main()
