#!/usr/bin/env python3
"""Estimated cost for sub-agent runs: tokens times a per-model blended USD rate.

Usage: cost_estimate.py selftest

A sub-agent run reports no total_cost_usd, only a token count. estimate(model, usage) prices that count
with adapters/claude/prices.json (blended USD per million tokens, per model family) and returns
(cost_usd, basis, reason): cost_usd rounded to 6 places and basis "tokens x blended", or None and a reason
when usage holds no token count or the model has no price. Never zero for a missing usage block.
usage may hold subagent_tokens (the sub-agent notice) or the result-event fields input_tokens,
cache_creation_input_tokens, cache_read_input_tokens, output_tokens (summed). The estimate is marked
cost_estimated true by the caller. Transcript usage is priced per field (basis "usage fields x rates", see below).

selftest calibrates the table against recorded runs.jsonl lines with both usage and a real cost_usd: per
model with at least 3 such lines, the aggregate estimate must be within 35 percent of the aggregate actual.

Per-field usage (a transcript or result event) is priced field by field with usage_input x usage_multipliers when
the file has them (basis "usage fields x rates"); the calibration over headless history stays blended.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
PRICES = HERE.parent / 'adapters' / 'claude' / 'prices.json'
BASIS = 'tokens x blended'
BASIS_USAGE = 'usage fields x rates'
TOKEN_KEYS = ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens')
TOLERANCE = 0.35


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0


def _read(path=PRICES):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def load(path=PRICES):
    m = _read(path).get('models', {})
    return m if isinstance(m, dict) else {}


def usage_rates(path=PRICES):
    """({family: input USD per million}, {token field: multiplier}) from the price file."""
    d = _read(path)
    r, m = d.get('usage_input'), d.get('usage_multipliers')
    return (r if isinstance(r, dict) else {}), (m if isinstance(m, dict) else {})


def usage_calibration(path=PRICES):
    """{token field: factor} that scales transcript counts for the streamed-usage undercount (T-0331)."""
    c = _read(path).get('usage_calibration')
    return {k: v for k, v in c.items() if _num(v)} if isinstance(c, dict) else {}


def transcript_usage(path):
    """Summed usage fields over a sub-agent or session transcript (jsonl), one count per message id; None if unreadable.

    The host writes several lines per message id while it streams; the first holds early partial counts (output 8),
    the last the final ones, so the last line per id wins (T-0332: cache fields then match the host exactly)."""
    last, tot = {}, dict.fromkeys(TOKEN_KEYS, 0)
    try:
        lines = pathlib.Path(path).read_text(encoding='utf-8').splitlines()
    except OSError:
        return None
    for line in lines:
        try:
            msg = json.loads(line).get('message')
        except (ValueError, AttributeError):
            continue
        u = msg.get('usage') if isinstance(msg, dict) else None
        if isinstance(u, dict):
            last[msg.get('id')] = u
    for u in last.values():
        for k in TOKEN_KEYS:
            if _num(u.get(k)):
                tot[k] += u[k]
    return tot if any(tot.values()) else None


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


def estimate(model, usage, table=None, by_field=True):
    """(cost_usd, basis, reason): the estimate, or None with a reason."""
    table = load() if table is None else table
    n = tokens(usage)
    if n is None:
        return None, None, 'no usage block'
    fam = family(model, table)
    rates, mult = usage_rates()
    if by_field and not _num(usage.get('subagent_tokens')) and fam in rates and _num(rates[fam]) and any(k in mult for k in TOKEN_KEYS):
        # Per-field usage (input, output, cache read and write): each field at its own rate, not one blended rate.
        cal = usage_calibration()
        usd = sum(usage[k] * cal.get(k, 1) * mult.get(k, 1) for k in TOKEN_KEYS if _num(usage.get(k))) * rates[fam] / 1e6
        return round(usd, 6), BASIS_USAGE, None
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
            est, _, _ = estimate(r.get('model'), r.get('usage'), table, by_field=False)
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
    c, b, r = estimate('opus', {'input_tokens': 500_000, 'output_tokens': 500_000}, table, by_field=False)
    expect('estimate: sums result-event fields', c == table['opus'])
    expect('no usage block: null with reason, never zero', estimate('opus', None, table) == (None, None, 'no usage block')
           and estimate('opus', {}, table)[0] is None)
    expect('unknown model: null with reason', estimate('gpt', {'subagent_tokens': 5}, table)[0] is None)

    # Live evidence (T-0328): the stored L2 and L3 verifier rows priced from transcript usage vs host totals.
    rates, mult = usage_rates()
    expect('usage rates and multipliers load', all(_num(rates.get(k)) for k in ('fable', 'opus', 'sonnet')) and mult)
    # Final per-message counts (last line per message id); host costUSD from the stored host totals.
    live = [('opus', {'input_tokens': 14, 'output_tokens': 5068, 'cache_read_input_tokens': 223021,
                      'cache_creation_input_tokens': 41554}, 0.3538),  # L2 verifier
            ('fable', {'input_tokens': 260, 'output_tokens': 14852, 'cache_read_input_tokens': 410383,
                       'cache_creation_input_tokens': 60757}, 2.3025),  # R1 verifier
            ('fable', {'input_tokens': 486, 'output_tokens': 20945, 'cache_read_input_tokens': 900039,
                       'cache_creation_input_tokens': 68277}, 3.6384)]  # final-rerun verifier (cache fields equal the host's)
    expect('docstring names the transcript label and does not call transcript pricing unassumed',
           BASIS_USAGE in __doc__ and 'is not assumed' not in __doc__)
    for fam, u, host in live:
        e, b, _ = estimate(fam, u, table)
        expect('live %s verifier row: estimate %s vs host %.4f within 35 percent' % (fam, e, host),
               e is not None and b == BASIS_USAGE and abs(e - host) <= TOLERANCE * host)
        # Negative control: the old blended count (cache reads excluded) misses the band.
        old = estimate(fam, {'subagent_tokens': u['input_tokens'] + u['output_tokens']}, table)[0]
        expect('negative control: %s blended count without cache is outside the band' % fam, abs(old - host) > TOLERANCE * host)
    u0 = live[2][1]
    expect('negative control: without the calibration the final-rerun row falls under the band',
           sum(u0[k] * mult.get(k, 1) for k in TOKEN_KEYS) * rates['fable'] / 1e6 / 3.6384 < 0.65)
    with tempfile.TemporaryDirectory() as t2:
        tf = pathlib.Path(t2) / 't.jsonl'
        m = lambda i, o: json.dumps({'message': {'id': i, 'usage': {'input_tokens': 1, 'output_tokens': o}}})
        tf.write_text('\n'.join([m('a', 8), m('a', 8), m('a', 10), m('b', 5), 'junk']) + '\n', encoding='utf-8')
        expect('transcript_usage sums the last line once per message id', transcript_usage(tf) ==
               {'input_tokens': 2, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'output_tokens': 15})
        expect('transcript_usage: missing file is None', transcript_usage(pathlib.Path(t2) / 'nope') is None)

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
