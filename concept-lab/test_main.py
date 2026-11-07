import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_rollout_and_rollback(self): self.assertEqual(m.demo(),{'canary':'1.1','rollback':'1.0'})
    def test_major_and_stability(self):
        with self.assertRaises(ValueError): m.accept('2.0')
        self.assertEqual(m.route('a',20),m.route('a',20))

if __name__ == '__main__':
    unittest.main()
