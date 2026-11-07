import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_injected_proposal_blocked(self):
        effects=[]
        with self.assertRaises(PermissionError): m.guarded_execute({'tool':'upload_secrets','args':{}},{'lookup'},effects)
        self.assertEqual(effects,[])
    def test_allowed_tool_still_validates_arguments(self):
        with self.assertRaises(ValueError): m.guarded_execute({'tool':'lookup','args':{'url':'attacker'}},{'lookup'},[])
        self.assertEqual(m.demo()['retrieved']['trust'],'untrusted')

if __name__ == '__main__':
    unittest.main()
