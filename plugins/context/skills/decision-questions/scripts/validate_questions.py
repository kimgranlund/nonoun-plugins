#!/usr/bin/env python3
"""Validate decision-questions question sets: spine, decision modes, model pin, role gates and phrasing.

Usage: validate_questions.py QUESTION_SET [QUESTION_SET ...] [--gates FILE] [--vocabulary FILE]
                             [--rules FILE] [--lint FILE] [--strict]

Each finding is one line: SEVERITY RULE SUBJECT FIELD: problem. Fix: fix.
Exit 0 when there are no errors (warnings allowed unless --strict), 1 on errors,
2 when an input file cannot be read. Phrasing is delegated to controlled-natural-language's
lint_cnl.py with the decision-question rules file, as a subprocess. Rule semantics: references/model.md.
Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from collections import namedtuple
from pathlib import Path

import yaml

CNL = Path(__file__).resolve().parents[2] / 'controlled-natural-language'
DEFAULT_RULES = CNL / 'templates' / 'decision-question.rules.yaml'
DEFAULT_LINT = CNL / 'scripts' / 'lint_cnl.py'

SET_FIELDS = ('id', 'version', 'model', 'shape', 'questions', 'decisions', 'role', 'gate_ids')
SET_REQUIRED = ('id', 'version', 'shape', 'questions', 'decisions', 'role')
QUESTION_FIELDS = ('id', 'kind', 'instructions', 'options', 'levels', 'scheme', 'version')
OPTION_FIELDS = ('concept_id', 'definition', 'excludes', 'examples')
EXCLUDES_FIELDS = ('neighbor', 'statement')
LEVEL_FIELDS = ('description', 'examples')
DECISION_FIELDS = ('id', 'mode', 'inputs', 'bands', 'margin', 'rival', 'assemble', 'outcome')
SHAPES = ('single-choice', 'retrieve-then-choose', 'hierarchical-walk', 'per-value-propositions',
          'boundary-pair', 'verify-against-rival')
KINDS = ('choice', 'score', 'proposition')
MODES = ('threshold', 'compare')
OUTCOMES = ('act', 'review', 'defer', 'flag')
ROLES = ('checker', 'suggester', 'voter')
MOVING_ALIASES = ('latest', 'default', 'stable', 'current')

ERROR_RULES = ('schema', 'threshold-on-proposition', 'compare-incomplete', 'unpinned-model', 'ungated-role',
               'missing-question', 'missing-assemble', 'cnl')
WARNING_RULES = ('peer-absent',)
RULE_ORDER = {rule: i for i, rule in enumerate(ERROR_RULES + WARNING_RULES)}
LINT_LINE = re.compile(r'^(ERROR|WARNING) (\S+) (.+?):(\d+): (.*?) Fix: (.*)$')


class Finding(namedtuple('Finding', 'severity rule subject field problem fix')):
    def line(self):
        return f'{self.severity} {self.rule} {self.subject} {self.field}: {self.problem} Fix: {self.fix}'

    def key(self):
        return (self.severity != 'ERROR', RULE_ORDER[self.rule], self.subject, self.field, self.problem)


class InputError(Exception):
    """An input file is missing or cannot be parsed; the caller exits 2."""


def load_yaml(path, what):
    try:
        return yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    except OSError as exc:
        raise InputError(f'{path}: cannot read {what}: {exc.strerror or exc}')
    except yaml.YAMLError as exc:
        raise InputError(f'{path}: {what} is not valid YAML: {" ".join(str(exc).split())}')


def load_gates(path):
    data = load_yaml(path, 'gate registry')
    gates = data.get('gates') if isinstance(data, dict) else None
    if not isinstance(gates, list):
        raise InputError(f'{path}: not an evaluation-system gate registry (no `gates:` list)')
    return {g['id']: g for g in gates if isinstance(g, dict) and isinstance(g.get('id'), str)}


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_unpinned(model):
    if not isinstance(model, (str, int)) or isinstance(model, bool) or not str(model).strip():
        return True
    text = str(model).strip().casefold()
    return text in MOVING_ALIASES or text.endswith('-latest') or '*' in text


class Checker:
    def __init__(self, path, data):
        self.path, self.data, self.findings = path, data, []
        self.subject = str(data.get('id')) if isinstance(data, dict) and data.get('id') else Path(path).name

    def add(self, severity, rule, field, problem, fix, subject=None):
        self.findings.append(Finding(severity, rule, subject or self.subject, field, problem, fix))

    def schema(self, field, problem, fix='correct the shape against references/model.md.'):
        self.add('ERROR', 'schema', field, problem, fix)

    def unknown_keys(self, mapping, allowed, where):
        for key in sorted(set(mapping) - set(allowed), key=str):
            self.schema(f'{where}.{key}', f'`{key}` is not a field here.', f"use one of: {', '.join(allowed)}.")

    # ------------------------------------------------------------ questions

    def check_questions(self):
        questions = {}
        raw = self.data.get('questions')
        if not isinstance(raw, list):
            self.schema('questions', '`questions` is not a list.')
            return questions
        for i, q in enumerate(raw):
            where = f'questions[{i}]'
            if not isinstance(q, dict):
                self.schema(where, 'a question is not a mapping.')
                continue
            self.unknown_keys(q, QUESTION_FIELDS, where)
            qid = q.get('id')
            if not isinstance(qid, str) or not qid:
                self.schema(f'{where}.id', 'a question has no id.')
                continue
            where = f'questions.{qid}'
            if qid in questions:
                self.schema(where, f"question id '{qid}' repeats.", 'give each question its own id.')
                continue
            questions[qid] = q
            if q.get('kind') not in KINDS:
                self.schema(f'{where}.kind', f"kind {q.get('kind')!r} is not one of {', '.join(KINDS)}.")
            if not isinstance(q.get('instructions'), str) or not q['instructions'].strip():
                self.schema(f'{where}.instructions', 'the question has no instructions.')
            if q.get('kind') == 'choice':
                self.check_options(q.get('options'), where)
            elif q.get('options') is not None:
                self.schema(f'{where}.options', f"a {q.get('kind')} question has no options.", 'remove `options`.')
            if q.get('kind') == 'score':
                self.check_levels(q.get('levels'), where)
            elif q.get('levels') is not None:
                self.schema(f'{where}.levels', f"a {q.get('kind')} question has no levels.", 'remove `levels`.')
        return questions

    def check_options(self, options, where):
        if not isinstance(options, dict) or not options:
            self.schema(f'{where}.options', 'a choice question needs an `options` mapping.')
            return
        for key, opt in options.items():
            at = f'{where}.options.{key}'
            if not isinstance(opt, dict):
                self.schema(at, 'an option is not a mapping.')
                continue
            self.unknown_keys(opt, OPTION_FIELDS, at)
            if not isinstance(opt.get('definition'), str) or not opt['definition'].strip():
                self.schema(f'{at}.definition', 'the option has no definition.')
            for j, ex in enumerate(opt.get('excludes') or []):
                if not isinstance(ex, dict) or set(ex) - set(EXCLUDES_FIELDS) or \
                        not all(isinstance(ex.get(f), str) and ex[f].strip() for f in EXCLUDES_FIELDS):
                    self.schema(f'{at}.excludes[{j}]', 'an excludes entry is not {neighbor, statement}.')
            if opt.get('examples') is not None and not isinstance(opt['examples'], list):
                self.schema(f'{at}.examples', '`examples` is not a list.')

    def check_levels(self, levels, where):
        if not isinstance(levels, list) or len(levels) < 2:
            self.schema(f'{where}.levels', 'a score question needs at least two levels, lowest first.')
            return
        for i, level in enumerate(levels):
            if not isinstance(level, dict) or not isinstance(level.get('description'), str):
                self.schema(f'{where}.levels[{i}]', 'a level is not {description, examples?}.')
            else:
                self.unknown_keys(level, LEVEL_FIELDS, f'{where}.levels[{i}]')

    # ------------------------------------------------------------ decisions

    def check_decisions(self, questions):
        raw = self.data.get('decisions')
        if not isinstance(raw, list):
            self.schema('decisions', '`decisions` is not a list.')
            return []
        seen, read = set(), []
        for i, d in enumerate(raw):
            if not isinstance(d, dict):
                self.schema(f'decisions[{i}]', 'a decision is not a mapping.')
                continue
            did = d.get('id') if isinstance(d.get('id'), str) else f'decisions[{i}]'
            where = f'decisions.{did}'
            self.unknown_keys(d, DECISION_FIELDS, where)
            if did in seen:
                self.schema(where, f"decision id '{did}' repeats.", 'give each decision its own id.')
            seen.add(did)
            inputs = d.get('inputs')
            if not isinstance(inputs, list) or not inputs or not all(isinstance(x, str) for x in inputs):
                self.schema(f'{where}.inputs', '`inputs` is not a non-empty list of question ids.')
                inputs = []
            if d.get('outcome') not in OUTCOMES:
                self.schema(f'{where}.outcome', f"outcome {d.get('outcome')!r} is not one of {', '.join(OUTCOMES)}.")
            names = list(inputs) + ([d['rival']] if isinstance(d.get('rival'), str) else [])
            for qid in names:
                if qid in questions:
                    read.append(qid)
                else:
                    field = 'rival' if qid == d.get('rival') and qid not in inputs else 'inputs'
                    self.add('ERROR', 'missing-question', f'{where}.{field}',
                             f"names question '{qid}', which the set does not define.",
                             'correct the id or add the question.')
            if len(inputs) > 1 and not d.get('assemble'):
                self.add('ERROR', 'missing-assemble', f'{where}.assemble',
                         f"combines {len(inputs)} isolated answers ({', '.join(inputs)}) into a joint label with no "
                         '`assemble` validator; questions in one request cannot see each other.',
                         'name the code validator that enforces the label grammar and refuses impossible combinations.')
            mode = d.get('mode')
            if mode == 'threshold':
                self.check_threshold(d, where, inputs, questions)
            elif mode == 'compare':
                self.check_compare(d, where, inputs, questions)
            else:
                self.schema(f'{where}.mode', f"mode {mode!r} is not one of {', '.join(MODES)}.")
        return read

    def check_threshold(self, d, where, inputs, questions):
        props = [q for q in inputs if questions.get(q, {}).get('kind') == 'proposition']
        if props:
            self.add('ERROR', 'threshold-on-proposition', f'{where}.mode',
                     f"thresholds proposition {', '.join(props)}; raw proposition values are poorly calibrated.",
                     'use compare mode with a rival proposition and a margin tuned on dev.')
        bands = d.get('bands')
        if not isinstance(bands, dict) or set(bands) != {'act', 'review'} or \
                not all(is_number(v) and 0 <= v <= 1 for v in bands.values()):
            self.schema(f'{where}.bands', 'threshold mode needs `bands: {act, review}`, each between 0 and 1.')
        elif bands['review'] > bands['act']:
            self.schema(f'{where}.bands', 'the review band is above the act band.', 'set review at or below act.')

    def check_compare(self, d, where, inputs, questions):
        missing = [f for f in ('rival', 'margin') if d.get(f) is None]
        if missing:
            self.add('ERROR', 'compare-incomplete', f'{where}.{missing[0]}',
                     f"compare mode has no {' and no '.join('`%s`' % f for f in missing)}.",
                     'name the rival proposition and a minimum margin tuned on dev; near-ties must never fire.')
        elif not is_number(d['margin']) or not 0 <= d['margin'] <= 1:
            self.schema(f'{where}.margin', '`margin` is not a number between 0 and 1.')
        for qid in inputs + ([d['rival']] if isinstance(d.get('rival'), str) else []):
            kind = questions.get(qid, {}).get('kind')
            if kind and kind != 'proposition':
                self.schema(f'{where}.mode', f"compare mode reads {kind} question '{qid}'.",
                            'compare propositions; choices and scores use threshold bands.')
        if len(inputs) > 1 and not missing:
            self.schema(f'{where}.inputs', 'compare mode reads one input against its rival.')

    # ------------------------------------------------------------ set-level

    def check_set(self, gates, gates_given):
        if not isinstance(self.data, dict):
            self.schema('(file)', 'the question set is not a YAML mapping.')
            return {}
        self.unknown_keys(self.data, SET_FIELDS, 'set')
        for field in SET_REQUIRED:
            if field not in self.data:
                self.schema(field, f'`{field}` is missing.')
        if 'shape' in self.data and self.data['shape'] not in SHAPES:
            self.schema('shape', f"shape {self.data['shape']!r} is not one of {', '.join(SHAPES)}.")
        if 'role' in self.data and self.data['role'] not in ROLES:
            self.schema('role', f"role {self.data['role']!r} is not one of {', '.join(ROLES)}.")
        model = self.data.get('model')
        if is_unpinned(model):
            self.add('ERROR', 'unpinned-model', 'model',
                     'no pinned model version.' if model is None or not str(model).strip()
                     else f"model {model!r} is an alias that moves, not a pinned version.",
                     'pin the exact version the adapter reports; a version change re-asks and re-runs the gates.')
        questions = self.check_questions()
        read = self.check_decisions(questions)
        self.check_role(read, gates, gates_given)
        return questions

    def check_role(self, read, gates, gates_given):
        role = self.data.get('role')
        if role not in ('suggester', 'voter'):
            return
        gate_ids = self.data.get('gate_ids') or []
        if not isinstance(gate_ids, list):
            self.schema('gate_ids', '`gate_ids` is not a list.')
            gate_ids = []
        model = str(self.data.get('model'))
        pin = "the set's model" if is_unpinned(self.data.get('model')) else model
        ungated = []
        for qid in sorted(set(read)):
            ok = any(gid in gates and gates[gid].get('question_id') == qid and gates[gid].get('status') == 'passed'
                     and str(gates[gid].get('pinned_target_version')) == model for gid in gate_ids)
            if not ok:
                ungated.append(qid)
        if ungated:
            why = '' if gates_given else ' (no gates.yaml was given)'
            self.add('ERROR', 'ungated-role', 'role',
                     f"role {role} needs a passed gate per question pinned to {pin}; ungated: "
                     f"{', '.join(ungated)}{why}.",
                     'record the passed per-question gate (question_id, pinned_target_version) in gate_ids, '
                     'or keep the role at checker.')

    # ------------------------------------------------------------ phrasing

    def governed(self, questions):
        """Render the governed text as a decision-question doc: (markdown, {line: (field, text)})."""
        lines, where = ['---', 'cnl: decision-question', '---', ''], {}

        def emit(field, text, row=False):
            text = ' '.join(str(text).split())
            where[len(lines) + 1] = (field, text)
            lines.extend([f'| {text} |' if row else text, ''])

        for qid, q in questions.items():
            if isinstance(q.get('instructions'), str):
                emit(f'questions.{qid}.instructions', q['instructions'])
            for i, level in enumerate(q.get('levels') or [], 1):
                if isinstance(level, dict) and isinstance(level.get('description'), str):
                    emit(f'questions.{qid}.levels[{i - 1}]', f"Level {i} means {level['description'].rstrip('.')}.")
            for key, opt in (q.get('options') or {}).items() if isinstance(q.get('options'), dict) else []:
                if not isinstance(opt, dict) or opt.get('concept_id'):
                    continue  # KOS text: governed in the vocabulary, copied verbatim
                if isinstance(opt.get('definition'), str):
                    emit(f'questions.{qid}.options.{key}.definition', opt['definition'], row=True)
                for j, ex in enumerate(opt.get('excludes') or []):
                    if isinstance(ex, dict) and isinstance(ex.get('statement'), str):
                        emit(f'questions.{qid}.options.{key}.excludes[{j}]', ex['statement'], row=True)
        return '\n'.join(lines), where

    def option_vocabulary(self, questions):
        concepts = []
        for q in questions.values():
            for key, opt in (q.get('options') or {}).items() if isinstance(q.get('options'), dict) else []:
                cid = opt.get('concept_id') if isinstance(opt, dict) and opt.get('concept_id') else key
                concepts.append({'id': str(cid), 'prefLabel': str(cid).replace('-', ' '),
                                 'definition': f'Option {cid} of question {q["id"]}.', 'scheme': 'options'})
        return {'schemes': [{'id': 'options', 'definition': 'Option keys of this question set.'}],
                'concepts': concepts}

    def lint(self, questions, rules, lint_script, vocabulary):
        doc, where = self.governed(questions)
        if len(where) == 0:
            return
        with tempfile.TemporaryDirectory() as tmp:
            doc_path = Path(tmp) / 'questions.md'
            doc_path.write_text(doc, encoding='utf-8')
            vocab = vocabulary
            if vocab is None:
                vocab = Path(tmp) / 'options.vocabulary.yaml'
                vocab.write_text(yaml.safe_dump(self.option_vocabulary(questions), sort_keys=False), encoding='utf-8')
            result = subprocess.run([sys.executable, '-B', str(lint_script), str(rules), str(vocab), str(doc_path)],
                                    capture_output=True, text=True)
        if result.returncode == 2:
            raise InputError(f'lint_cnl.py could not read its inputs: {result.stderr.strip() or result.stdout.strip()}')
        for raw in result.stdout.splitlines():
            m = LINT_LINE.match(raw)
            if not m:
                continue
            severity, rule, path, line, problem, fix = m.groups()
            if Path(path).name != 'questions.md':
                self.add(severity, 'cnl', 'rules', f'{rule} in {path}:{line}: {problem}', fix)
                continue
            field, text = where.get(int(line), ('(governed text)', ''))
            self.add(severity, 'cnl', field, f'{rule}: {problem} In: "{text.rstrip(".")}".', fix.rstrip('.') + '.')


def check(paths, gates_path=None, vocabulary=None, rules=None, lint_script=None):
    gates = load_gates(gates_path) if gates_path else {}
    rules = Path(rules) if rules else DEFAULT_RULES
    lint_script = Path(lint_script) if lint_script else DEFAULT_LINT
    if vocabulary and not Path(vocabulary).is_file():
        raise InputError(f'{vocabulary}: cannot read vocabulary')
    findings = []
    for path in paths:
        data = load_yaml(path, 'question set')
        checker = Checker(path, data)
        questions = checker.check_set(gates, bool(gates_path))
        if rules.is_file() and lint_script.is_file():
            checker.lint(questions, rules, lint_script, vocabulary)
        else:
            missing = rules if not rules.is_file() else lint_script
            checker.add('WARNING', 'peer-absent', 'phrasing',
                        f'{missing} is missing, so instructions and options were not linted.',
                        'install controlled-natural-language beside this skill or pass --rules and --lint; '
                        'until then check the decision-question rules by eye.')
        findings += checker.findings
    return sorted(set(findings), key=Finding.key)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('question_sets', nargs='+', metavar='QUESTION_SET')
    parser.add_argument('--gates', help='evaluation-system gate registry (gates.yaml)')
    parser.add_argument('--vocabulary', help='knowledge-organization-system vocabulary for option slots')
    parser.add_argument('--rules', help=f'CNL decision-question rules file (default {DEFAULT_RULES})')
    parser.add_argument('--lint', help=f'lint_cnl.py path (default {DEFAULT_LINT})')
    parser.add_argument('--strict', action='store_true', help='exit 1 on warnings too')
    args = parser.parse_args(argv)
    try:
        findings = check(args.question_sets, args.gates, args.vocabulary, args.rules, args.lint)
    except InputError as exc:
        print(f'ERROR input: {exc}', file=sys.stderr)
        return 2
    for finding in findings:
        print(finding.line())
    errors = sum(f.severity == 'ERROR' for f in findings)
    warnings = len(findings) - errors
    print(f'{len(args.question_sets)} question set(s): {errors} error(s), {warnings} warning(s)')
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main())
