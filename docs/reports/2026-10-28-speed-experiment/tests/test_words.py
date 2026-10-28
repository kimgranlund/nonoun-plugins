import unittest, textkit
class T(unittest.TestCase):
    def test_spaces(self): self.assertEqual(textkit.word_count('a  b c'), 3)
