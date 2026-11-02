#!/usr/bin/env python3
"""Generate an evaluation-system suite for a question set: standard, invariance and negation cases, balanced.

Usage: make_eval_cases.py QUESTION_SET --seeds FILE [--holdout-percent N] [--permutations N] [--out FILE]

Seeds are a YAML list (or a `cases:` list) of {id, question, state, expected, basis, added_because}
with optional source, split and tags. Every generated case carries its seed's `basis` and is tagged
with its question id; option-order permutations are `kind: invariance` and boundary-pair negations
are `kind: negation`, each with `variant_of`. Splits are stratified by expected value, and variants
follow their base case. Errors go to stderr; exit 1 on any error (nothing written), 2 when an input
cannot be read. Validate the output with evaluation-system's validate_suite.py.
Rule semantics: references/model.md. Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

import yaml

SOURCES = ('production', 'synthetic', 'adversarial', 'regression')
BASES = ('owner', 'judgment', 'convention', 'agent')
SEED_FIELDS = ('id', 'question', 'state', 'expected', 'basis', 'added_because', 'source', 'split', 'tags')


class InputError(Exception):
    """An input file is missing or cannot be parsed; the caller exits 2."""


def load(path, what):
    try:
        return yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    except OSError as exc:
        raise InputError(f'{path}: cannot read {what}: {exc.strerror or exc}')
    except yaml.YAMLError as exc:
        raise InputError(f'{path}: {what} is not valid YAML: {" ".join(str(exc).split())}')


def orders(keys, count):
    """Up to `count` option orders other than `keys`: reversed first, then left rotations."""
    candidates = [list(reversed(keys))] + [keys[i:] + keys[:i] for i in range(1, len(keys))]
    out = []
    for order in candidates:
        if order != keys and order not in out:
            out.append(order)
    return out[:count]


def partner(question_set, qid):
    for d in question_set.get('decisions') or []:
        if d.get('mode') == 'compare':
            if qid in (d.get('inputs') or []):
                return d.get('rival')
            if d.get('rival') == qid:
                return (d.get('inputs') or [None])[0]
    return None


def stratified_split(cases, key, percent):
    """Assign holdout to about `percent` of each stratum, deterministically by case id."""
    strata = {}
    for case in cases:
        strata.setdefault(key(case), []).append(case)
    for members in strata.values():
        members.sort(key=lambda c: c['id'])
        for i, case in enumerate(members):
            if 'split' not in case:
                case['split'] = 'holdout' if (i + 1) * percent // 100 > i * percent // 100 else 'dev'


def make_suite(question_set, seeds, holdout_percent=30, permutations=2):
    """Return (suite or None, errors)."""
    errors = []
    questions = {q['id']: q for q in question_set.get('questions') or [] if isinstance(q, dict) and 'id' in q}
    standard, ids = [], set()
    for i, seed in enumerate(seeds):
        where = f"seed {seed.get('id', i) if isinstance(seed, dict) else i}"
        if not isinstance(seed, dict):
            errors.append(f'{where}: not a mapping.')
            continue
        unknown = sorted(set(seed) - set(SEED_FIELDS))
        if unknown:
            errors.append(f"{where}: unknown field(s) {', '.join(unknown)}; use {', '.join(SEED_FIELDS)}.")
        missing = [f for f in ('id', 'question', 'state', 'expected', 'basis', 'added_because') if seed.get(f) is None]
        if missing:
            errors.append(f"{where}: missing {', '.join(missing)}; every case needs its basis and its evidence.")
            continue
        if seed['basis'] not in BASES:
            errors.append(f"{where}: basis {seed['basis']!r} is not one of {', '.join(BASES)}.")
        if seed.get('source', 'production') not in SOURCES:
            errors.append(f"{where}: source {seed['source']!r} is not one of {', '.join(SOURCES)}.")
        if seed['id'] in ids:
            errors.append(f'{where}: the id repeats.')
        ids.add(seed['id'])
        q = questions.get(seed['question'])
        if q is None:
            errors.append(f"{where}: question {seed['question']!r} is not in the question set.")
            continue
        exp = seed['expected']
        if q['kind'] == 'choice' and exp not in (q.get('options') or {}):
            errors.append(f"{where}: expected {exp!r} is not an option of {q['id']}.")
            continue
        if q['kind'] == 'score' and exp not in range(1, len(q.get('levels') or []) + 1):
            errors.append(f"{where}: expected {exp!r} is not a level number of {q['id']}.")
            continue
        if q['kind'] == 'proposition' and not isinstance(exp, bool):
            errors.append(f"{where}: a proposition expects true or false, not {exp!r}.")
            continue
        case = {'id': str(seed['id']),
                'input': {'question_id': q['id'], 'state': seed['state']},
                'expected': {'answer': exp} if q['kind'] == 'proposition' else {'value': exp},
                'tags': [q['id']] + [t for t in seed.get('tags') or [] if t != q['id']],
                'source': seed.get('source', 'production'),
                'basis': seed['basis'],
                'kind': 'standard',
                'added_because': str(seed['added_because']),
                'graders': ['answer-match' if q['kind'] == 'proposition' else 'value-match']}
        if seed.get('split') in ('dev', 'holdout'):
            case['split'] = seed['split']
        standard.append(case)
    if errors:
        return None, errors
    stratified_split(standard, lambda c: (c['input']['question_id'], str(c['expected'])), holdout_percent)

    variants = []
    for case in standard:
        q = questions[case['input']['question_id']]
        base = {k: case[k] for k in ('source', 'basis', 'split', 'graders')}
        base.update(source='adversarial', variant_of=case['id'])
        if q['kind'] == 'choice':
            for n, order in enumerate(orders(list(q['options']), permutations), 1):
                variants.append(dict(base, id=f"{case['id']}-perm{n}", kind='invariance',
                                     input=dict(case['input'], options=order), expected=case['expected'],
                                     tags=list(case['tags']),
                                     added_because=f"option order of {case['id']} permuted to {', '.join(order)}"))
        elif q['kind'] == 'proposition':
            variants.append(dict(base, id=f"{case['id']}-perm1", kind='invariance',
                                 input=dict(case['input'], options=['no', 'yes']), expected=case['expected'],
                                 tags=list(case['tags']),
                                 added_because=f"answer options of {case['id']} presented as no, yes"))
            rival = partner(question_set, q['id'])
            if question_set.get('shape') == 'boundary-pair' and rival in questions:
                variants.append(dict(base, id=f"{case['id']}-neg", kind='negation',
                                     input={'question_id': rival, 'state': case['input']['state']},
                                     expected={'answer': not case['expected']['answer']},
                                     tags=list(case['tags']),
                                     added_because=f"negation of {case['id']}: the rival {rival} asked, answer flipped"))
    cases = standard + variants
    clash = sorted(i for i, n in Counter(c['id'] for c in cases).items() if n > 1)
    if clash:
        return None, [f"generated case id(s) {', '.join(clash)} collide with seed ids; rename the seeds."]
    for qid, q in questions.items():
        if q['kind'] != 'proposition':
            continue
        answers = Counter(c['expected']['answer'] for c in cases if qid in c['tags'] and c['kind'] != 'invariance')
        if not answers:
            continue
        if answers[True] != answers[False]:
            errors.append(f"proposition {qid} has {answers[True]} true and {answers[False]} false cases; "
                          'a proposition suite is balanced and scored in both directions. Add seeds for the short side.')
    if errors:
        return None, errors
    order = {c['id']: i for i, c in enumerate(standard)}
    cases.sort(key=lambda c: (order[c.get('variant_of', c['id'])], c.get('variant_of') is not None, c['id']))
    for case in cases:
        if case['kind'] == 'standard':
            del case['kind']
    suite = {
        'id': f"{question_set.get('id')}-cases",
        'version': question_set.get('version', 1),
        'target': str(question_set.get('id')),
        'target_spec': [' '.join(q['instructions'].split()) for q in questions.values()],
        'graders': [{'id': 'value-match', 'kind': 'exact', 'config': {'field': 'value'}},
                    {'id': 'answer-match', 'kind': 'exact', 'config': {'field': 'answer'}}],
        'slices': sorted({c['tags'][0] for c in cases}),
        'cases': cases,
    }
    return suite, []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('question_set', help='the question set YAML')
    parser.add_argument('--seeds', required=True, help='seed cases YAML')
    parser.add_argument('--holdout-percent', type=int, default=30, help='share of each stratum in holdout (default 30)')
    parser.add_argument('--permutations', type=int, default=2, help='option orders per choice case (default 2)')
    parser.add_argument('--out', help='write the suite here (default stdout)')
    args = parser.parse_args(argv)
    try:
        question_set = load(args.question_set, 'question set')
        seeds = load(args.seeds, 'seeds')
    except InputError as exc:
        print(f'ERROR input: {exc}', file=sys.stderr)
        return 2
    if isinstance(seeds, dict):
        seeds = seeds.get('cases')
    if not isinstance(question_set, dict) or not isinstance(seeds, list):
        print('ERROR input: need a question set mapping and a list of seed cases', file=sys.stderr)
        return 2
    suite, errors = make_suite(question_set, seeds, args.holdout_percent, args.permutations)
    for error in errors:
        print(f'ERROR {error}', file=sys.stderr)
    if suite is None:
        print(f'refused: {len(errors)} error(s); nothing written.', file=sys.stderr)
        return 1
    header = (f"# Generated by make_eval_cases.py from {Path(args.question_set).name} and {Path(args.seeds).name}; "
              'regenerate rather than edit.\n')
    text = header + yaml.safe_dump(suite, sort_keys=False, allow_unicode=True, width=110)
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
