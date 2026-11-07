import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_tool_vs_goal(self): self.assertEqual(m.demo()['tool'],2); self.assertEqual(m.demo()['delegation']['state'],'completed')
    def test_duplicate_task(self):
        a=m.Agent(); goal={'capability':'report','rows':[1]}; first=a.delegate('t',goal)
        self.assertEqual(a.delegate('t',goal),first)

if __name__ == '__main__':
    unittest.main()
