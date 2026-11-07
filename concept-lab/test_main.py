import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_tenant_prefilter(self): self.assertEqual(m.demo(),['a1'])
    def test_acl_not_just_tenant(self):
        self.assertEqual(m.retrieve(m.DOCS,{'tenant':'a','user':'bob'},'refund'),[])
        self.assertEqual(m.retrieve(m.DOCS,{'tenant':'b','user':'bob'},'refund'),['b1'])

if __name__ == '__main__':
    unittest.main()
