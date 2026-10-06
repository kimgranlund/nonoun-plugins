#!/usr/bin/env python3
"""Estimated cost for sub-agent runs: tokens times a per-model blended USD rate.

Usage: cost_estimate.py selftest

A sub-agent run reports no total_cost_usd, only a token count. estimate(model, usage) prices that count
with adapters/claude/prices.json (blended USD per million tokens, per model family) and returns
(cost_usd, basis, reason): cost_usd rounded to 6 places and basis "tokens x blended", or None and a reason
when usage holds no token count or the model has no price. Never zero for a missing usage block.
usage may hold subagent_tokens (the sub-agent notice) or the result-event fields input_tokens,
cache_creation_input_tokens, cache_read_input_tokens, output_tokens (summed). The estimate is marked
cost_estimated true by the caller. Probe P5 (transcript usage x price) is not assumed.

selftest calibrates the table against recorded runs.jsonl lines with both usage and a real cost_usd: per
model with at least 3 such lines, the aggregate estimate must be within 35 percent of the aggregate actual.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
PRICES = HERE.parent / 'adapters' / 'claude' / 'prices.json'
BASIS = 'tokens x blended'
TOKEN_KEYS = ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens')
TOLERANCE = 0.35


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0


def load(path=PRICES):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding='utf-8')).get('models', {})
    except (OSError, ValueError, AttributeError):
        return {}


def family(model, table):
    m = (model or '').lower()
    return next((k for k in table if k in m), None)


def tokens(usage):
    """Total token count from a usage block, or None when it holds none."""
    if not isinstance(usage, dict):
        return None
    if _num(usage.get('subagent_tokens')):
        return usage['subagent_tokens']
    vals = [usage[k] for k in TOKEN_KEYS if _num(usage.get(k))]
    return sum(vals) if vals else None


def estimate(model, usage, table=None):
    """(cost_usd, basis, reason): the estimate, or None with a reason."""
    table = load() if table is None else table
    n = tokens(usage)
    if n is None:
        return None, None, 'no usage block'
    fam = family(model, table)
    if fam is None or not _num(table.get(fam)):
        return None, None, 'no price for model %s' % model
    return round(n / 1e6 * table[fam], 6), BASIS, None


def calibration(root, table):
    """{family: [actual, estimated, n]} over runs.jsonl under root with usage and a real cost_usd."""
    out = {}
    for f in pathlib.Path(root).rglob('runs.jsonl'):
        try:
            lines = f.read_text(encoding='utf-8').splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            c = r.get('cost_usd') if isinstance(r, dict) else None
            if not (_num(c) and c > 0) or r.get('cost_estimated') or r.get('transport') == 'subagent':
                continue
            est, _, _ = estimate(r.get('model'), r.get('usage'), table)
            fam = family(r.get('model'), table)
            if est is None:
                continue
            a = out.setdefault(fam, [0.0, 0.0, 0])
            a[0] += c
            a[1] += est
            a[2] += 1
    return out


def selftest():
    import tempfile
    misses, oks = [], []

    def expect(label, cond):
        (oks if cond else misses).append(label)

    table = load()
    expect('price table loads with fable, opus, sonnet', all(_num(table.get(k)) for k in ('fable', 'opus', 'sonnet')))
    c, b, r = estimate('claude-sonnet-5-5', {'subagent_tokens': 1_000_000}, table)
    expect('estimate: tokens x blended', c == table['sonnet'] and b == BASIS and r is None)
    c, b, r = estimate('opus', {'input_tokens': 500_000, 'output_tokens': 500_000}, table)
    expect('estimate: sums result-event fields', c == table['opus'])
    expect('no usage block: null with reason, never zero', estimate('opus', None, table) == (None, None, 'no usage block')
           and estimate('opus', {}, table)[0] is None)
    expect('unknown model: null with reason', estimate('gpt', {'subagent_tokens': 5}, table)[0] is None)

    def run(root, rows):
        d = pathlib.Path(root)
        d.mkdir(parents=True, exist_ok=True)
        (d / 'runs.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in rows), encoding='utf-8')

    def within(cal):
        return all(abs(e - a) <= TOLERANCE * a for a, e, n in cal.values() if n >= 3)

    with tempfile.TemporaryDirectory() as tmp:
        good = [{'model': 'sonnet', 'usage': {'input_tokens': 1_000_000}, 'cost_usd': 0.81} for _ in range(3)]
        run(tmp + '/good', good)
        cal = calibration(tmp + '/good', table)
        expect('calibration: fixture on the table passes', cal.get('sonnet', [0, 0, 0])[2] == 3 and within(cal))
        # Negative control: actual cost double the table's, so the table is off by more than 35 percent.
        run(tmp + '/bad', [dict(x, cost_usd=1.62) for x in good])
        expect('negative control: a table 50 percent low is rejected', not within(calibration(tmp + '/bad', table)))

    repo = HERE.parent.parent.parent
    cal = calibration(repo / '.sdlc', table)
    for fam, (a, e, n) in sorted(cal.items()):
        if n >= 3:
            expect('recorded history %s (n=%d): estimate %.2f vs actual %.2f within 35 percent' % (fam, n, e, a),
                   abs(e - a) <= TOLERANCE * a)
    for m in misses:
        print('FAIL ' + m)
    print('cost_estimate selftest: %d ok, %d failed' % (len(oks), len(misses)))
    return 1 if misses else 0


if __name__ == '__main__':
    sys.exit(selftest() if sys.argv[1:] == ['selftest'] else (print(__doc__) or 2))
