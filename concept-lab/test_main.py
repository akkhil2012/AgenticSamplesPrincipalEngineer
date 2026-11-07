import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_shadow_and_rollback(self): self.assertEqual(m.demo()['after_rollback'],'v1')
    def test_model_and_quality_gates(self):
        old=m.Index('v1',2,{'d':[1,0]}); new=m.Index('v2',2,{'d':[0,1]}); mig=m.Migration(old,new)
        with self.assertRaises(ValueError): old.search('v2',[1,0])
        with self.assertRaises(ValueError): mig.promote(.5)
        self.assertIs(mig.active,old)

if __name__ == '__main__':
    unittest.main()
