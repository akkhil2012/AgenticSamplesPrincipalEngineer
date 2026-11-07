import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_untrusted_text_not_forwarded(self): self.assertEqual(set(m.demo()),{'ticket','status'})
    def test_forbidden_plan(self):
        with self.assertRaises(PermissionError): m.execute(m.Plan('delete','INC-7'))

if __name__ == '__main__':
    unittest.main()
