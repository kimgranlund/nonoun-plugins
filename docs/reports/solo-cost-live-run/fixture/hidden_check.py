import sys, importlib
sys.path.insert(0, sys.argv[1])
u = importlib.import_module("util")
cases = [("hi", "HI!"), ("", "!"), ("Mixed Case", "MIXED CASE!")]
bad = [(a, b, u.shout(a)) for a, b in cases if u.shout(a) != b]
print("hidden_check: %d/%d passed" % (len(cases) - len(bad), len(cases)))
sys.exit(1 if bad else 0)
