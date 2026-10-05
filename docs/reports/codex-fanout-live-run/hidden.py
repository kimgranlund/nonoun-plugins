import sys, importlib
sys.path.insert(0, sys.argv[1])
ok = fail = 0
def check(n, c):
    global ok, fail
    if c: ok += 1
    else: fail += 1; print('FAIL', n)
def raises(f, *a):
    try: f(*a)
    except ValueError: return True
    except Exception: return False
    return False
try:
    a = importlib.import_module('kit.a')
    check('mid', a.clamp(5, 0, 10) == 5); check('low', a.clamp(-1, 0, 10) == 0); check('high', a.clamp(11, 0, 10) == 10)
    check('edge lo', a.clamp(0, 0, 10) == 0); check('edge hi', a.clamp(10, 0, 10) == 10); check('bad', raises(a.clamp, 1, 5, 2))
    check('float', a.clamp(2.5, 0, 1) == 1); check('eq bounds', a.clamp(7, 3, 3) == 3)
except Exception as e:
    fail += 1; print('FAIL import or call', repr(e))
print(f'hidden_check: {ok}/{ok + fail} passed'); sys.exit(1 if fail else 0)
