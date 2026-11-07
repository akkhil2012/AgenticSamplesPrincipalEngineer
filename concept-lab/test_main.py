import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_plan_executes(self): self.assertEqual(m.demo()['result'],'Count: 3')
    def test_forbidden_plan(self):
        with self.assertRaises(PermissionError): m.executor([{'tool':'delete'}])
        with self.assertRaises(ValueError): m.executor([])

if __name__ == '__main__':
    unittest.main()
