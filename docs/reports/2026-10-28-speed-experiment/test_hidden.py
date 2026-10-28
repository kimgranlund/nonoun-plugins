import unittest, textkit as t
class H(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(t.slugify('  Hi,  There!  '), 'hi-there')
    def test_words(self):
        self.assertEqual(t.word_count(''), 0); self.assertEqual(t.word_count('   '), 0); self.assertEqual(t.word_count('one'), 1)
    def test_trunc(self):
        self.assertEqual(t.truncate('abcdef', 4), 'abc…'); self.assertEqual(t.truncate('abcd', 4), 'abcd')
    def test_kv(self):
        self.assertEqual(t.parse_kv(''), {}); self.assertEqual(t.parse_kv('a=1;;b=x=y'), {'a': '1', 'b': 'x=y'})
    def test_median(self):
        self.assertEqual(t.median([3, 1, 2]), 2); self.assertEqual(t.median([5]), 5); self.assertEqual(t.median([1, 2]), 1.5)
