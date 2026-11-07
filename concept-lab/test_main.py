import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_discovery(self): self.assertEqual(m.demo(),['engagement'])
    def test_inactive_and_duplicate(self):
        r=m.Registry(); x=m.Manifest('x',1,'metrics',False); r.register(x)
        self.assertEqual(r.discover('metrics',1),[])
        with self.assertRaises(ValueError): r.register(x)

if __name__ == '__main__':
    unittest.main()
