import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_approval_consumed(self):
        q=m.Queue(); q.propose('a',{'x':1}); q.approve('a','bob'); q.consume('a')
        with self.assertRaises(PermissionError): q.consume('a')
    def test_pending_cannot_execute(self):
        q=m.Queue(); q.propose('a',{'x':1})
        with self.assertRaises(PermissionError): q.consume('a')

if __name__ == '__main__':
    unittest.main()
