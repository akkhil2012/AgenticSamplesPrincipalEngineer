import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_total_budget_and_recency(self):
        r=m.demo(); self.assertEqual(r['messages'],['recent','now'])
        self.assertLessEqual(m.estimate(r['system'])+sum(map(m.estimate,r['messages']))+r['output_reserve'],20)
    def test_oversize_system_and_message(self):
        with self.assertRaises(ValueError): m.pack('too long',[],3,1)
        self.assertEqual(m.pack('p',['oversized'],3,1)['messages'],[])

if __name__ == '__main__':
    unittest.main()
