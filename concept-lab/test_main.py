import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_original_user_retained(self): self.assertEqual(m.demo()['on_behalf_of'],'alice')
    def test_privileged_deputy_cannot_escalate(self):
        user={'id':'a','tenant':'a','resources':['r'],'scopes':['read']}; agent={'scopes':['read','delete']}
        for req in ({'tenant':'b','resource':'r','action':'read'},{'tenant':'a','resource':'r','action':'delete'}):
            with self.assertRaises(PermissionError): m.deputy(user,agent,req)

if __name__ == '__main__':
    unittest.main()
