import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_cycle(self): self.assertEqual(m.demo()['status'],'cycle')
    def test_hop_ceiling_and_completion(self):
        self.assertEqual(m.delegate(0,lambda a:a+1,3)['status'],'hop_limit')
        self.assertEqual(m.delegate('a',lambda _:None)['status'],'completed')

if __name__ == '__main__':
    unittest.main()
