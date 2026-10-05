
import sys, importlib
sys.path.insert(0, sys.argv[1])
ok = fail = 0
def check(name, cond):
    global ok, fail
    if cond: ok += 1
    else:
        fail += 1; print('FAIL', name)
def raises(f, *a):
    try: f(*a)
    except ValueError: return True
    except Exception: return False
    return False
try:
    d = importlib.import_module('kit.d')
    check('pd full', d.parse_duration('1h30m15s') == 5415); check('pd s', d.parse_duration('90s') == 90)
    check('pd h', d.parse_duration('2h') == 7200); check('pd m', d.parse_duration('45m') == 2700)
    check('pd empty', raises(d.parse_duration, '')); check('pd unit', raises(d.parse_duration, '5x'))
    check('pd order', raises(d.parse_duration, '5s1h')); check('pd repeat', raises(d.parse_duration, '1h1h')); check('pd nonum', raises(d.parse_duration, 'h'))
except Exception as e:
    fail += 1; print('FAIL import or call', repr(e))
print(f'hidden_check: {ok}/{ok + fail} passed'); sys.exit(1 if fail else 0)
