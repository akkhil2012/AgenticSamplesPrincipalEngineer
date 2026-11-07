import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_crash_resume(self): self.assertEqual(m.demo()['resumed_steps'],['report'])
    def test_workflow_isolation(self):
        with m.tempfile.TemporaryDirectory() as tmp:
            p=m.Path(tmp)/'s.db'; m.resume(p,'a',[('s',lambda:'x')])
            self.assertEqual(m.resume(p,'b',[('s',lambda:'y')]),['s'])

if __name__ == '__main__':
    unittest.main()
