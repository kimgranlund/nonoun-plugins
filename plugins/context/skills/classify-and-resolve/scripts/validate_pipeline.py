#!/usr/bin/env python3
"""Validate classify-and-resolve pipeline specs against a KOS vocabulary, a gate registry, question sets and logs.

Usage: validate_pipeline.py PIPELINE [PIPELINE ...] [--vocabulary FILE] [--gates FILE] [--question-set FILE ...]
                            [--log FILE ...] [--window-days N] [--max-unclassified-share X]
                            [--today YYYY-MM-DD] [--strict]

A pipeline file may hold several YAML documents; each is one pipeline, validated on its own.
Each finding is one line: SEVERITY RULE SUBJECT FIELD: problem. Fix: fix.
Exit 0 when there are no errors (warnings allowed unless --strict), 1 on errors,
2 when an input file cannot be read. Rule semantics: references/model.md.
Question sets are checked by decision-questions' validate_questions.py, run as a subprocess by path.
Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import datetime
import json
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

import yaml

UNCLASSIFIED = 'unclassified'  # reserved label: never a concept id, never a route key
VALIDATE_QUESTIONS = Path(__file__).resolve().parents[2] / 'decision-questions' / 'scripts' / 'validate_questions.py'

PIPELINE_FIELDS = ('id', 'version', 'scheme', 'classes', 'cascade', 'fallback', 'routes', 'unclassified_route',
                   'rule_repair_route', 'resolvers')
CLASS_FIELDS = ('id', 'definition')
STEP_FIELDS = ('classifier_id', 'kind', 'question_set', 'abstain_below', 'rules')
RESOLVER_FIELDS = ('id', 'accepts', 'output_type', 'side_effects', 'autonomy', 'promotion_gate',
                   'review_sample_rate', 'policy')
STEP_KINDS = ('rule', 'observed', 'model', 'human')
FALLBACKS = ('broader', 'unclassified')
SIDE_EFFECTS = ('none', 'reversible', 'irreversible')
AUTONOMY = ('manual', 'suggest', 'auto')
ROLES = ('checker', 'suggester', 'voter')  # decision-questions role ladder, lowest first

ENVELOPE_FIELDS = ('log_id', 'at', 'pipeline_id', 'pipeline_version', 'record', 'item_id')
CLASSIFICATION_FIELDS = ('item', 'label', 'level', 'confidence', 'rationale', 'evidence', 'classifier_id',
                         'cascade_step', 'model_version')
CLASSIFICATION_REQUIRED = ('label', 'level', 'confidence', 'classifier_id', 'cascade_step')
LEVELS = ('exact', 'broader')
EVIDENCE_FIELDS = ('kind', 'ref', 'value')
EVIDENCE_KINDS = ('rule', 'observed', 'answer')
RESOLUTION_FIELDS = ('resolver_id', 'status', 'output', 'decided_by', 'corrected_label')
RESOLUTION_REQUIRED = ('resolver_id', 'status', 'output', 'decided_by')
ITEM_FIELDS = ('id', 'source', 'payload', 'received_at')
RECORD_KINDS = ('classification', 'resolution')
STATUSES = ('resolved', 'escalated', 'deferred', 'rejected')
DECIDERS = ('resolver', 'human')

ERROR_RULES = ('schema', 'unrouted-class', 'unknown-resolver', 'unresolved-route', 'missing-unclassified-route',
               'auto-unclassified', 'no-fallthrough', 'autonomy-matrix', 'unknown-gate', 'gate-not-passed',
               'abstain-range', 'model-question-set', 'question-set-role', 'broader-fallback',
               'missing-rule-repair-route')
WARNING_RULES = ('idle-class', 'unclassified-share', 'unreviewed-suggest', 'peer-absent')
RULE_ORDER = {rule: i for i, rule in enumerate(ERROR_RULES + WARNING_RULES)}


class Finding(namedtuple('Finding', 'severity rule subject field problem fix')):
    def line(self):
        return f'{self.severity} {self.rule} {self.subject} {self.field}: {self.problem} Fix: {self.fix}'

    def key(self):
        return (self.severity != 'ERROR', RULE_ORDER[self.rule], self.subject, self.field, self.problem)


class InputError(Exception):
    """An input file is missing or cannot be parsed; the caller exits 2."""


def normalize(label):
    return ' '.join(str(label).casefold().split())


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def needs_gate(side_effects, autonomy):
    """The autonomy matrix: the cells that require a passed promotion_gate."""
    return autonomy == 'auto' or (side_effects == 'irreversible' and autonomy == 'suggest')


# ---------------------------------------------------------------- inputs

def load_pipelines(path):
    """Return the YAML documents in a pipeline file. Raises OSError or yaml.YAMLError."""
    text = Path(path).read_text(encoding='utf-8')
    return [doc for doc in yaml.safe_load_all(text) if doc is not None]


def load_yaml(path, what):
    try:
        return yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    except OSError as exc:
        raise InputError(f'{path}: cannot read {what}: {exc.strerror or exc}')
    except yaml.YAMLError as exc:
        raise InputError(f'{path}: {what} is not valid YAML: {" ".join(str(exc).split())}')


def load_vocabulary(path):
    data = load_yaml(path, 'vocabulary')
    if not isinstance(data, dict) or not isinstance(data.get('concepts'), list):
        raise InputError(f'{path}: not a knowledge-organization-system vocabulary (no `concepts:` list)')
    schemes = {s.get('id') for s in data.get('schemes') or [] if isinstance(s, dict)}
    concepts = {c['id']: c for c in data['concepts'] if isinstance(c, dict) and isinstance(c.get('id'), str)}
    return {'schemes': schemes, 'concepts': concepts}


def load_question_sets(paths, gates_path):
    """Read question sets and check each with validate_questions.py. Returns {id: {data, path, problems}}."""
    sets = {}
    for path in paths:
        data = load_yaml(path, 'question set')
        qid = data.get('id') if isinstance(data, dict) else None
        if not isinstance(qid, str):
            raise InputError(f'{path}: not a decision-questions question set (no `id`)')
        if not VALIDATE_QUESTIONS.is_file():
            sets[qid] = {'data': data, 'path': path, 'problems': None}
            continue
        command = [sys.executable, '-B', str(VALIDATE_QUESTIONS), str(path)]
        if gates_path:
            command += ['--gates', str(gates_path)]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 2:
            raise InputError(f'{path}: validate_questions.py could not read its inputs: '
                             f'{result.stderr.strip() or result.stdout.strip()}')
        errors = [line.split(' ', 2)[1] for line in result.stdout.splitlines() if line.startswith('ERROR ')]
        sets[qid] = {'data': data, 'path': path, 'problems': sorted(set(errors))}
    return sets


def can_abstain(question_set):
    """True when a question set has a decision that can hold an answer back: a review band or a margin above 0."""
    decisions = question_set.get('decisions') if isinstance(question_set, dict) else None
    for decision in decisions if isinstance(decisions, list) else []:
        if not isinstance(decision, dict):
            continue
        bands = decision.get('bands') if isinstance(decision.get('bands'), dict) else {}
        if (is_number(bands.get('review')) and bands['review'] > 0) or \
                (is_number(decision.get('margin')) and decision['margin'] > 0):
            return True
    return False


def load_gates(path):
    data = load_yaml(path, 'gate registry')
    gates = data.get('gates') if isinstance(data, dict) else None
    if not isinstance(gates, list):
        raise InputError(f'{path}: not an evaluation-system gate registry (no `gates:` list)')
    return {g['id']: g.get('status') or 'open' for g in gates if isinstance(g, dict) and isinstance(g.get('id'), str)}


def check_record(record):
    """Return the problems with one log record against templates/log.schema.json."""
    if not isinstance(record, dict):
        return ['the record is not a JSON object']
    problems = [f'`{f}` is missing' for f in ENVELOPE_FIELDS if f not in record]
    kind = record.get('record')
    if kind not in RECORD_KINDS:
        return problems + [f'`record` is {kind!r}, not one of {", ".join(RECORD_KINDS)}']
    own, required = ((CLASSIFICATION_FIELDS, CLASSIFICATION_REQUIRED) if kind == 'classification'
                     else (RESOLUTION_FIELDS, RESOLUTION_REQUIRED))
    problems += [f'`{f}` is missing' for f in required if f not in record]
    problems += [f'`{f}` is not a {kind} field' for f in sorted(set(record) - set(ENVELOPE_FIELDS) - set(own))]
    if kind == 'classification':
        conf = record.get('confidence')
        if conf is not None and not (is_number(conf) and 0 <= conf <= 1):
            problems.append('`confidence` is not a number in [0, 1] or null')
        if 'cascade_step' in record and not (isinstance(record['cascade_step'], int)
                                             and not isinstance(record['cascade_step'], bool)
                                             and record['cascade_step'] >= 0):
            problems.append('`cascade_step` is not a non-negative integer')
        if 'level' in record and record['level'] not in LEVELS:
            problems.append(f'`level` is {record["level"]!r}, not one of {", ".join(LEVELS)}')
        evidence = record.get('evidence', [])
        if not isinstance(evidence, list):
            problems.append('`evidence` is not a list')
        else:
            for i, entry in enumerate(evidence):
                if not isinstance(entry, dict) or entry.get('kind') not in EVIDENCE_KINDS or 'ref' not in entry \
                        or set(entry) - set(EVIDENCE_FIELDS):
                    problems.append(f'`evidence[{i}]` is not {{kind: {"|".join(EVIDENCE_KINDS)}, ref, value}}')
        item = record.get('item')
        if item is not None:
            if not isinstance(item, dict):
                problems.append('`item` is not an object')
            else:
                problems += [f'`item.{f}` is missing' for f in ITEM_FIELDS if f not in item]
                problems += [f'`item.{f}` is not an Item field' for f in sorted(set(item) - set(ITEM_FIELDS))]
                if 'id' in item and item['id'] != record.get('item_id'):
                    problems.append('`item.id` differs from `item_id`')
    else:
        if record.get('status') not in STATUSES and 'status' in record:
            problems.append(f'`status` is {record["status"]!r}, not one of {", ".join(STATUSES)}')
        if record.get('decided_by') not in DECIDERS and 'decided_by' in record:
            problems.append(f'`decided_by` is {record["decided_by"]!r}, not one of {", ".join(DECIDERS)}')
    return problems


def read_log(paths):
    """Read JSONL logs. Returns (records, problems); each problem is (where, message). Raises InputError."""
    records, problems, seen = [], [], set()
    for path in paths:
        try:
            lines = Path(path).read_text(encoding='utf-8').splitlines()
        except OSError as exc:
            raise InputError(f'{path}: cannot read log: {exc.strerror or exc}')
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            where = f'{path}:{number}'
            try:
                record = json.loads(line)
            except ValueError as exc:
                problems.append((where, f'not valid JSON: {exc}'))
                continue
            found = check_record(record)
            if not found and record['log_id'] in seen:
                found = [f"`log_id` {record['log_id']!r} repeats"]
            if found:
                problems.append((where, '; '.join(found)))
                continue
            seen.add(record['log_id'])
            records.append(dict(record, _where=where, _order=len(records)))
    return records, problems


def item_outcomes(records):
    """Fold records into one outcome per item: the final classification, resolutions, the latest correction."""
    items = {}
    for record in records:
        entry = items.setdefault(record['item_id'], {'final': None, 'resolutions': [], 'corrected': None,
                                                     'item': None})
        if record['record'] == 'classification':
            key = (record['cascade_step'], record['at'], record['_order'])
            final = entry['final']
            if final is None or key >= (final['cascade_step'], final['at'], final['_order']):
                entry['final'] = record
            if record.get('item') is not None and entry['item'] is None:
                entry['item'] = record['item']
        else:
            entry['resolutions'].append(record)
            if record.get('corrected_label'):
                entry['corrected'] = record
    return items


# ---------------------------------------------------------------- pipeline rules

def _classes(pipeline, pid, vocab, findings):
    """Return (classes, concepts) where classes maps id -> concept for the pipeline's scheme."""
    scheme = pipeline.get('scheme')
    if vocab is not None:
        if scheme not in vocab['schemes']:
            findings.append(Finding('ERROR', 'schema', pid, 'scheme',
                                    f'scheme {scheme!r} is not declared in the vocabulary.',
                                    'name a scheme the vocabulary declares, or add it through knowledge-organization-system.'))
        classes = {cid: c for cid, c in vocab['concepts'].items()
                   if c.get('scheme') == scheme and not c.get('deprecated') and cid != UNCLASSIFIED}
        return classes, vocab['concepts']
    inline = pipeline.get('classes')
    if not isinstance(inline, list) or not inline:
        findings.append(Finding('ERROR', 'schema', pid, 'classes',
                                'no vocabulary was given and the pipeline lists no inline classes.',
                                'pass --vocabulary, or list `classes: [{id, definition}]` in the pipeline.'))
        return {}, {}
    classes = {}
    for i, entry in enumerate(inline):
        if not isinstance(entry, dict) or not isinstance(entry.get('id'), str) or not entry.get('definition'):
            findings.append(Finding('ERROR', 'schema', f'{pid}:classes[{i}]', 'id',
                                    'an inline class needs an `id` and a one-line `definition`.',
                                    'write `{id, definition}` for every class.'))
            continue
        for field in sorted(set(entry) - set(CLASS_FIELDS)):
            findings.append(Finding('ERROR', 'schema', f'{pid}:{entry["id"]}', field,
                                    f'unknown inline class field `{field}`.',
                                    'keep inline classes to `{id, definition}`; richer classes belong in a KOS vocabulary.'))
        classes[entry['id']] = dict(entry, scheme=scheme)
    return classes, classes


def _check_shape(pipeline, pid, findings):
    def schema(subject, field, problem, fix):
        findings.append(Finding('ERROR', 'schema', subject, field, problem, fix))

    for field in sorted(set(pipeline) - set(PIPELINE_FIELDS)):
        schema(pid, field, f'unknown pipeline field `{field}`.', f'use only {", ".join(PIPELINE_FIELDS)}.')
    for field in ('id', 'version', 'scheme', 'cascade', 'routes', 'resolvers'):
        if field not in pipeline:
            schema(pid, field, f'required field `{field}` is missing.', 'add it (references/model.md, Pipeline).')
    cascade = pipeline.get('cascade')
    if 'cascade' in pipeline and (not isinstance(cascade, list) or not cascade):
        schema(pid, 'cascade', 'the cascade lists no steps.', 'start with one `human` step (Stage 0).')
    for i, step in enumerate(cascade if isinstance(cascade, list) else []):
        subject = f'{pid}:cascade[{i}]'
        if not isinstance(step, dict):
            schema(subject, '-', 'a cascade step is not a mapping.', 'write `{classifier_id, kind}`.')
            continue
        for field in sorted(set(step) - set(STEP_FIELDS)):
            schema(subject, field, f'unknown cascade step field `{field}`.', f'use only {", ".join(STEP_FIELDS)}.')
        if not isinstance(step.get('classifier_id'), str):
            schema(subject, 'classifier_id', 'the step has no `classifier_id`.', 'name the classifier.')
        if step.get('kind') not in STEP_KINDS:
            schema(subject, 'kind', f'kind {step.get("kind")!r} is not one of {", ".join(STEP_KINDS)}.',
                   'use rule, observed, model or human.')
        if 'question_set' in step and step.get('kind') != 'model':
            schema(subject, 'question_set', 'only a `model` step reads a question set.',
                   'remove `question_set`, or make the step kind model.')
        elif 'question_set' in step and not isinstance(step['question_set'], str):
            schema(subject, 'question_set', '`question_set` is not a question set id.',
                   'name the decision-questions question set by its `id`.')
        if 'abstain_below' in step and not is_number(step['abstain_below']):
            schema(subject, 'abstain_below', '`abstain_below` is not a number.', 'write a confidence between 0 and 1.')
        if 'rules' in step and not (isinstance(step['rules'], list) and all(isinstance(r, str) for r in step['rules'])):
            schema(subject, 'rules', '`rules` is not a list of statements.',
                   'write each rule as one controlled-natural-language statement.')
    if 'fallback' in pipeline and pipeline['fallback'] not in FALLBACKS:
        schema(pid, 'fallback', f'fallback {pipeline["fallback"]!r} is not one of {", ".join(FALLBACKS)}.',
               'use broader or unclassified.')
    if 'routes' in pipeline and not isinstance(pipeline['routes'], dict):
        schema(pid, 'routes', '`routes` is not a mapping of class id to resolver id.', 'write `routes: {class-id: resolver-id}`.')
    resolvers = pipeline.get('resolvers')
    if 'resolvers' in pipeline and not isinstance(resolvers, list):
        schema(pid, 'resolvers', '`resolvers` is not a list.', 'list each resolver contract.')
    seen = set()
    for i, res in enumerate(resolvers if isinstance(resolvers, list) else []):
        rid = res.get('id') if isinstance(res, dict) else None
        subject = f'{pid}:{rid}' if isinstance(rid, str) else f'{pid}:resolvers[{i}]'
        if not isinstance(res, dict) or not isinstance(rid, str):
            schema(subject, 'id', 'a resolver has no `id`.', 'give every resolver a stable id.')
            continue
        if rid in seen:
            schema(subject, 'id', f'resolver id {rid!r} is declared twice.', 'keep one declaration.')
        seen.add(rid)
        for field in sorted(set(res) - set(RESOLVER_FIELDS)):
            schema(subject, field, f'unknown resolver field `{field}`.', f'use only {", ".join(RESOLVER_FIELDS)}.')
        for field in ('accepts', 'output_type', 'side_effects', 'autonomy'):
            if field not in res:
                schema(subject, field, f'required field `{field}` is missing.', 'declare the full resolver contract.')
        if 'accepts' in res and not (isinstance(res['accepts'], list) and res['accepts']):
            schema(subject, 'accepts', '`accepts` is not a non-empty list of class ids.', 'list the classes it accepts.')
        if 'side_effects' in res and res['side_effects'] not in SIDE_EFFECTS:
            schema(subject, 'side_effects', f'{res["side_effects"]!r} is not one of {", ".join(SIDE_EFFECTS)}.',
                   'use none, reversible or irreversible.')
        if 'autonomy' in res and res['autonomy'] not in AUTONOMY:
            schema(subject, 'autonomy', f'{res["autonomy"]!r} is not one of {", ".join(AUTONOMY)}.',
                   'use manual, suggest or auto.')
        rate = res.get('review_sample_rate')
        if rate is not None and not (is_number(rate) and 0 <= rate <= 1):
            schema(subject, 'review_sample_rate', '`review_sample_rate` is not a number in [0, 1].',
                   'write the share of auto decisions a human reviews, for example 0.05.')


def validate_pipeline(pipeline, vocab, gates, findings, question_sets=None):
    """Append findings for one pipeline document. Returns (pipeline id, inferred stage, classes, resolvers).

    question_sets is {id: {data, path, problems}} from load_question_sets, or None when none were given."""
    if not isinstance(pipeline, dict):
        findings.append(Finding('ERROR', 'schema', '-', '-', 'a document is not a pipeline mapping.',
                                'write the Pipeline fields from references/model.md.'))
        return '-', 0, {}, {}
    pid = pipeline.get('id') if isinstance(pipeline.get('id'), str) else '-'
    _check_shape(pipeline, pid, findings)
    classes, concepts = _classes(pipeline, pid, vocab, findings)
    routes = pipeline.get('routes') if isinstance(pipeline.get('routes'), dict) else {}
    resolvers = {r['id']: r for r in pipeline.get('resolvers') or []
                 if isinstance(r, dict) and isinstance(r.get('id'), str)} \
        if isinstance(pipeline.get('resolvers'), list) else {}
    scheme = pipeline.get('scheme')

    for cid in sorted(set(classes) - set(routes)):
        findings.append(Finding('ERROR', 'unrouted-class', f'{pid}:{cid}', 'routes',
                                f'class {cid!r} in scheme {scheme!r} has no route.',
                                'route it to exactly one resolver, or deprecate the concept through knowledge-organization-system.'))
    for key in sorted(routes, key=str):
        target = routes[key]
        subject = f'{pid}:{key}'
        if key == UNCLASSIFIED:
            findings.append(Finding('ERROR', 'schema', subject, 'routes',
                                    '`unclassified` is reserved and is not a route key.',
                                    'route abstentions with `unclassified_route`.'))
        elif key not in classes:
            concept = concepts.get(key)
            if concept is not None and concept.get('deprecated'):
                problem = f'route key {key!r} is a deprecated concept.'
                fix = f"route {concept.get('replacedBy')!r} instead and bump the pipeline version."
            elif concept is not None:
                problem = f'route key {key!r} is in scheme {concept.get("scheme")!r}, not {scheme!r}.'
                fix = "route only the pipeline scheme's concepts."
            else:
                match = sorted(cid for cid, c in classes.items()
                               if normalize(key) in [normalize(c.get('prefLabel', ''))]
                               + [normalize(a) for a in c.get('altLabel') or []])
                problem = f'route key {key!r} does not resolve to a concept id in the vocabulary.'
                fix = (f'write the concept id {match[0]!r}, not a label.' if match
                       else 'use a concept id, or add the class through knowledge-organization-system first.')
            findings.append(Finding('ERROR', 'unresolved-route', subject, 'routes', problem, fix))
        if not isinstance(target, str) or target not in resolvers:
            findings.append(Finding('ERROR', 'unknown-resolver', subject, 'routes',
                                    f'route target {target!r} is not a declared resolver.',
                                    'declare the resolver under `resolvers`, or route to one that exists.'))

    catch = pipeline.get('unclassified_route')
    if not catch:
        findings.append(Finding('ERROR', 'missing-unclassified-route', pid, 'unclassified_route',
                                'the pipeline has no `unclassified_route`, so abstentions have nowhere to go.',
                                'route `unclassified` to a manual human or deferred queue.'))
    elif not isinstance(catch, str) or catch not in resolvers:
        findings.append(Finding('ERROR', 'unknown-resolver', f'{pid}:{UNCLASSIFIED}', 'unclassified_route',
                                f'unclassified_route {catch!r} is not a declared resolver.',
                                'declare a manual resolver for the unclassified queue.'))
    elif resolvers[catch].get('autonomy') == 'auto':
        findings.append(Finding('ERROR', 'auto-unclassified', f'{pid}:{catch}', 'autonomy',
                                f'unclassified_route leads to {catch!r}, which acts with autonomy auto.',
                                'send unclassified items to a manual or suggest resolver a human works.'))

    repair = pipeline.get('rule_repair_route')
    if 'rule_repair_route' in pipeline and (not isinstance(repair, str) or repair not in resolvers):
        findings.append(Finding('ERROR', 'unknown-resolver', pid, 'rule_repair_route',
                                f'rule_repair_route {repair!r} is not a declared resolver.',
                                'declare a manual resolver that owns rule and observed-evidence fixes.'))

    cascade = [s for s in pipeline.get('cascade') or [] if isinstance(s, dict)] \
        if isinstance(pipeline.get('cascade'), list) else []
    kinds = {s.get('kind') for s in cascade}
    for i, step in enumerate(cascade):
        value = step.get('abstain_below')
        if is_number(value) and not 0 <= value <= 1:
            findings.append(Finding('ERROR', 'abstain-range', f'{pid}:cascade[{i}]', 'abstain_below',
                                    f'abstain_below {value} is outside [0, 1].',
                                    'write a confidence between 0 and 1, tuned on dev cases only.'))
    _check_model_steps(pid, cascade, routes, resolvers, question_sets, findings)
    if cascade:
        last = cascade[-1]
        threshold = last.get('abstain_below')
        known = (question_sets or {}).get(last.get('question_set'))
        if last.get('kind') == 'model' and not (is_number(threshold) and threshold > 0) \
                and (known is not None or not last.get('question_set')) \
                and not (known is not None and can_abstain(known['data'])):
            findings.append(Finding('ERROR', 'no-fallthrough', f'{pid}:cascade[{len(cascade) - 1}]', 'kind',
                                    'the final step is a model that never abstains, so no item can fall through to unclassified.',
                                    'end the cascade with a `human` step, or give the final model a question set '
                                    'with a review band above 0.'))
    if kinds & {'rule', 'observed'} and 'model' in kinds and 'rule_repair_route' not in pipeline:
        findings.append(Finding('ERROR', 'missing-rule-repair-route', pid, 'rule_repair_route',
                                'the cascade has a rule or observed step and a model step, but no `rule_repair_route` '
                                'for items where they disagree.',
                                'route disagreements to a manual resolver that checks the rule first; '
                                'they go to normal review as well.'))
    if pipeline.get('fallback') == 'broader' and not any(c.get('broader') for c in classes.values()):
        findings.append(Finding('ERROR', 'broader-fallback', pid, 'fallback',
                                f'fallback is broader, but scheme {scheme!r} has no `broader` links, so no item '
                                'can fall back to a coarser class.',
                                'use `fallback: unclassified`, or add the hierarchy through knowledge-organization-system.'))

    promoted = False
    for rid in sorted(resolvers):
        res = resolvers[rid]
        side, autonomy, gate = res.get('side_effects'), res.get('autonomy'), res.get('promotion_gate')
        subject = f'{pid}:{rid}'
        if side not in SIDE_EFFECTS or autonomy not in AUTONOMY:
            continue
        gated = needs_gate(side, autonomy)
        promoted = promoted or gated
        missing = []
        if gated and not gate:
            missing.append('a promotion_gate')
        rate = res.get('review_sample_rate')
        if side == 'irreversible' and autonomy == 'auto' and not (is_number(rate) and rate > 0):
            missing.append('review_sample_rate above 0')
        if missing:
            findings.append(Finding('ERROR', 'autonomy-matrix', subject, 'autonomy',
                                    f'side_effects {side} with autonomy {autonomy} requires {" and ".join(missing)}.',
                                    'lower the autonomy, or add what the matrix requires (references/resolvers.md).'))
        if gate and gates is not None and gate not in gates:
            findings.append(Finding('ERROR', 'unknown-gate', subject, 'promotion_gate',
                                    f'promotion_gate {gate!r} is not in the gate registry.',
                                    'add the gate to gates.yaml through evaluation-system, or correct the id.'))
        elif gate and gated:
            status = gates.get(gate) if gates is not None else None
            if status != 'passed':
                state = f'is {status}' if status else 'cannot be read (no gate registry was given)'
                findings.append(Finding('ERROR', 'gate-not-passed', subject, 'promotion_gate',
                                        f'autonomy {autonomy} needs gate {gate!r} passed, but its status {state}.',
                                        'keep the resolver at manual until evaluation-system records the gate as passed.'))
    if vocab is None:
        findings.append(Finding('WARNING', 'peer-absent', pid, 'scheme',
                                'no vocabulary was given, so classes are an inline list and route keys are not checked against a KOS scheme.',
                                'pass --vocabulary with the knowledge-organization-system vocabulary.'))
    if question_sets is None and any(s.get('kind') == 'model' and s.get('question_set') for s in cascade):
        findings.append(Finding('WARNING', 'peer-absent', pid, 'question_set',
                                'no question set was given, so model steps were not checked against decision-questions.',
                                'pass --question-set with each decision-questions question set the cascade names.'))
    if gates is None and any(r.get('promotion_gate') for r in resolvers.values()):
        findings.append(Finding('WARNING', 'peer-absent', pid, 'promotion_gate',
                                'no gate registry was given, so no promotion_gate can count as passed.',
                                'pass --gates with the evaluation-system gates.yaml.'))

    if promoted:
        stage = 3
    elif 'model' in kinds or any(r.get('autonomy') == 'suggest' for r in resolvers.values()):
        stage = 2
    elif kinds & {'rule', 'observed'}:
        stage = 1
    else:
        stage = 0
    return pid, stage, classes, resolvers


def _check_model_steps(pid, cascade, routes, resolvers, question_sets, findings):
    """model-question-set and question-set-role: each model step reads a valid question set whose role
    covers the autonomy of the resolvers it routes to (suggester for suggest or auto)."""
    routed = [resolvers[t].get('autonomy') for t in routes.values() if isinstance(t, str) and t in resolvers]
    highest = max((AUTONOMY.index(a) for a in routed if a in AUTONOMY), default=0)
    needed = 'suggester' if highest > 0 else 'checker'
    for i, step in enumerate(cascade):
        if step.get('kind') != 'model':
            continue
        subject, qid = f'{pid}:cascade[{i}]', step.get('question_set')
        if not qid:
            findings.append(Finding('ERROR', 'model-question-set', subject, 'question_set',
                                    'the model step names no question set.',
                                    'write its question as a decision-questions question set and name it by id.'))
            continue
        if not isinstance(qid, str) or question_sets is None:
            continue
        known = question_sets.get(qid)
        if known is None:
            findings.append(Finding('ERROR', 'model-question-set', subject, 'question_set',
                                    f'question set {qid!r} is not among the --question-set files.',
                                    'pass its file with --question-set, or correct the id.'))
        elif known['problems']:
            findings.append(Finding('ERROR', 'model-question-set', subject, 'question_set',
                                    f'question set {qid!r} fails validate_questions.py '
                                    f'({", ".join(known["problems"])}).',
                                    f'run decision-questions validate_questions.py {known["path"]} and fix it.'))
        else:
            if known['problems'] is None:
                findings.append(Finding('WARNING', 'peer-absent', subject, 'question_set',
                                        f'{VALIDATE_QUESTIONS} is missing, so question set {qid!r} was not validated.',
                                        'install decision-questions beside this skill.'))
            role = known['data'].get('role')
            if role in ROLES and ROLES.index(role) < ROLES.index(needed):
                findings.append(Finding('ERROR', 'question-set-role', subject, 'question_set',
                                        f'question set {qid!r} has role {role}, but it routes to resolvers at autonomy '
                                        f'{AUTONOMY[highest]}, which needs role {needed}.',
                                        'keep those resolvers at manual until decision-questions promotes the set '
                                        'to suggester behind its gates.'))


# ---------------------------------------------------------------- log warnings

def log_warnings(pid, classes, resolvers, records, window, today, max_share, findings):
    start = (today - datetime.timedelta(days=window)).isoformat()
    end = today.isoformat()
    scoped = [r for r in records if r['pipeline_id'] == pid and start <= r['at'][:10] <= end]
    outcomes = item_outcomes(scoped)
    volume = {cid: 0 for cid in classes}
    unclassified = classified = 0
    for entry in outcomes.values():
        if entry['final'] is None:
            continue
        classified += 1
        label = entry['corrected']['corrected_label'] if entry['corrected'] else entry['final']['label']
        if entry['final']['label'] == UNCLASSIFIED:
            unclassified += 1
        if label in volume:
            volume[label] += 1
    for cid in sorted(c for c, n in volume.items() if n == 0):
        findings.append(Finding('WARNING', 'idle-class', f'{pid}:{cid}', 'routes',
                                f'class {cid!r} has no log volume in the {window} days to {end}.',
                                'treat it as a retirement candidate: merge or deprecate it through knowledge-organization-system.'))
    if classified and unclassified / classified > max_share:
        findings.append(Finding('WARNING', 'unclassified-share', pid, 'unclassified_route',
                                f'{unclassified} of {classified} items ({unclassified / classified:.2f}) ended unclassified, above {max_share}.',
                                'run unclassified_report.py and propose the missing classes to knowledge-organization-system.'))
    corrected = {r['resolver_id'] for r in scoped if r['record'] == 'resolution' and r.get('corrected_label')}
    for rid in sorted(r for r, res in resolvers.items() if res.get('autonomy') == 'suggest' and r not in corrected):
        findings.append(Finding('WARNING', 'unreviewed-suggest', f'{pid}:{rid}', 'autonomy',
                                f'resolver {rid!r} suggests, but no correction is recorded in the {window} days to {end}.',
                                'check that a human reviews its suggestions and logs corrected_label on a misroute.'))


# ---------------------------------------------------------------- entry point

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('pipelines', nargs='+', metavar='PIPELINE', help='pipeline YAML file(s)')
    parser.add_argument('--vocabulary', help='knowledge-organization-system vocabulary.yaml')
    parser.add_argument('--gates', help='evaluation-system gates.yaml')
    parser.add_argument('--question-set', action='append', default=[], metavar='FILE', dest='question_sets',
                        help='decision-questions question set a model step names (repeatable)')
    parser.add_argument('--log', action='append', default=[], metavar='FILE', help='JSONL log (repeatable)')
    parser.add_argument('--window-days', type=int, default=30, help='log window for warnings (default 30)')
    parser.add_argument('--max-unclassified-share', type=float, default=0.2,
                        help='warn above this unclassified share (default 0.2)')
    parser.add_argument('--today', help='end of the log window, YYYY-MM-DD (default today)')
    parser.add_argument('--strict', action='store_true', help='exit 1 on warnings too')
    args = parser.parse_args(argv)
    try:
        today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
        vocab = load_vocabulary(args.vocabulary) if args.vocabulary else None
        gates = load_gates(args.gates) if args.gates else None
        question_sets = load_question_sets(args.question_sets, args.gates) if args.question_sets else None
        records, problems = read_log(args.log)
    except (InputError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2
    findings = [Finding('ERROR', 'schema', f'log:{where}', 'record', f'{message}.',
                        'write the record in the shape of templates/log.schema.json.')
                for where, message in problems]
    stages, seen = [], set()
    for path in args.pipelines:
        try:
            docs = load_pipelines(path)
        except OSError as exc:
            print(f'{path}: cannot read: {exc.strerror or exc}', file=sys.stderr)
            return 2
        except yaml.YAMLError as exc:
            findings.append(Finding('ERROR', 'schema', path, '-', f'not valid YAML: {" ".join(str(exc).split())}.',
                                    'fix the YAML syntax.'))
            continue
        if not docs:
            findings.append(Finding('ERROR', 'schema', path, '-', 'the file holds no pipeline.',
                                    'start from templates/pipeline.yaml.'))
        for doc in docs:
            result = validate_pipeline(doc, vocab, gates, findings, question_sets)
            pid, stage = result[0], result[1]
            if pid != '-' and pid in seen:
                findings.append(Finding('ERROR', 'schema', pid, 'id', f'pipeline id {pid!r} is used twice.',
                                        'give each pipeline its own id.'))
            seen.add(pid)
            stages.append((pid, stage))
            if args.log:
                log_warnings(pid, result[2], result[3], records, args.window_days, today,
                             args.max_unclassified_share, findings)
    findings.sort(key=Finding.key)
    errors = sum(f.severity == 'ERROR' for f in findings)
    warnings = len(findings) - errors
    for finding in findings:
        print(finding.line())
    if len(stages) == 1:
        stage_text = f'inferred stage {stages[0][1]}'
    else:
        stage_text = 'inferred stages ' + ', '.join(f'{pid}={stage}' for pid, stage in stages)
    print(f'{", ".join(args.pipelines)}: {errors} error(s), {warnings} warning(s), {stage_text}')
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main())
