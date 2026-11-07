import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_both_levels(self): self.assertEqual(m.demo(),'allowed')
    def test_each_level_independent(self):
        with self.assertRaisesRegex(PermissionError,'Level 1'): m.authorize({'delegates':set(),'grants':{('read','r')}},'analyst','read','r')
        with self.assertRaisesRegex(PermissionError,'Level 2'): m.authorize({'delegates':{'analyst'},'grants':set()},'analyst','read','r')

if __name__ == '__main__':
    unittest.main()
