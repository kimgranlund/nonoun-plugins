#!/usr/bin/env python3
"""Compile a question set's options from a knowledge-organization-system scheme.

Usage: compile_questions.py VOCABULARY --template FILE --shape single-choice|retrieve-then-choose
                            [--scheme ID] [--concepts ID,...] [--max-options N] [--allow-none]
                            [--run RUN_JSON] [--out FILE]

The template is a question set; its first question gets one option per selected active concept,
keyed by concept id, with `concept_id`, `definition` and `excludes` copied verbatim. Contrast text is
never synthesized. Findings go to stderr as SEVERITY RULE SUBJECT FIELD: problem. Fix: fix.
The question set goes to --out or stdout, and nothing is written when there is an error.
Exit 0 on success (warnings allowed), 1 on errors, 2 when an input cannot be read.
Rule semantics: references/model.md. Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import copy
import json
import re
import sys
from collections import namedtuple
from pathlib import Path

import yaml

SHAPES = ('single-choice', 'retrieve-then-choose')
NONE_KEY = 'none'
ERROR_RULES = ('missing-definition', 'too-many-options', 'none-without-examples', 'duplicate-option',
               'unknown-selection')
WARNING_RULES = ('excludes-outside-options', 'unaddressed-confusion')
RULE_ORDER = {rule: i for i, rule in enumerate(ERROR_RULES + WARNING_RULES)}
CONFUSION = re.compile(r'^expected (.+), got (.+)$')


class Finding(namedtuple('Finding', 'severity rule subject field problem fix')):
    def line(self):
        return f'{self.severity} {self.rule} {self.subject} {self.field}: {self.problem} Fix: {self.fix}'

    def key(self):
        return (self.severity != 'ERROR', RULE_ORDER[self.rule], self.subject, self.field, self.problem)


class InputError(Exception):
    """An input file is missing or cannot be parsed; the caller exits 2."""


def load(path, what, parse=yaml.safe_load):
    try:
        return parse(Path(path).read_text(encoding='utf-8'))
    except OSError as exc:
        raise InputError(f'{path}: cannot read {what}: {exc.strerror or exc}')
    except (yaml.YAMLError, ValueError) as exc:
        raise InputError(f'{path}: {what} cannot be parsed: {" ".join(str(exc).split())}')


def label(value):
    """An option key from a compared value: a string, or a mapping's `value` or `label`."""
    if isinstance(value, dict):
        value = value.get('value', value.get('label'))
    return value if isinstance(value, str) else None


def confusions(run):
    """Sorted option-key pairs from an evaluation-system run's exact-grader failures ("expected X, got Y")."""
    pairs = set()
    for result in run.get('results') or [] if isinstance(run, dict) else []:
        detail = result.get('detail') if isinstance(result, dict) else None
        m = CONFUSION.match(detail) if result.get('outcome') == 'fail' and isinstance(detail, str) else None
        if not m:
            continue
        try:
            a, b = label(json.loads(m.group(1))), label(json.loads(m.group(2)))
        except ValueError:
            continue
        if a and b and a != b:
            pairs.add(tuple(sorted((a, b))))
    return sorted(pairs)


def compile_set(vocabulary, template, shape, scheme=None, selection=None, max_options=12, allow_none=False, run=None):
    """Return (question_set or None, findings)."""
    findings = []
    subject = str(template.get('id', 'template')) if isinstance(template, dict) else 'template'

    def add(severity, rule, field, problem, fix):
        findings.append(Finding(severity, rule, subject, field, problem, fix))

    if not isinstance(vocabulary, dict) or not isinstance(vocabulary.get('concepts'), list):
        raise InputError('the vocabulary is not a knowledge-organization-system vocabulary (no `concepts:` list)')
    if not isinstance(template, dict) or not isinstance(template.get('questions'), list) or not template['questions'] \
            or not isinstance(template['questions'][0], dict):
        raise InputError('the template is not a question set with at least one question')
    schemes = [s.get('id') for s in vocabulary.get('schemes') or [] if isinstance(s, dict)]
    concepts = [c for c in vocabulary['concepts'] if isinstance(c, dict)]
    scheme = scheme or (schemes[0] if len(schemes) == 1 else None)
    if scheme not in schemes:
        add('ERROR', 'unknown-selection', 'scheme', f'scheme {scheme!r} is not declared in the vocabulary.',
            f"pass --scheme with one of: {', '.join(str(s) for s in schemes) or '(none declared)'}.")
        return None, findings
    by_id = {}
    for c in concepts:
        by_id.setdefault(c.get('id'), c)
    if selection:
        chosen = []
        for cid in selection:
            c = by_id.get(cid)
            if c is None or c.get('scheme') != scheme:
                add('ERROR', 'unknown-selection', f'concepts.{cid}', f"'{cid}' is not a concept in scheme {scheme}.",
                    'select concept ids from that scheme, or add the concept through knowledge-organization-system.')
            elif c.get('deprecated'):
                add('ERROR', 'unknown-selection', f'concepts.{cid}', f"'{cid}' is deprecated.",
                    f"select its replacement {c.get('replacedBy')!r} instead.")
            else:
                chosen.append(c)
    else:
        chosen = [c for c in concepts if c.get('scheme') == scheme and not c.get('deprecated')]

    question = copy.deepcopy(template['questions'][0])
    hand = question.get('options') if isinstance(question.get('options'), dict) else {}
    options, seen = {}, set()
    for c in chosen:
        cid = c.get('id')
        if cid in seen:
            add('ERROR', 'duplicate-option', f'options.{cid}', f"option key '{cid}' appears twice in the scheme.",
                'give each concept a unique id in the vocabulary (validate_kos.py reports it as schema).')
            continue
        seen.add(cid)
        definition = c.get('definition')
        if not isinstance(definition, str) or not definition.strip():
            add('ERROR', 'missing-definition', f'options.{cid}', f"concept '{cid}' has no definition.",
                'write the definition in the vocabulary first (knowledge-organization-system); '
                'the compiler never invents option text.')
            continue
        option = {'concept_id': cid, 'definition': definition.strip()}
        if c.get('excludes'):
            option['excludes'] = copy.deepcopy(c['excludes'])
        examples = (hand.get(cid) or {}).get('examples') if isinstance(hand.get(cid), dict) else None
        if examples:
            option['examples'] = list(examples)
        options[cid] = option
    if allow_none:
        if NONE_KEY in options:
            if NONE_KEY in hand:
                add('ERROR', 'duplicate-option', f'options.{NONE_KEY}',
                    f"option key '{NONE_KEY}' comes from both the vocabulary and the template.",
                    'keep one general option.')
        elif isinstance(hand.get(NONE_KEY), dict):
            options[NONE_KEY] = copy.deepcopy(hand[NONE_KEY])
        if not (options.get(NONE_KEY) or {}).get('examples'):
            add('ERROR', 'none-without-examples', f'options.{NONE_KEY}',
                f"the scheme allows none, but there is no '{NONE_KEY}' option with concrete examples.",
                f"add a '{NONE_KEY}' option with a definition and examples to the template's first question.")
    count = len(options)
    if shape == 'single-choice' and count > max_options:
        add('ERROR', 'too-many-options', 'options',
            f'single-choice offers {count} options; the maximum is {max_options}.',
            'use retrieve-then-choose or hierarchical-walk, or narrow --concepts to what the domain uses.')
    for key, option in options.items():
        for ex in option.get('excludes') or []:
            neighbor = ex.get('neighbor') if isinstance(ex, dict) else None
            if neighbor not in options:
                add('WARNING', 'excludes-outside-options', f'options.{key}.excludes',
                    f"neighbor '{neighbor}' is not in the option set, so this contrast points at nothing the model sees.",
                    'add the neighbor to --concepts if the domain uses it, or accept the dangling contrast knowingly.')
    if run is not None:
        for a, b in confusions(run):
            if a in options and b in options and not any(
                    isinstance(ex, dict) and ex.get('neighbor') == other
                    for key, other in ((a, b), (b, a)) for ex in options[key].get('excludes') or []):
                add('WARNING', 'unaddressed-confusion', f'options.{a}',
                    f"the last evaluation run confused '{a}' and '{b}', and neither option has an excludes entry naming the other.",
                    'author an excludes entry in the vocabulary (knowledge-organization-system), recompile and re-run.')
    if any(f.severity == 'ERROR' for f in findings):
        return None, findings
    question['options'] = options
    question['kind'] = 'choice'
    question['scheme'] = scheme
    result = copy.deepcopy(template)
    result['shape'] = shape
    result['questions'] = [question] + result['questions'][1:]
    return result, findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('vocabulary', help='knowledge-organization-system vocabulary YAML')
    parser.add_argument('--template', required=True, help='a question set whose first question receives the options')
    parser.add_argument('--shape', required=True, choices=SHAPES, help='other shapes are written by hand (references/shapes.md)')
    parser.add_argument('--scheme', help='the KOS scheme id (default: the only scheme)')
    parser.add_argument('--concepts', help='comma-separated concept ids (default: every active concept in the scheme)')
    parser.add_argument('--max-options', type=int, default=12, help='largest single-choice option count (default 12)')
    parser.add_argument('--allow-none', action='store_true', help="require a 'none' option with examples")
    parser.add_argument('--run', help="an evaluation-system run.json; confused option pairs without excludes are warned")
    parser.add_argument('--out', help='write the question set here (default stdout)')
    args = parser.parse_args(argv)
    try:
        vocabulary = load(args.vocabulary, 'vocabulary')
        template = load(args.template, 'template')
        run = load(args.run, 'run', json.loads) if args.run else None
        selection = [c.strip() for c in args.concepts.split(',') if c.strip()] if args.concepts else None
        result, findings = compile_set(vocabulary, template, args.shape, args.scheme, selection,
                                       args.max_options, args.allow_none, run)
    except InputError as exc:
        print(f'ERROR input: {exc}', file=sys.stderr)
        return 2
    for finding in sorted(set(findings), key=Finding.key):
        print(finding.line(), file=sys.stderr)
    if result is None:
        print(f'refused: {sum(f.severity == "ERROR" for f in findings)} error(s); nothing written.', file=sys.stderr)
        return 1
    text = yaml.safe_dump(result, sort_keys=False, allow_unicode=True, width=100)
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
