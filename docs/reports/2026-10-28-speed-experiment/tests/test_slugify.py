import unittest, textkit
class T(unittest.TestCase):
    def test_lower(self): self.assertEqual(textkit.slugify('Hello World'), 'hello-world')
