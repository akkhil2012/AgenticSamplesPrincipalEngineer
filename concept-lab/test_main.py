import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_cumulative_limit(self):
        r=m.Run({'refund'},5,100); r.refund(60)
        with self.assertRaises(PermissionError): r.refund(60)
        self.assertEqual(r.amount,40)
    def test_tool_scope_and_action_count(self):
        with self.assertRaises(PermissionError): m.Run(set(),1,100).refund(10)
        r=m.Run({'refund'},1,100); r.refund(10)
        with self.assertRaises(PermissionError): r.refund(10)

if __name__ == '__main__':
    unittest.main()
