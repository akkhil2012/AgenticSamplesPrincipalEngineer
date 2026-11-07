import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_action_budget(self):
        cap=m.Capability({'read'},1); cap.call('read',{'read'})
        with self.assertRaises(PermissionError): cap.call('read',{'read'})
    def test_scope_intersection(self):
        cap=m.Capability({'write'},2)
        with self.assertRaises(PermissionError): cap.call('write',{'read'})
        self.assertEqual(cap.remaining,2)

if __name__ == '__main__':
    unittest.main()
