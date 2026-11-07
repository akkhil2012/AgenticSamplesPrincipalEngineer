import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_minimization_and_no_alias(self):
        ctx={'tenant':'a','aggregate':{'count':1},'secret':'x'}; out=m.share(ctx,'a')
        out['aggregate']['count']=9
        self.assertEqual(ctx['aggregate']['count'],1); self.assertNotIn('secret',out)
    def test_cross_tenant(self):
        with self.assertRaises(PermissionError): m.share({'tenant':'a'},'b')

if __name__ == '__main__':
    unittest.main()
