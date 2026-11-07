import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_old_and_new_equivalent(self): self.assertEqual(m.demo()[0],m.demo()[1])
    def test_unknown_and_malformed_rejected(self):
        for msg in ({'version':3,'query':'x'},{'version':2,'input':{'text':3}}):
            with self.assertRaises(ValueError): m.normalize(msg)

if __name__ == '__main__':
    unittest.main()
