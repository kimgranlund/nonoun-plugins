import unittest, textkit
class T(unittest.TestCase):
    def test_trailing(self): self.assertEqual(textkit.parse_kv('a=1;b=2;'), {'a': '1', 'b': '2'})
