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
    d = importlib.import_module('kit.d')
    check('full', d.parse_duration('1h30m15s') == 5415); check('s', d.parse_duration('90s') == 90)
    check('h', d.parse_duration('2h') == 7200); check('m', d.parse_duration('45m') == 2700); check('zero', d.parse_duration('0s') == 0)
    check('empty', raises(d.parse_duration, '')); check('unit', raises(d.parse_duration, '5x'))
    check('order', raises(d.parse_duration, '5s1h')); check('repeat', raises(d.parse_duration, '1h1h')); check('nonum', raises(d.parse_duration, 'h'))
    check('int', type(d.parse_duration('1m')) is int)
    check('readme', 'parse_duration' in open(sys.argv[1] + '/README.md').read())
except Exception as e:
    fail += 1; print('FAIL import or call', repr(e))
print(f'hidden_check: {ok}/{ok + fail} passed'); sys.exit(1 if fail else 0)
