#!/usr/bin/env python3
"""Run an evaluation suite against a target command and write run.json and report.md.

Usage: run_suite.py SUITE [--target CMD] [--target-version V] [--split dev|holdout|all] [--tune FILE]
                    [--gates FILE] [--vocabulary FILE] [--human-results FILE] [--traffic FILE]
                    [--max-drift X] [--out DIR] [--timeout S] [--strict]

The target reads one case's input as JSON on stdin and writes its output as JSON on stdout; an output
mapping may carry `confidence` (0 to 1) or `abstain: true`.
Exit 0 when no gate failed, 1 when a gate failed or tag drift exceeded the limit (or a gate is
insufficient_n or stale under --strict), 2 when the run was refused or an input could not be read.
Protocol and file shapes: references/model.md. Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import datetime
import json
import math
import re
import shlex
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

import validate_suite as vs

OUTCOMES = ('pass', 'fail', 'score', 'abstain')
Z95 = 1.959964
BANDS = 10  # equal-width confidence bands for calibration


class Refusal(Exception):
    """The run cannot start (exit 2)."""


def wilson(passes, n, z=Z95):
    """95% Wilson score interval for a proportion; None when n is 0."""
    if n == 0:
        return None
    p = passes / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)]


def dig(value, field):
    """Read a dotted field from a JSON value; None when absent."""
    for part in field.split('.') if field else []:
        value = value.get(part) if isinstance(value, dict) else None
    return value


def call(argv, payload, timeout):
    """Run a command with JSON on stdin. Return (parsed stdout or None, exit code, error text)."""
    try:
        proc = subprocess.run(argv, input=json.dumps(payload, default=str), capture_output=True,
                              text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, None, str(exc)
    try:
        output = json.loads(proc.stdout) if proc.stdout.strip() else None
    except ValueError:
        output = None
    return output, proc.returncode, proc.stderr.strip()[-300:]


def verdict(output, code, error):
    """Outcome of a command grader: a JSON {outcome, detail} wins, else exit 0 pass, 1 fail, other abstain."""
    if isinstance(output, dict) and output.get('outcome') in OUTCOMES:
        return output['outcome'], output.get('detail', '')
    if code == 0:
        return 'pass', ''
    if code == 1:
        return 'fail', error or 'the grader exited 1'
    return 'abstain', f'grader error: {error or code}'


def tokens(value):
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, default=str)
    return re.findall(r'\w+', text.casefold())


def token_f1(actual, gold):
    a, g = Counter(tokens(actual)), Counter(tokens(gold))
    common = sum((a & g).values())
    if not common:
        return 0.0
    precision, recall = common / sum(a.values()), common / sum(g.values())
    return round(2 * precision * recall / (precision + recall), 4)


def compared(case, config, output):
    field = config.get('field')
    actual = dig(output, field) if field else output
    expected = case['expected']
    if field and isinstance(expected, dict) and field in expected:
        expected = expected[field]
    return actual, expected


def grade(grader, case, output, target_error, ran_target, human, vocabulary, timeout):
    """Return (outcome, detail) for one case and grader."""
    kind, config = grader['kind'], grader['config']
    if kind == 'human':
        record = human.get((case['id'], grader['id']))
        return (record['outcome'], record.get('detail', '')) if record else ('abstain', 'no recorded human outcome')
    if not ran_target:
        return 'abstain', 'no target command was given'
    if target_error:
        return 'fail', f'target error: {target_error}'
    if isinstance(output, dict) and output.get('abstain') is True:
        return 'abstain', 'the target abstained'
    payload = {'input': case['input'], 'output': output, 'expected': case['expected']}
    if kind == 'exact':
        actual, expected = compared(case, config, output)
        if vocabulary and isinstance(actual, str) and isinstance(expected, str) and vocabulary.resolve(actual):
            actual, expected = vocabulary.resolve(actual), vocabulary.resolve(expected) or expected
        elif config.get('normalize') and isinstance(actual, str) and isinstance(expected, str):
            actual, expected = vs.normalize(actual), vs.normalize(expected)
        if actual == expected:
            return 'pass', ''
        return 'fail', f'expected {json.dumps(expected, default=str)}, got {json.dumps(actual, default=str)}'
    if kind == 'programmatic' or (kind == 'reference' and config.get('command')):
        return verdict(*call(shlex.split(config['command']), payload, timeout))
    if kind == 'reference':
        score = token_f1(*compared(case, config, output))
        return ('pass' if score >= config.get('pass_at', 0.8) else 'fail'), {'score': score}
    results = {}
    for criterion in config['criteria']:  # rubric-model: each criterion is checked on its own
        results[criterion] = verdict(*call(shlex.split(config['command']), dict(payload, criterion=criterion), timeout))[0]
    outcomes = set(results.values())
    outcome = 'fail' if 'fail' in outcomes else 'abstain' if outcomes - {'pass'} else 'pass'
    return outcome, {'criteria': results}


def counts_as(result, grader):
    """Map a grader result to pass, fail or abstain for the pass_rate metric."""
    outcome = result['outcome']
    if outcome == 'score':
        score = result['detail'].get('score') if isinstance(result['detail'], dict) else None
        if not isinstance(score, (int, float)):
            return 'abstain'
        return 'pass' if score >= grader['config'].get('pass_at', 0.5) else 'fail'
    return outcome


def case_outcome(results):
    if 'fail' in results:
        return 'fail'
    if not results or 'abstain' in results:
        return 'abstain'
    return 'pass'


def read_human(path, suite):
    if not path:
        return {}
    data = vs.read_yaml(path)
    if not isinstance(data, list):
        raise Refusal(f'{path}: human results must be a list of {{case_id, grader_id, outcome, detail}}.')
    records, cases = {}, {c['id'] for c in suite.cases}
    for item in data:
        if not isinstance(item, dict) or item.get('outcome') not in OUTCOMES:
            raise Refusal(f'{path}: each human result needs case_id, grader_id and an outcome in {", ".join(OUTCOMES)}.')
        case_id, grader_id = str(item.get('case_id')), item.get('grader_id')
        if grader_id not in suite.graders:
            raise Refusal(f"{path}: unknown-grader: grader '{grader_id}' is not declared in suite '{suite.id}'.")
        if case_id not in cases:
            raise Refusal(f"{path}: case '{case_id}' is not in suite '{suite.id}'.")
        records[(case_id, grader_id)] = item
    return records


def measure(members, outcomes):
    """pass_rate over cases: value, n (answered cases), Wilson interval, passes and coverage (share answered)."""
    answered = [outcomes[c['id']] for c in members if outcomes[c['id']] != 'abstain']
    n, passes = len(answered), answered.count('pass')
    return {'value': round(passes / n, 4) if n else None, 'n': n, 'interval': wilson(passes, n), 'passes': passes,
            'coverage': round(n / len(members), 4) if members else None}


def by_direction(members, outcomes):
    """pass_rate per expected truth value, for the members that state one; empty when none does."""
    directions = {}
    for value in (True, False):
        cases = [c for c in members if vs.direction(c['expected']) is value]
        if cases:
            directions[str(value).lower()] = measure(cases, outcomes)
    return directions


def calibration(cases, outcomes, confidence):
    """Per-band accuracy and expected calibration error over answered dev cases that returned a confidence."""
    scored = [(confidence[c['id']], outcomes[c['id']] == 'pass') for c in cases
              if c['split'] == 'dev' and c['id'] in confidence and outcomes[c['id']] != 'abstain']
    if not scored:
        return None
    bands, ece = [], 0.0
    for b in range(BANDS):
        low, high = b / BANDS, (b + 1) / BANDS
        members = [(p, ok) for p, ok in scored if low <= p < high or (b == BANDS - 1 and p == 1.0)]
        if not members:
            continue
        accuracy = sum(ok for _, ok in members) / len(members)
        mean = sum(p for p, _ in members) / len(members)
        ece += len(members) / len(scored) * abs(accuracy - mean)
        bands.append({'range': [low, high], 'n': len(members), 'accuracy': round(accuracy, 4),
                      'confidence': round(mean, 4)})
    return {'bands': bands, 'ece': round(ece, 4), 'n': len(scored)}


def gate_status(gate, metric, directions, target_version, suite_version):
    """Return (status, note) for one gate; earlier checks win."""
    if 'suite_version' in gate and str(gate['suite_version']) != str(suite_version):
        return 'open', f"pinned to suite version {gate['suite_version']}"
    if target_version is not None and str(gate['pinned_target_version']) != str(target_version):
        return 'stale', f"pinned to target version {gate['pinned_target_version']}; re-pin after review"
    if metric['n'] < gate['min_n']:
        return 'insufficient_n', f"n {metric['n']} is below min_n {gate['min_n']}"
    if 'min_coverage' in gate and metric['coverage'] < gate['min_coverage']:
        return 'failed', f"coverage {fmt(metric['coverage'])} is below min_coverage {gate['min_coverage']}"
    if metric['value'] < gate['threshold']:
        return 'failed', ''
    weak = [f"{d} {fmt(m['value'])}" for d, m in directions.items() if m['n'] and m['value'] < gate['threshold']]
    if weak:
        return 'failed', f"direction below threshold: {', '.join(weak)}"
    return 'passed', ''


def drift(cases, path, limit):
    traffic = vs.read_yaml(path)
    if not isinstance(traffic, dict) or not all(isinstance(v, (int, float)) and v >= 0 for v in traffic.values()):
        raise Refusal(f'{path}: traffic must map each tag to a live count.')
    observed = Counter(t for c in cases for t in c['tags'])
    live_total, case_total = sum(traffic.values()), sum(observed.values())
    tags = set(traffic) | set(observed)
    if not live_total or not case_total:
        distance = 1.0
    else:
        distance = 0.5 * sum(abs(traffic.get(t, 0) / live_total - observed.get(t, 0) / case_total) for t in tags)
    return {'distance': round(distance, 4), 'max': limit, 'exceeded': distance > limit}


def evaluate(suite, gates, args, vocabulary):
    started = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    splits = {'dev': ('dev',), 'holdout': ('holdout',), 'all': ('dev', 'holdout')}[args.split]
    cases = [c for c in suite.active_cases() if c['split'] in splits]
    human = read_human(args.human_results, suite)
    argv = shlex.split(args.target) if args.target else None
    results, by_case, confidence = [], {}, {}
    for case in cases:
        output, error = None, None
        graders = [suite.graders[g] for g in suite.case_graders(case)]
        if argv and any(g['kind'] != 'human' for g in graders):
            output, code, stderr = call(argv, case['input'], args.timeout)
            if code is None or code != 0:
                error = stderr or f'exit {code}'
            elif output is None:
                error = 'stdout was not JSON'
            elif isinstance(output, dict) and isinstance(output.get('confidence'), (int, float)) \
                    and not isinstance(output['confidence'], bool) and 0 <= output['confidence'] <= 1:
                confidence[case['id']] = output['confidence']
        for grader in graders:
            outcome, detail = grade(grader, case, output, error, bool(argv), human, vocabulary, args.timeout)
            result = {'case_id': case['id'], 'grader_id': grader['id'], 'outcome': outcome, 'detail': detail}
            results.append(result)
            by_case.setdefault(case['id'], []).append(counts_as(result, grader))
    outcomes = {c['id']: case_outcome(by_case.get(c['id'], [])) for c in cases}
    metrics = {}
    for slice_id in [vs.ALL] + list(suite.slices):
        members = suite.slice_cases(slice_id, cases)
        metrics[slice_id] = measure(members, outcomes)
        directions = by_direction(members, outcomes)
        if directions:
            metrics[slice_id]['directions'] = directions
    gate_results = []
    for gate in gates:
        members = suite.gate_cases(gate, cases)
        metric, directions = measure(members, outcomes), by_direction(members, outcomes)
        status, note = gate_status(gate, metric, directions, args.target_version, suite.version)
        gate_results.append(dict(gate, status=status, value=metric['value'], n=metric['n'],
                                 coverage=metric['coverage'], directions=directions, note=note))
    run = {'id': f"{suite.id}-{started:%Y%m%dT%H%M%SZ}", 'suite_id': suite.id, 'suite_version': suite.version,
           'target_version': args.target_version or 'unversioned',
           'started_at': started.isoformat().replace('+00:00', 'Z'),
           'split': args.split, 'tuning': bool(args.tune), 'results': results, 'metrics': metrics,
           'gates': gate_results}
    if any(c['basis'] for c in cases):
        run['by_basis'] = {b: measure([c for c in cases if c['basis'] == b], outcomes)
                           for b in vs.BASES if b == 'owner' or any(c['basis'] == b for c in cases)}
    calibrated = calibration(cases, outcomes, confidence)
    if calibrated:
        run['calibration'] = calibrated
    if args.traffic:
        run['drift'] = drift(cases, args.traffic, args.max_drift)
    return run, cases, outcomes


def log_holdout(suite, run, cases):
    """Append a line per run that touched holdout cases; return the number of such runs logged."""
    log = suite.path.parent / 'holdout-runs.jsonl'
    held = sum(c['split'] == 'holdout' for c in cases)
    if held:
        with log.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps({'run_id': run['id'], 'suite_id': suite.id, 'suite_version': suite.version,
                                     'started_at': run['started_at'], 'holdout_cases': held}) + '\n')
    if not log.is_file():
        return 0
    return sum(1 for line in log.read_text(encoding='utf-8').splitlines()
               if line.strip() and json.loads(line).get('suite_id') == suite.id)


def fmt(value):
    return 'n/a' if value is None else f'{value:.2f}'


def interval_text(interval):
    return 'n/a' if interval is None else f'{fmt(interval[0])} to {fmt(interval[1])}'


def report(suite, run, outcomes, holdout_runs):
    abstained = sum(o == 'abstain' for o in outcomes.values())
    lines = [f"# Run {run['id']}", '',
             f"- Suite `{suite.id}` version {suite.version}; target version `{run['target_version']}`",
             f"- Split `{run['split']}`; tuning run: {'yes' if run['tuning'] else 'no'}; started {run['started_at']}",
             f'- Cases run: {len(outcomes)} ({abstained} abstained, left out of n); holdout runs logged for this suite: {holdout_runs}',
             '', '## Metrics (pass_rate)', '',
             '| Slice | n | Passes | Value | 95% interval (Wilson) | Coverage |', '|---|---|---|---|---|---|']
    for slice_id, m in run['metrics'].items():
        lines.append(f"| {slice_id} | {m['n']} | {m['passes']} | {fmt(m['value'])} | {interval_text(m['interval'])} "
                     f"| {fmt(m['coverage'])} |")
    directional = [(s, d, m) for s, sm in run['metrics'].items() for d, m in sm.get('directions', {}).items()]
    if directional:
        lines += ['', '## Accuracy per direction', '',
                  'Cases whose expected answer is true and cases whose expected answer is false, scored apart.', '',
                  '| Slice | Expected | n | Passes | Value | 95% interval (Wilson) | Coverage |',
                  '|---|---|---|---|---|---|---|']
        for slice_id, d, m in directional:
            lines.append(f"| {slice_id} | {d} | {m['n']} | {m['passes']} | {fmt(m['value'])} "
                         f"| {interval_text(m['interval'])} | {fmt(m['coverage'])} |")
    if 'by_basis' in run:
        lines += ['', '## By basis (who decided expected)', '',
                  '| Basis | n | Passes | Value | 95% interval (Wilson) | Coverage |', '|---|---|---|---|---|---|']
        for basis, m in run['by_basis'].items():
            lines.append(f"| {basis} | {m['n']} | {m['passes']} | {fmt(m['value'])} | {interval_text(m['interval'])} "
                         f"| {fmt(m['coverage'])} |")
    if 'calibration' in run:
        c = run['calibration']
        lines += ['', '## Calibration (dev)', '',
                  f"Expected calibration error {c['ece']:.3f} over {c['n']} answered dev case(s).", '',
                  '| Confidence band | n | Accuracy | Mean confidence |', '|---|---|---|---|']
        for band in c['bands']:
            lines.append(f"| {fmt(band['range'][0])} to {fmt(band['range'][1])} | {band['n']} | {fmt(band['accuracy'])} "
                         f"| {fmt(band['confidence'])} |")
    lines += ['', '## Gates', '']
    if run['gates']:
        lines += ['| Gate | Slice | Threshold | min_n | n | Value | Coverage | Status | Action | Owner |',
                  '|---|---|---|---|---|---|---|---|---|---|']
        for g in run['gates']:
            status = f"`{g['status']}`" + (f" ({g['note']})" if g['note'] else '')
            lines.append(f"| {g['id']} | {g['slice']} | {g['threshold']} | {g['min_n']} | {g['n']} | {fmt(g['value'])} "
                         f"| {fmt(g['coverage'])} | {status} | {g['action']} | {g['owner']} |")
    else:
        lines.append('No gate reads this suite: these numbers decide nothing yet.')
    if 'drift' in run:
        d = run['drift']
        lines += ['', '## Drift', '',
                  f"Tag distance between cases and live traffic: {d['distance']:.2f} (limit {d['max']:.2f})"
                  + (': exceeded, the run fails.' if d['exceeded'] else '.')]
    failing = [r for r in run['results'] if r['outcome'] == 'fail']
    lines += ['', '## Failing results', '']
    if failing:
        lines += ['| Case | Grader | Detail |', '|---|---|---|']
        for r in failing:
            detail = r['detail'] if isinstance(r['detail'], str) else json.dumps(r['detail'], default=str)
            lines.append(f"| {r['case_id']} | {r['grader_id']} | {detail.replace('|', '/')} |")
    else:
        lines.append('None.')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('suite', help='the suite YAML file')
    parser.add_argument('--target', metavar='CMD', help='command that reads one input as JSON on stdin and writes JSON on stdout')
    parser.add_argument('--target-version', help="the target's version: recorded in run.json, and a gate pinned to "
                                                  'another version is stale (default: unversioned, no stale check)')
    parser.add_argument('--split', choices=('dev', 'holdout', 'all'), default='dev', help='cases to run (default dev)')
    vs.add_input_arguments(parser)
    parser.add_argument('--human-results', metavar='FILE', help='recorded human outcomes: [{case_id, grader_id, outcome, detail}]')
    parser.add_argument('--traffic', metavar='FILE', help='live tag counts for the drift check')
    parser.add_argument('--max-drift', type=float, default=0.2, help='largest allowed tag distance (default 0.2)')
    parser.add_argument('--out', metavar='DIR', help='output folder (default eval-runs/<run id>)')
    parser.add_argument('--timeout', type=float, default=60, help='seconds per target or grader call (default 60)')
    parser.add_argument('--strict', action='store_true', help='exit 1 when a gate is insufficient_n or stale')
    args = parser.parse_args(argv)
    try:
        if args.tune and args.split != 'dev':
            raise Refusal(f'refused: --tune with --split {args.split} would tune on holdout cases; tune on dev only.')
        findings, suites, gates, vocabulary = vs.check([args.suite], args.gates, args.vocabulary, args.tune)
        errors = [f for f in findings if f.severity == 'ERROR']
        if errors:
            raise Refusal('\n'.join(f.line() for f in errors) + f'\nrefused: {args.suite} has {len(errors)} validation error(s).')
        suite = suites[0]
        run, cases, outcomes = evaluate(suite, gates.get(suite.id, []), args, vocabulary)
    except (Refusal, vs.InputError) as exc:
        print(exc, file=sys.stderr)
        return 2
    holdout_runs = log_holdout(suite, run, cases)
    out = Path(args.out or Path('eval-runs') / run['id'])
    out.mkdir(parents=True, exist_ok=True)
    (out / 'run.json').write_text(json.dumps(run, indent=2, default=str) + '\n', encoding='utf-8')
    (out / 'report.md').write_text(report(suite, run, outcomes, holdout_runs), encoding='utf-8')
    statuses = Counter(g['status'] for g in run['gates'])
    print(f"{out / 'run.json'}, {out / 'report.md'}: {len(cases)} case(s), "
          f"pass_rate {fmt(run['metrics'][vs.ALL]['value'])} (n {run['metrics'][vs.ALL]['n']}), "
          f"gates {dict(sorted(statuses.items())) or 'none'}")
    failed = statuses['failed'] or run.get('drift', {}).get('exceeded') or \
        (args.strict and (statuses['insufficient_n'] or statuses['stale']))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
