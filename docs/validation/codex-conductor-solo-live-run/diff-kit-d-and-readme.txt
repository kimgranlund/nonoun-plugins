diff --git a/README.md b/README.md
index e6cde43..c0cff8e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,9 @@
 # kit

 Small helpers.
+
+Use `from kit.d import parse_duration` to convert a duration string to integer
+seconds: `parse_duration("1h30m15s")` returns `5415`. Supply non-negative integers
+followed by `h`, `m`, or `s`, each at most once and in that order; components may
+be omitted, so `"2h"` and `"90s"` are also valid. Empty or malformed strings
+raise `ValueError`.
diff --git a/kit/d.py b/kit/d.py
index a478c11..fecd8ff 100644
--- a/kit/d.py
+++ b/kit/d.py
@@ -1 +1,15 @@
 """kit.d: duration helpers."""
+
+import re
+
+
+def parse_duration(text):
+    """Return seconds from ordered integer h, m, and s components.
+
+    Raise ValueError if text is empty or does not match the duration format.
+    """
+    match = re.fullmatch(r"(?:([0-9]+)h)?(?:([0-9]+)m)?(?:([0-9]+)s)?", text)
+    if not text or match is None:
+        raise ValueError(f"Invalid duration: {text!r}")
+    hours, minutes, seconds = (int(value or 0) for value in match.groups())
+    return hours * 3600 + minutes * 60 + seconds
