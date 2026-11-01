#!/usr/bin/env python3
"""Run an evaluation suite against a target command and write run.json and report.md.

Usage: run_suite.py SUITE [--target CMD] [--target-version V] [--split dev|holdout|all] [--tune FILE]
                    [--gates FILE] [--vocabulary FILE] [--human-results FILE] [--traffic FILE]
                    [--max-drift X] [--out DIR] [--timeout S] [--strict]

The target reads one case's input as JSON on stdin and writes its output as JSON on stdout.
Exit 0 when no gate failed, 1 when a gate failed or tag drift exceeded the limit (or a gate is
insufficient_n under --strict), 2 when the run was refused or an input could not be read.
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
    results, by_case = [], {}
    for case in cases:
        output, error = None, None
        graders = [suite.graders[g] for g in suite.case_graders(case)]
        if argv and any(g['kind'] != 'human' for g in graders):
            output, code, stderr = call(argv, case['input'], args.timeout)
            if code is None or code != 0:
                error = stderr or f'exit {code}'
            elif output is None:
                error = 'stdout was not JSON'
        for grader in graders:
            outcome, detail = grade(grader, case, output, error, bool(argv), human, vocabulary, args.timeout)
            result = {'case_id': case['id'], 'grader_id': grader['id'], 'outcome': outcome, 'detail': detail}
            results.append(result)
            by_case.setdefault(case['id'], []).append(counts_as(result, grader))
    outcomes = {c['id']: case_outcome(by_case.get(c['id'], [])) for c in cases}
    metrics = {}
    for slice_id in [vs.ALL] + list(suite.slices):
        members = [outcomes[c['id']] for c in suite.slice_cases(slice_id, cases)]
        n = sum(o != 'abstain' for o in members)
        passes = members.count('pass')
        metrics[slice_id] = {'value': round(passes / n, 4) if n else None, 'n': n,
                             'interval': wilson(passes, n), 'passes': passes}
    gate_results = []
    for gate in gates:
        metric = metrics[gate['slice']]
        if 'suite_version' in gate and str(gate['suite_version']) != str(suite.version):
            status, note = 'open', f"pinned to suite version {gate['suite_version']}"
        elif metric['n'] < gate['min_n']:
            status, note = 'insufficient_n', f"n {metric['n']} is below min_n {gate['min_n']}"
        else:
            status = 'passed' if metric['value'] >= gate['threshold'] else 'failed'
            note = ''
        gate_results.append(dict(gate, status=status, value=metric['value'], n=metric['n'], note=note))
    run = {'id': f"{suite.id}-{started:%Y%m%dT%H%M%SZ}", 'suite_id': suite.id, 'suite_version': suite.version,
           'target_version': args.target_version, 'started_at': started.isoformat().replace('+00:00', 'Z'),
           'split': args.split, 'tuning': bool(args.tune), 'results': results, 'metrics': metrics,
           'gates': gate_results}
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


def report(suite, run, outcomes, holdout_runs):
    abstained = sum(o == 'abstain' for o in outcomes.values())
    lines = [f"# Run {run['id']}", '',
             f"- Suite `{suite.id}` version {suite.version}; target version `{run['target_version']}`",
             f"- Split `{run['split']}`; tuning run: {'yes' if run['tuning'] else 'no'}; started {run['started_at']}",
             f'- Cases run: {len(outcomes)} ({abstained} abstained, left out of n); holdout runs logged for this suite: {holdout_runs}',
             '', '## Metrics (pass_rate)', '',
             '| Slice | n | Passes | Value | 95% interval (Wilson) |', '|---|---|---|---|---|']
    for slice_id, m in run['metrics'].items():
        interval = 'n/a' if m['interval'] is None else f"{fmt(m['interval'][0])} to {fmt(m['interval'][1])}"
        lines.append(f"| {slice_id} | {m['n']} | {m['passes']} | {fmt(m['value'])} | {interval} |")
    lines += ['', '## Gates', '']
    if run['gates']:
        lines += ['| Gate | Slice | Threshold | min_n | n | Value | Status | Action | Owner |',
                  '|---|---|---|---|---|---|---|---|---|']
        for g in run['gates']:
            status = f"`{g['status']}`" + (f" ({g['note']})" if g['note'] else '')
            lines.append(f"| {g['id']} | {g['slice']} | {g['threshold']} | {g['min_n']} | {g['n']} | {fmt(g['value'])} "
                         f"| {status} | {g['action']} | {g['owner']} |")
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
    parser.add_argument('--target-version', default='unversioned', help='recorded in run.json')
    parser.add_argument('--split', choices=('dev', 'holdout', 'all'), default='dev', help='cases to run (default dev)')
    vs.add_input_arguments(parser)
    parser.add_argument('--human-results', metavar='FILE', help='recorded human outcomes: [{case_id, grader_id, outcome, detail}]')
    parser.add_argument('--traffic', metavar='FILE', help='live tag counts for the drift check')
    parser.add_argument('--max-drift', type=float, default=0.2, help='largest allowed tag distance (default 0.2)')
    parser.add_argument('--out', metavar='DIR', help='output folder (default eval-runs/<run id>)')
    parser.add_argument('--timeout', type=float, default=60, help='seconds per target or grader call (default 60)')
    parser.add_argument('--strict', action='store_true', help='exit 1 when a gate is insufficient_n')
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
    failed = statuses['failed'] or run.get('drift', {}).get('exceeded') or (args.strict and statuses['insufficient_n'])
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
