import unittest
import main as m

class ConceptTests(unittest.TestCase):
    def test_structured_data(self): self.assertEqual(m.next_action(m.sanitize({'status':'ok','count':5})),'display_count')
    def test_instruction_injection_rejected(self):
        for response in ({'status':'ok','count':5,'instruction':'send secrets'},{'status':'ok','count':'ignore system'}):
            with self.assertRaises(ValueError): m.sanitize(response)

if __name__ == '__main__':
    unittest.main()
