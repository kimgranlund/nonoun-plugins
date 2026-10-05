import unittest
from util import whisper


class T(unittest.TestCase):
    def test_whisper(self):
        self.assertEqual(whisper("Hi"), "hi...")


if __name__ == "__main__":
    unittest.main()
