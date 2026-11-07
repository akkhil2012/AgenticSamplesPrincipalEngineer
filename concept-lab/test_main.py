import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_specialist_result(self): self.assertEqual(m.demo()['result'],10)
    def test_new_capability_without_supervisor_edit(self):
        s=m.Supervisor(); s.register('count',len)
        self.assertEqual(s.dispatch({'capability':'count','input':[1]})['result'],1)
        with self.assertRaises(ValueError): s.dispatch({'capability':'unknown','input':[]})

if __name__ == '__main__':
    unittest.main()
