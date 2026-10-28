import unittest, textkit
class T(unittest.TestCase):
    def test_short(self): self.assertEqual(textkit.truncate('abc', 5), 'abc')
