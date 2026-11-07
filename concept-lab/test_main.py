import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_mutation(self): self.assertEqual(m.demo(),{'before':True,'after_tamper':False})
    def test_truncation_and_reordering(self):
        j=m.Journal(); j.append({'n':1}); checkpoint=j.append({'n':2})
        j.rows.reverse(); self.assertFalse(j.verify(checkpoint)); j.rows.reverse()
        j.rows.pop(); self.assertFalse(j.verify(checkpoint))

if __name__ == '__main__':
    unittest.main()
