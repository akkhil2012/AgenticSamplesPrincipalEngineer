import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_live_revocation(self): self.assertEqual(m.demo()['after'], 'revoked')
    def test_versions_are_immutable(self):
        cp=m.ControlPlane(); cp.publish(1,['read'])
        with self.assertRaises(ValueError): cp.publish(1,['delete'])
        with self.assertRaises(PermissionError): cp.execute(1,'delete')

if __name__ == '__main__':
    unittest.main()
