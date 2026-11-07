import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_complete_evidence(self): self.assertTrue(m.demo()['evidence_complete'])
    def test_missing_and_modified_evidence(self):
        r=m.evidence_bundle({'identity':'alice'}); self.assertFalse(r['evidence_complete']); self.assertIn('approval',r['missing'])
        self.assertNotEqual(r['checksum'],m.evidence_bundle({'identity':'bob'})['checksum'])

if __name__ == '__main__':
    unittest.main()
