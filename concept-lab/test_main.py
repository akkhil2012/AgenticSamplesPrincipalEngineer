import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_discover_and_call(self): self.assertEqual(m.demo()['call']['content'][0]['text'],'5')
    def test_strict_schema(self):
        with self.assertRaises(ValueError): m.dispatch('tools/call',{'name':'add','arguments':{'a':True,'b':2}})
        with self.assertRaises(ValueError): m.dispatch('tools/call',{'name':'shell','arguments':{}})

if __name__ == '__main__':
    unittest.main()
