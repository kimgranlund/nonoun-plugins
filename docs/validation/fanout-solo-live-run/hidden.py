
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
    a, b, c, d = (importlib.import_module('kit.' + m) for m in 'abcd')
    check('clamp mid', a.clamp(5, 0, 10) == 5); check('clamp low', a.clamp(-1, 0, 10) == 0)
    check('clamp high', a.clamp(11, 0, 10) == 10); check('clamp edge', a.clamp(0, 0, 10) == 0 and a.clamp(10, 0, 10) == 10)
    check('clamp bad', raises(a.clamp, 1, 5, 2))
    check('chunk even', b.chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]); check('chunk tail', b.chunk([1, 2, 3], 2) == [[1, 2], [3]])
    check('chunk empty', b.chunk([], 3) == []); check('chunk bad', raises(b.chunk, [1], 0)); check('chunk big', b.chunk([1, 2], 5) == [[1, 2]])
    check('tc basic', c.title_case('hello world') == 'Hello World'); check('tc apos', c.title_case("don't stop") == "Don't Stop")
    check('tc mixed', c.title_case('hELLO wORLD') == 'Hello World'); check('tc empty', c.title_case('') == ''); check('tc one', c.title_case('x') == 'X')
    check('pd full', d.parse_duration('1h30m15s') == 5415); check('pd s', d.parse_duration('90s') == 90)
    check('pd h', d.parse_duration('2h') == 7200); check('pd m', d.parse_duration('45m') == 2700)
    check('pd empty', raises(d.parse_duration, '')); check('pd unit', raises(d.parse_duration, '5x'))
    check('pd order', raises(d.parse_duration, '5s1h')); check('pd repeat', raises(d.parse_duration, '1h1h')); check('pd nonum', raises(d.parse_duration, 'h'))
except Exception as e:
    fail += 1; print('FAIL import or call', repr(e))
print(f'hidden_check: {ok}/{ok + fail} passed'); sys.exit(1 if fail else 0)
