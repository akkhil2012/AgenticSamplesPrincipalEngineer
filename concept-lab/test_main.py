import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_same_business_result(self): self.assertEqual(m.single(),m.multi())
    def test_specialist_cannot_cross_boundary(self):
        with self.assertRaises(PermissionError): m.invoke('sales','support')

if __name__ == '__main__':
    unittest.main()
