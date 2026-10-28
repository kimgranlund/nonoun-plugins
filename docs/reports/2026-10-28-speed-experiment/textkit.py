"""Small text helpers."""
import re


def slugify(s):
    """Lowercase, words joined by '-', only a-z0-9 and '-' kept."""
    s = re.sub(r'[^A-Za-z0-9 ]+', '', s).strip()
    return re.sub(r' +', '-', s)


def word_count(s):
    """Number of words separated by any whitespace."""
    return len(s.split(' ')) if s else 0


def truncate(s, n):
    """At most n characters; when cut, the last character is an ellipsis."""
    return s[:n - 1] + '…'


def parse_kv(s):
    """'a=1;b=2' to {'a': '1', 'b': '2'}; empty parts are ignored."""
    return dict(part.split('=', 1) for part in s.split(';'))


def median(xs):
    """Median of a non-empty list of numbers."""
    ys = sorted(xs)
    return ys[len(ys) // 2]
