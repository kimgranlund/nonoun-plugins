#!/usr/bin/env python3
"""Validate evaluation suites and, optionally, the gate registry, KOS vocabulary and tuning config they use.

Usage: validate_suite.py SUITE [SUITE ...] [--gates FILE] [--vocabulary FILE] [--tune FILE]
                         [--rules FILE] [--target-version V] [--runs PATH]
                         [--max-validation-age DAYS] [--today YYYY-MM-DD] [--strict]

Each finding is one line: SEVERITY RULE SUBJECT FIELD: problem. Fix: fix.
Exit 0 when there are no errors (warnings allowed unless --strict), 1 on errors,
2 when an input file cannot be read. Rule semantics: references/model.md.
Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import datetime
import json
import sys
from collections import namedtuple
from pathlib import Path

import yaml

SUITE_FIELDS = ('id', 'version', 'target', 'target_spec', 'cases', 'cases_path', 'graders', 'slices')
CASE_FIELDS = ('id', 'input', 'expected', 'tags', 'source', 'basis', 'kind', 'variant_of', 'added_because',
               'split', 'added_at', 'graders', 'status', 'retired_reason')
GRADER_FIELDS = ('id', 'kind', 'config', 'validated_against')
VALIDATION_FIELDS = ('human_set', 'agreement', 'n', 'measured_at')
GATE_FIELDS = ('id', 'suite_id', 'suite_version', 'question_id', 'metric', 'slice', 'basis', 'threshold', 'min_n',
               'min_coverage', 'pinned_target_version', 'action', 'owner', 'status')
SOURCES = ('production', 'synthetic', 'adversarial', 'regression')
BASES = ('owner', 'judgment', 'convention', 'agent')  # who or what decided `expected`
KINDS = ('standard', 'invariance', 'negation')
VARIANT_KINDS = ('invariance', 'negation')  # kinds that must name the case they vary
SPLITS = ('dev', 'holdout')
GRADER_KINDS = ('exact', 'programmatic', 'reference', 'rubric-model', 'human')
TRUST_KINDS = ('rubric-model', 'reference')  # graders that must be validated before backing a gate
GATE_STATUSES = ('open', 'passed', 'failed', 'insufficient_n', 'stale')
METRICS = ('pass_rate',)
ALL = 'all'

ERROR_RULES = ('schema', 'duplicate-case-id', 'missing-evidence', 'unknown-grader', 'gate-reference',
               'unvalidated-grader', 'holdout-in-tuning', 'unresolved-label', 'missing-variant',
               'convention-in-judgment-gate', 'uncalibrated-gate', 'stale-gate')
WARNING_RULES = ('synthetic-majority', 'ungated-metric', 'retired-case-gated', 'stale-validation', 'peer-absent',
                 'missing-basis', 'convention-in-judgment-suite')
RULE_ORDER = {rule: i for i, rule in enumerate(ERROR_RULES + WARNING_RULES)}
DEFAULT_MAX_AGE_DAYS = 180


class InputError(Exception):
    """An input file cannot be read (exit 2)."""


class Finding(namedtuple('Finding', 'severity rule subject field problem fix')):
    def line(self):
        return f'{self.severity} {self.rule} {self.subject} {self.field}: {self.problem} Fix: {self.fix}'

    def key(self):
        return (self.severity != 'ERROR', RULE_ORDER[self.rule], self.subject, self.field, self.problem)


def normalize(label):
    """Compare labels case-insensitively with collapsed whitespace, as the KOS validator does."""
    return ' '.join(str(label).casefold().split())


def read_yaml(path):
    """Parse a YAML file. Raises InputError when unreadable, yaml.YAMLError when not YAML."""
    try:
        text = Path(path).read_text(encoding='utf-8')
    except OSError as exc:
        raise InputError(f'{path}: cannot read: {exc.strerror or exc}')
    return yaml.safe_load(text)


def as_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        return None


def direction(expected):
    """The truth value a proposition case expects: a boolean `expected` or `expected.answer`; else None."""
    if isinstance(expected, dict):
        expected = expected.get('answer')
    return expected if isinstance(expected, bool) else None


def expected_labels(expected):
    """The labels inside an expected value: a string, `label`, or each item of `labels`."""
    if isinstance(expected, str):
        return [expected]
    if isinstance(expected, dict):
        labels = [expected['label']] if isinstance(expected.get('label'), str) else []
        if isinstance(expected.get('labels'), list):
            labels += [v for v in expected['labels'] if isinstance(v, str)]
        return labels
    return []


class Vocabulary:
    """Resolve labels against a knowledge-organization-system vocabulary (read by its published field names)."""

    def __init__(self, data):
        self.active, self.retired = {}, {}
        concepts = data.get('concepts') if isinstance(data, dict) else None
        concepts = [c for c in concepts or [] if isinstance(c, dict) and isinstance(c.get('id'), str)]
        by_id = {c['id']: c for c in concepts}
        for c in concepts:
            labels = [c['id'], c.get('prefLabel')] + list(c.get('altLabel') or [])
            if c.get('deprecated'):
                successor = by_id.get(c.get('replacedBy'), {}).get('prefLabel') or c.get('replacedBy')
                for label in labels + list(c.get('hiddenLabel') or []):
                    if isinstance(label, str):
                        self.retired.setdefault(normalize(label), successor)
                continue
            for label in labels:
                if isinstance(label, str):
                    self.active[normalize(label)] = c['id']
            for label in c.get('hiddenLabel') or []:
                if isinstance(label, str):
                    self.retired.setdefault(normalize(label), c.get('prefLabel') or c['id'])

    def resolve(self, label):
        """Return the concept id for an active label, or None."""
        return self.active.get(normalize(label))


class Suite:
    """A parsed suite: schema problems are reported as findings; usable parts are kept."""

    def __init__(self, path, data, findings):
        self.path = Path(path)
        self.id = '-'
        self.version = None
        self.graders = {}
        self.cases = []
        self.slices = {}
        self._read(data, findings)

    def _schema(self, findings, subject, field, problem, fix):
        findings.append(Finding('ERROR', 'schema', subject, field, problem, fix))

    def _read(self, data, findings):
        if not isinstance(data, dict):
            self._schema(findings, str(self.path), '-', 'the file is empty or not a mapping.',
                         'start from templates/suite.yaml.')
            return
        sid = data.get('id')
        if isinstance(sid, str) and sid.strip():
            self.id = sid
        else:
            self._schema(findings, str(self.path), 'id', 'the suite has no id.', 'give the suite a stable `id`.')
        for field in sorted(set(data) - set(SUITE_FIELDS)):
            self._schema(findings, self.id, field, f"unknown suite field '{field}'.",
                         'use only the Suite fields in references/model.md.')
        self.version = data.get('version')
        if not isinstance(self.version, (int, str)) or isinstance(self.version, bool):
            self._schema(findings, self.id, 'version', 'the suite has no version.', 'add `version: 1`.')
        if not isinstance(data.get('target'), str) or not data['target'].strip():
            self._schema(findings, self.id, 'target', 'the suite names no target.',
                         'name what is under test (a prompt, agent, classifier or process).')
        spec = data.get('target_spec')
        if not (isinstance(spec, str) and spec.strip()) and not (
                isinstance(spec, list) and spec and all(isinstance(s, str) and s.strip() for s in spec)):
            self._schema(findings, self.id, 'target_spec', 'the suite states no target spec.',
                         'state the behavior under test, one statement per line.')
        self._read_graders(data.get('graders'), findings)
        self._read_slices(data.get('slices'), findings)
        self._read_cases(data, findings)

    def _read_graders(self, raw, findings):
        if not isinstance(raw, list) or not raw:
            self._schema(findings, self.id, 'graders', 'the suite declares no grader.',
                         'add one `exact` or `programmatic` grader (Stage 0).')
            return
        for i, item in enumerate(raw):
            gid = item.get('id') if isinstance(item, dict) else None
            if not isinstance(gid, str) or not gid.strip():
                self._schema(findings, f'graders[{i}]', 'id', 'grader has no id.', 'give every grader an `id`.')
                continue
            if gid in self.graders:
                self._schema(findings, gid, 'id', f"grader id '{gid}' is declared twice.", 'keep one declaration.')
                continue
            for field in sorted(set(item) - set(GRADER_FIELDS)):
                self._schema(findings, gid, field, f"unknown grader field '{field}'.",
                             f"use only {', '.join(GRADER_FIELDS)}.")
            kind = item.get('kind')
            if kind not in GRADER_KINDS:
                self._schema(findings, gid, 'kind', f"kind '{kind}' is not a grader kind.",
                             f"use one of {', '.join(GRADER_KINDS)}.")
            config = item.get('config') or {}
            if not isinstance(config, dict):
                self._schema(findings, gid, 'config', 'must be a mapping.', 'write `config: {key: value}`.')
                config = {}
            if kind in ('programmatic', 'rubric-model') and not isinstance(config.get('command'), str):
                self._schema(findings, gid, 'config', f'a {kind} grader needs `config.command`.',
                             'name the command that grades one case (references/graders.md).')
            criteria = config.get('criteria')
            if kind == 'rubric-model' and not (isinstance(criteria, list) and criteria
                                                and all(isinstance(c, str) for c in criteria)):
                self._schema(findings, gid, 'config', 'a rubric-model grader needs `config.criteria`.',
                             'list each rubric criterion as one statement.')
            validated = item.get('validated_against')
            if validated is not None:
                validated = self._read_validation(gid, validated, findings)
            self.graders[gid] = {'id': gid, 'kind': kind, 'config': config, 'validated_against': validated}

    def _read_validation(self, gid, value, findings):
        problem = None
        if not isinstance(value, dict):
            problem = 'must be a mapping'
        elif set(value) - set(VALIDATION_FIELDS) or set(VALIDATION_FIELDS) - set(value):
            problem = f"needs exactly {', '.join(VALIDATION_FIELDS)}"
        elif not isinstance(value['agreement'], (int, float)) or not 0 <= value['agreement'] <= 1:
            problem = 'agreement must be a number from 0 to 1'
        elif not isinstance(value['n'], int) or value['n'] < 1:
            problem = 'n must be a positive integer'
        elif as_date(value['measured_at']) is None:
            problem = 'measured_at must be a date (YYYY-MM-DD)'
        if problem:
            self._schema(findings, gid, 'validated_against', f'{problem}.',
                         'record {human_set, agreement, n, measured_at} from the agreement study.')
            return None
        return dict(value, measured_at=as_date(value['measured_at']))

    def _read_slices(self, raw, findings):
        if raw is None:
            return
        if not isinstance(raw, list):
            self._schema(findings, self.id, 'slices', 'must be a list.', 'write `slices: [tag, ...]`.')
            return
        for i, item in enumerate(raw):
            if isinstance(item, str):
                item = {'id': item, 'tags': [item]}
            if not isinstance(item, dict) or not isinstance(item.get('id'), str) or \
                    set(item) - {'id', 'tags', 'cases'} or len(set(item) & {'tags', 'cases'}) != 1:
                self._schema(findings, f'slices[{i}]', 'slices', 'a slice is a tag, `{id, tags}` or `{id, cases}`.',
                             'write the slice in one of those three shapes.')
                continue
            members = item.get('tags', item.get('cases'))
            if not isinstance(members, list) or not all(isinstance(m, str) for m in members):
                self._schema(findings, item['id'], 'slices', 'slice members must be a list of strings.',
                             'list tags or case ids.')
                continue
            if item['id'] == ALL or item['id'] in self.slices:
                self._schema(findings, item['id'], 'slices', f"slice id '{item['id']}' is reserved or repeated.",
                             'give each slice its own id; `all` always exists.')
                continue
            self.slices[item['id']] = {'tags': set(item.get('tags', [])), 'cases': list(item.get('cases', []))}

    def _load_cases(self, data, findings):
        if 'cases' in data and 'cases_path' in data:
            self._schema(findings, self.id, 'cases', 'both `cases` and `cases_path` are set.', 'keep one of them.')
        if 'cases' in data:
            return data['cases']
        if 'cases_path' not in data:
            self._schema(findings, self.id, 'cases', 'the suite has no cases.', 'add `cases:` or `cases_path:`.')
            return []
        path = self.path.parent / str(data['cases_path'])
        try:
            text = path.read_text(encoding='utf-8')
            if path.suffix == '.jsonl':
                return [json.loads(line) for line in text.splitlines() if line.strip()]
            return yaml.safe_load(text)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            self._schema(findings, self.id, 'cases_path', f'cannot read {path}: {exc}.', 'point it at a YAML list or JSONL file.')
            return []

    def _read_cases(self, data, findings):
        raw = self._load_cases(data, findings)
        if not isinstance(raw, list):
            self._schema(findings, self.id, 'cases', 'cases must be a list.', 'write each case as a list item.')
            return
        seen = set()
        for i, item in enumerate(raw):
            if not isinstance(item, dict):
                self._schema(findings, f'cases[{i}]', '-', 'case is not a mapping.', 'write each case as a mapping.')
                continue
            cid = item.get('id')
            if not isinstance(cid, (str, int)) or isinstance(cid, bool) or not str(cid).strip():
                self._schema(findings, f'cases[{i}]', 'id', 'case has no id.', 'give it a stable `id`.')
                continue
            cid = str(cid)
            if cid in seen:
                findings.append(Finding('ERROR', 'duplicate-case-id', cid, 'id', f"case id '{cid}' is used twice.",
                                        'give each case its own id; retire one if both test the same thing.'))
                continue
            seen.add(cid)
            self.cases.append(self._read_case(cid, item, findings))

    def _read_case(self, cid, item, findings):
        for field in sorted(set(item) - set(CASE_FIELDS)):
            self._schema(findings, cid, field, f"unknown case field '{field}'.", 'use only the Case fields in references/model.md.')
        missing = [f for f in ('expected', 'added_because')
                   if item.get(f) is None or (f == 'added_because' and not str(item[f]).strip())]
        if missing:
            findings.append(Finding('ERROR', 'missing-evidence', cid, ','.join(missing),
                                    f"case lacks {' and '.join(missing)}.",
                                    'write the expected outcome and the evidence that produced the case (a bug, log id or spec clause).'))
        case = {'id': cid, 'input': item.get('input'), 'expected': item.get('expected'),
                'added_because': item.get('added_because'), 'added_at': item.get('added_at')}
        if 'input' not in item:
            self._schema(findings, cid, 'input', 'case has no input.', 'write what the target receives.')
        for field, choices, default in (('source', SOURCES, None), ('split', SPLITS, 'dev'),
                                        ('status', ('active', 'retired'), 'active'), ('kind', KINDS, 'standard')):
            value = item.get(field, default)
            if value not in choices:
                self._schema(findings, cid, field, f"'{value}' is not one of {', '.join(choices)}.", f'set `{field}`.')
                value = default
            case[field] = value
        case['basis'] = item.get('basis')
        if case['basis'] is not None and case['basis'] not in BASES:
            self._schema(findings, cid, 'basis', f"'{case['basis']}' is not one of {', '.join(BASES)}.",
                         'name who or what decided `expected`.')
            case['basis'] = None
        variant_of = item.get('variant_of')
        if variant_of is not None and (not isinstance(variant_of, (str, int)) or isinstance(variant_of, bool)):
            self._schema(findings, cid, 'variant_of', 'must be a case id.', 'name the case this one varies.')
            variant_of = None
        case['variant_of'] = None if variant_of is None else str(variant_of)
        for field in ('tags', 'graders'):
            value = item.get(field)
            if value is not None and not (isinstance(value, list) and all(isinstance(v, str) for v in value)):
                self._schema(findings, cid, field, 'must be a list of strings.', f'write `{field}: [a, b]`.')
                value = None
            case[field] = value
        case['tags'] = case['tags'] or []
        if case['status'] == 'retired' and not str(item.get('retired_reason') or '').strip():
            self._schema(findings, cid, 'retired_reason', 'a retired case needs a reason.',
                         'write why it left (the changed spec clause, the duplicate it joined).')
        case['retired_reason'] = item.get('retired_reason')
        if case['added_at'] is not None and as_date(case['added_at']) is None:
            self._schema(findings, cid, 'added_at', 'must be a date (YYYY-MM-DD).', 'write the date the case was added.')
        return case

    def active_cases(self):
        return [c for c in self.cases if c['status'] == 'active']

    def case_graders(self, case):
        return case['graders'] if case['graders'] is not None else list(self.graders)

    def slice_cases(self, slice_id, cases=None):
        """Cases in a slice, from the given list (default: active cases)."""
        cases = self.active_cases() if cases is None else cases
        if slice_id == ALL:
            return list(cases)
        spec = self.slices[slice_id]
        if spec['cases']:
            return [c for c in cases if c['id'] in spec['cases']]
        return [c for c in cases if spec['tags'] & set(c['tags'])]

    def gate_cases(self, gate, cases=None):
        """The cases a gate reads: its slice, narrowed to its `question_id` tag and its `basis` list."""
        members = self.slice_cases(gate['slice'], cases)
        if gate.get('question_id'):
            members = [c for c in members if gate['question_id'] in c['tags']]
        if gate.get('basis'):
            members = [c for c in members if c['basis'] in gate['basis']]
        return members

    def inferred_stage(self, gated):
        if gated:
            return 3
        if any(c['split'] == 'holdout' for c in self.cases) or any(g['kind'] == 'rubric-model' for g in self.graders.values()):
            return 2
        if any(c['source'] == 'regression' for c in self.cases):
            return 1
        return 0


def read_gates(data, findings):
    """Return gate dicts from a registry; shape problems become schema findings."""
    if not isinstance(data, dict) or not isinstance(data.get('gates', []), list) or set(data) - {'gates'}:
        findings.append(Finding('ERROR', 'schema', '-', 'gates', 'the registry is not a mapping with a `gates:` list.',
                                'start from templates/gates.yaml.'))
        return []
    gates, seen = [], set()
    for i, item in enumerate(data.get('gates') or []):
        gid = item.get('id') if isinstance(item, dict) else None
        if not isinstance(gid, str) or not gid.strip() or gid in seen:
            findings.append(Finding('ERROR', 'schema', f'gates[{i}]', 'id', 'gate has no id or repeats one.',
                                    'give every gate its own stable `id`.'))
            continue
        seen.add(gid)
        problems = [f"unknown field '{f}'" for f in sorted(set(item) - set(GATE_FIELDS))]
        for field in ('suite_id', 'metric', 'slice', 'action', 'owner'):
            if not isinstance(item.get(field), str) or not item[field].strip():
                problems.append(f'`{field}` is missing')
        threshold, min_n = item.get('threshold'), item.get('min_n')
        if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or not 0 <= threshold <= 1:
            problems.append('`threshold` must be a number from 0 to 1')
        if not isinstance(min_n, int) or isinstance(min_n, bool) or min_n < 1:
            problems.append('`min_n` must be a positive integer')
        if item.get('status', 'open') not in GATE_STATUSES:
            problems.append(f"`status` must be one of {', '.join(GATE_STATUSES)}")
        pinned = item.get('pinned_target_version')
        if not isinstance(pinned, (int, str)) or isinstance(pinned, bool) or not str(pinned).strip():
            problems.append('`pinned_target_version` is missing')
        if 'question_id' in item and (not isinstance(item['question_id'], str) or not item['question_id'].strip()):
            problems.append('`question_id` must be a case tag')
        basis = item.get('basis')
        if basis is not None and not (isinstance(basis, list) and basis and all(b in BASES for b in basis)):
            problems.append(f"`basis` must be a list of {', '.join(BASES)}")
        coverage = item.get('min_coverage')
        if coverage is not None and (not isinstance(coverage, (int, float)) or isinstance(coverage, bool)
                                     or not 0 <= coverage <= 1):
            problems.append('`min_coverage` must be a number from 0 to 1')
        if problems:
            findings.append(Finding('ERROR', 'schema', gid, '-', '; '.join(problems) + '.',
                                    'write the gate with the Gate fields in references/model.md.'))
            continue
        gates.append(dict(item, status=item.get('status', 'open')))
    return gates


def _check_gates(suites, gates, findings, target_version=None, runs=None):
    """Return {suite id: [gates]} for gates whose references resolve."""
    by_id = {s.id: s for s in suites}
    resolved = {}
    for gate in gates:
        suite = by_id.get(gate['suite_id'])
        problem = None
        if suite is None:
            problem = (f"suite '{gate['suite_id']}' was not validated with this registry.",
                       'correct `suite_id`, or pass the suite on the command line.', 'suite_id')
        elif gate['metric'] not in METRICS:
            problem = (f"metric '{gate['metric']}' is not defined.", f"use {', '.join(METRICS)}.", 'metric')
        elif gate['slice'] != ALL and gate['slice'] not in suite.slices:
            problem = (f"slice '{gate['slice']}' is not declared in suite '{suite.id}'.",
                       f"declare it under `slices`, or use one of: {', '.join([ALL] + sorted(suite.slices))}.", 'slice')
        elif gate.get('question_id') and not any(gate['question_id'] in c['tags'] for c in suite.active_cases()):
            problem = (f"no active case in suite '{suite.id}' is tagged with question '{gate['question_id']}'.",
                       'tag the question\'s cases with its id, or correct `question_id`.', 'question_id')
        if problem:
            findings.append(Finding('ERROR', 'gate-reference', gate['id'], problem[2], problem[0], problem[1]))
            continue
        resolved.setdefault(suite.id, []).append(gate)
        members = suite.gate_cases(gate)
        backing = sorted({g for c in members for g in suite.case_graders(c)
                          if g in suite.graders and suite.graders[g]['kind'] in TRUST_KINDS
                          and not suite.graders[g]['validated_against']})
        if backing:
            findings.append(Finding('ERROR', 'unvalidated-grader', gate['id'], 'slice',
                                    f"slice '{gate['slice']}' is graded by {', '.join(backing)} with no validated_against.",
                                    'measure agreement with human judgment and record validated_against (references/graders.md), or gate a slice that grader does not grade.'))
        if gate['slice'] != ALL:
            for cid in suite.slices[gate['slice']]['cases']:
                if any(c['id'] == cid and c['status'] == 'retired' for c in suite.cases):
                    findings.append(Finding('WARNING', 'retired-case-gated', gate['id'], 'slice',
                                            f"slice '{gate['slice']}' names retired case '{cid}'.",
                                            'repoint the slice at active cases.'))
        bases = {c['basis'] for c in members}
        if {'judgment', 'convention'} <= bases:
            findings.append(Finding('ERROR', 'convention-in-judgment-gate', gate['id'], 'basis',
                                    f"the gate reads judgment cases and {sum(c['basis'] == 'convention' for c in members)} "
                                    'convention case(s), whose rule-derived gold inflates measured accuracy.',
                                    'set the gate\'s `basis` to exclude convention, for example [owner, judgment].'))
        if runs is not None and 'min_coverage' in gate:
            latest = runs.get(suite.id)
            if not (latest and isinstance(latest.get('calibration'), dict)):
                where = f"run '{latest.get('id')}'" if latest else 'no run given for this suite'
                findings.append(Finding('ERROR', 'uncalibrated-gate', gate['id'], 'min_coverage',
                                        f'the gate relies on confidence bands but its latest run has no calibration ({where}).',
                                        'run the suite on dev with a target that returns `confidence`, so the run records calibration.'))
        pinned = str(gate['pinned_target_version'])
        if target_version is not None and gate['status'] == 'passed' and pinned != str(target_version):
            findings.append(Finding('ERROR', 'stale-gate', gate['id'], 'status',
                                    f"the gate is recorded passed at target version {pinned}, but the target is now {target_version}.",
                                    'record `status: stale`, re-run the suite on the new version, then re-pin the gate.'))
    return resolved


def _check_suite(suite, vocabulary, rules_given, max_age, today, findings):
    for case in suite.cases:
        for gid in case['graders'] or []:
            if gid not in suite.graders:
                findings.append(Finding('ERROR', 'unknown-grader', case['id'], 'graders',
                                        f"grader '{gid}' is not declared in suite '{suite.id}'.",
                                        f"use one of: {', '.join(sorted(suite.graders)) or '(declare a grader)'}."))
    labelled = [c for c in suite.cases if c['expected'] is not None and expected_labels(c['expected'])]
    if vocabulary is not None:
        for case in labelled:
            for label in expected_labels(case['expected']):
                if vocabulary.resolve(label) is None:
                    successor = vocabulary.retired.get(normalize(label))
                    hint = f"write '{successor}' (the label is retired)." if successor else \
                        'use a concept id, prefLabel or altLabel, or add the concept through knowledge-organization-system first.'
                    findings.append(Finding('ERROR', 'unresolved-label', case['id'], 'expected',
                                            f"label '{label}' resolves to no active concept.", hint))
    elif labelled:
        findings.append(Finding('WARNING', 'peer-absent', suite.id, 'expected',
                                f'{len(labelled)} case(s) have expected labels but no vocabulary is configured; labels are unchecked strings.',
                                'pass --vocabulary with the knowledge-organization-system vocabulary, or accept plain labels knowingly.'))
    if not rules_given and any(g['kind'] == 'rubric-model' and g['config'].get('criteria') for g in suite.graders.values()):
        findings.append(Finding('WARNING', 'peer-absent', suite.id, 'criteria',
                                'rubric criteria are plain sentences with no controlled-natural-language rules file.',
                                'pass --rules and lint the criteria with controlled-natural-language, or accept plain criteria knowingly.'))
    ids = {c['id'] for c in suite.cases}
    for case in suite.cases:
        if case['kind'] in VARIANT_KINDS and case['variant_of'] not in ids:
            problem = (f"`variant_of` names '{case['variant_of']}', which is not a case in suite '{suite.id}'."
                       if case['variant_of'] else 'the case does not name the case it varies.')
            findings.append(Finding('ERROR', 'missing-variant', case['id'], 'variant_of',
                                    f"{case['kind']} case: {problem}",
                                    'set `variant_of` to the id of the standard case it permutes or negates.'))
    active = suite.active_cases()
    unstated = [c['id'] for c in active if c['basis'] is None]
    if unstated:
        listed = ', '.join(unstated[:5]) + (f' and {len(unstated) - 5} more' if len(unstated) > 5 else '')
        findings.append(Finding('WARNING', 'missing-basis', suite.id, 'basis',
                                f'{len(unstated)} active case(s) state no basis ({listed}); nobody can tell who decided their gold.',
                                f"set `basis` on each case to one of {', '.join(BASES)}."))
    if {'judgment', 'convention'} <= {c['basis'] for c in active}:
        findings.append(Finding('WARNING', 'convention-in-judgment-suite', suite.id, 'basis',
                                'the suite mixes judgment and convention cases.',
                                'give every judgment gate a `basis` that excludes convention, or move convention cases to their own suite.'))
    synthetic = sum(c['source'] == 'synthetic' for c in active)
    if active and synthetic * 2 > len(active):
        findings.append(Finding('WARNING', 'synthetic-majority', suite.id, 'source',
                                f'{synthetic} of {len(active)} active cases are synthetic.',
                                'add production, adversarial or regression cases; synthetic cases never make up a whole suite.'))
    for gid, grader in sorted(suite.graders.items()):
        validated = grader['validated_against']
        if validated and (today - validated['measured_at']).days > max_age:
            findings.append(Finding('WARNING', 'stale-validation', gid, 'validated_against',
                                    f"agreement was measured {validated['measured_at']}, more than {max_age} days ago.",
                                    're-measure agreement on a fresh human sample and update validated_against.'))


def _check_tuning(suites, tune, findings):
    if not isinstance(tune, dict) or set(tune) - {'cases'} or not isinstance(tune.get('cases'), list):
        findings.append(Finding('ERROR', 'schema', '-', 'tune', 'the tuning config is not a mapping with a `cases:` list.',
                                'write `cases: [ids]` naming the cases tuned against.'))
        return
    cases = {c['id']: c for s in suites for c in s.cases}
    for cid in tune['cases']:
        case = cases.get(str(cid))
        if case is None:
            findings.append(Finding('ERROR', 'schema', str(cid), 'tune', 'the tuning config names an unknown case.',
                                    'list only case ids from the validated suites.'))
        elif case['split'] == 'holdout':
            findings.append(Finding('ERROR', 'holdout-in-tuning', str(cid), 'split',
                                    'the tuning config names a holdout case.',
                                    'tune on dev cases only; move this case to dev and add a fresh holdout case.'))


def latest_runs(paths):
    """Return {suite id: the run.json with the latest started_at} from run.json files and folders holding them."""
    files = []
    for path in map(Path, paths):
        files += sorted(path.rglob('run.json')) if path.is_dir() else [path]
    latest = {}
    for path in files:
        try:
            run = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise InputError(f'{path}: cannot read a run: {exc}')
        if not isinstance(run, dict) or not isinstance(run.get('suite_id'), str):
            raise InputError(f'{path}: not a run.json (no suite_id)')
        current = latest.get(run['suite_id'])
        if current is None or str(run.get('started_at')) > str(current.get('started_at')):
            latest[run['suite_id']] = run
    return latest


def check(suite_paths, gates_path=None, vocabulary_path=None, tune_path=None, rules_path=None,
          max_age=DEFAULT_MAX_AGE_DAYS, today=None, target_version=None, run_paths=None):
    """Return (sorted findings, suites, {suite id: gates}, Vocabulary or None). Raises InputError."""
    findings = []
    today = today or datetime.date.today()

    def parse(path, label):
        try:
            return read_yaml(path)
        except yaml.YAMLError as exc:
            problem = ' '.join(str(exc).split())
            findings.append(Finding('ERROR', 'schema', str(path), label, f'not valid YAML: {problem}.', 'fix the YAML syntax.'))
            return None

    suites = [Suite(p, parse(p, 'suite'), findings) for p in suite_paths]
    vocabulary = Vocabulary(parse(vocabulary_path, 'vocabulary')) if vocabulary_path else None
    if rules_path:
        read_yaml(rules_path)  # must exist and be readable; linting criteria belongs to controlled-natural-language
    for suite in suites:
        _check_suite(suite, vocabulary, bool(rules_path), max_age, today, findings)
    gates = {}
    if gates_path:
        runs = latest_runs(run_paths) if run_paths else None
        gates = _check_gates(suites, read_gates(parse(gates_path, 'gates'), findings), findings, target_version, runs)
        for suite in suites:
            gated = {g['slice'] for g in gates.get(suite.id, [])}
            if gates.get(suite.id):
                for slice_id in sorted(set(suite.slices) - gated):
                    findings.append(Finding('WARNING', 'ungated-metric', suite.id, 'slices',
                                            f"slice '{slice_id}' has no gate at Stage 3.",
                                            'gate it with a threshold, min_n, action and owner, or drop the slice.'))
    if tune_path:
        _check_tuning(suites, parse(tune_path, 'tune'), findings)
    return sorted(findings, key=Finding.key), suites, gates, vocabulary


def add_input_arguments(parser):
    """The inputs the validator and the runner share."""
    parser.add_argument('--gates', metavar='FILE', help='gate registry (gates.yaml)')
    parser.add_argument('--vocabulary', metavar='FILE', help='knowledge-organization-system vocabulary for expected labels')
    parser.add_argument('--tune', metavar='FILE', help='tuning config: `cases: [ids]` tuned against')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('suites', nargs='+', metavar='SUITE', help='suite YAML file(s)')
    add_input_arguments(parser)
    parser.add_argument('--rules', metavar='FILE', help='controlled-natural-language rules file for rubric criteria')
    parser.add_argument('--target-version', metavar='V', help="the target's current version, for stale gates")
    parser.add_argument('--runs', action='append', metavar='PATH',
                        help='a run.json or a folder of them (repeatable); the latest per suite is checked for calibration')
    parser.add_argument('--max-validation-age', type=int, default=DEFAULT_MAX_AGE_DAYS, metavar='DAYS',
                        help=f'age after which validated_against is stale (default {DEFAULT_MAX_AGE_DAYS})')
    parser.add_argument('--today', type=datetime.date.fromisoformat, help='date for staleness checks (YYYY-MM-DD)')
    parser.add_argument('--strict', action='store_true', help='exit 1 on warnings too')
    args = parser.parse_args(argv)
    try:
        findings, suites, gates, _ = check(args.suites, args.gates, args.vocabulary, args.tune, args.rules,
                                           args.max_validation_age, args.today, args.target_version, args.runs)
    except InputError as exc:
        print(exc, file=sys.stderr)
        return 2
    errors = sum(f.severity == 'ERROR' for f in findings)
    warnings = len(findings) - errors
    for finding in findings:
        print(finding.line())
    stages = [str(s.inferred_stage(bool(gates.get(s.id)))) for s in suites]
    stage = stages[0] if len(suites) == 1 else ', '.join(f'{s.id}={n}' for s, n in zip(suites, stages))
    print(f"{', '.join(args.suites)}: {errors} error(s), {warnings} warning(s), inferred stage {stage}")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main())
