import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_lost_reply(self): self.assertEqual(m.demo(),{'retry_result':1,'effects':1})
    def test_conflict_and_tenant_scope(self):
        t=m.Tool(); t.call('a','w','s',{'x':1})
        with self.assertRaises(ValueError): t.call('a','w','s',{'x':2})
        t.call('b','w','s',{'x':2}); self.assertEqual(t.effects,2)

if __name__ == '__main__':
    unittest.main()
