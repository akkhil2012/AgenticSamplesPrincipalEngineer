import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_fixed_skips_planner(self):
        self.assertEqual(m.route('report',lambda:1/0),['done:lookup','done:summarize'])
    def test_untrusted_plan_rejected(self):
        for p in ([],['delete'],['lookup']*4):
            with self.assertRaises(ValueError): m.execute(p)

if __name__ == '__main__':
    unittest.main()
