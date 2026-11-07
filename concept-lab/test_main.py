import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_reopen_and_resume(self): self.assertEqual(m.demo()['recovered'],'completed')
    def test_stale_transition(self):
        db=m.connect(':memory:'); db.execute("INSERT INTO workflows VALUES ('w','pending')"); db.commit()
        m.transition(db,'w','pending','running')
        with self.assertRaises(RuntimeError): m.transition(db,'w','pending','running')
        db.close()

if __name__ == '__main__':
    unittest.main()
