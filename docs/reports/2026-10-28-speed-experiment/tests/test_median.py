import unittest, textkit
class T(unittest.TestCase):
    def test_even(self): self.assertEqual(textkit.median([4, 1, 3, 2]), 2.5)
