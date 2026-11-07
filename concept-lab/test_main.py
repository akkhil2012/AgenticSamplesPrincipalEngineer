import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_shared_version(self): self.assertEqual(m.demo()[0],2)
    def test_lost_update_and_tenant(self):
        mem=m.SharedMemory(); mem.write('a','k',0,1)
        with self.assertRaises(RuntimeError): mem.write('a','k',0,2)
        self.assertEqual(mem.read('b','k'),(0,None)); self.assertEqual(mem.read('a','k'),(1,1))

if __name__ == '__main__':
    unittest.main()
