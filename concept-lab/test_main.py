import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_minimized_summary(self):
        r=m.demo(); self.assertTrue(r['validated']); self.assertEqual(r['summary'],[{'task_id':'w1','status':'pending'}])
    def test_hallucinated_fact_and_secret(self):
        source=[{'task_id':'w','status':'pending'}]
        self.assertFalse(m.validate([{'task_id':'w','status':'approved'}],source))
        self.assertFalse(m.validate([{'email':'secret'}],source))

if __name__ == '__main__':
    unittest.main()
