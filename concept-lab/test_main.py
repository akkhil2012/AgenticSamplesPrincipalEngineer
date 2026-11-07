import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_model_observes_tool_result(self): self.assertEqual(m.demo()['answer'],'ticket open')
    def test_loop_and_policy(self):
        model=lambda _: {'kind':'tool','tool':'write'}
        with self.assertRaises(PermissionError): m.run(model, {'write':lambda:1}, set())
        with self.assertRaises(RuntimeError): m.run(model, {'write':lambda:1}, {'write'}, 2)

if __name__ == '__main__':
    unittest.main()
