#!/usr/bin/env python3
"""Deterministic DecisionModel that replays recorded answers, for tests and eval runs without network or cost.

Usage: fixture.py --recordings FILE --question-set FILE [--abstain-below review|act|none]

As a target for evaluation-system's run_suite.py it reads one case input, {question_id, state, options?},
as JSON on stdin and writes one JSON answer on stdout: {value, confidence, probabilities, outcome,
model_version} for a choice or score, {answer, delta, probabilities, model_version} for a proposition,
with abstain: true below the chosen band or within the compare margin. Exit 1 on a missing recording
or a model version other than the question set's pin. Contract: references/model.md.
Standard library plus PyYAML; runs on Python 3.9.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml


class FixtureError(Exception):
    """A recording is missing or does not fit the question; the CLI exits 1."""


def state_key(state):
    """The recording key of a state: its `id`, else a short hash of its canonical JSON."""
    if isinstance(state, dict) and state.get('id') is not None:
        return str(state['id'])
    blob = json.dumps(state, sort_keys=True, separators=(',', ':'), default=str)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:12]


def key_text(key):
    """A recording key as text; YAML reads a bare yes or no as a boolean."""
    return 'yes' if key is True else 'no' if key is False else str(key)


def answer_keys(question):
    """The keys an answer's probabilities range over, in presentation order."""
    if question['kind'] == 'choice':
        return [str(k) for k in question['options']]
    if question['kind'] == 'score':
        return [str(i) for i in range(1, len(question['levels']) + 1)]
    return ['yes', 'no']


class FixtureModel:
    """Implements DecisionModel.ask by replaying a recordings file."""

    def __init__(self, recordings_path):
        data = yaml.safe_load(Path(recordings_path).read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not isinstance(data.get('answers'), list):
            raise FixtureError(f'{recordings_path}: not a recordings file (needs model_version and an answers list)')
        self.model_version = str(data.get('model_version', ''))
        self.recordings = {}
        for row in data['answers']:
            order = tuple(key_text(k) for k in row['order']) if row.get('order') else None
            self.recordings[(str(row['state']), str(row['question']), order)] = row['probabilities']

    def recorded(self, key, question, order):
        for lookup in ((key, question['id'], order), (key, question['id'], None)):
            if lookup in self.recordings:
                return self.recordings[lookup]
        raise FixtureError(f"no recorded answer for state {key!r}, question {question['id']!r}")

    def answer(self, state, question, order=None):
        """One Answer. `order` is the presented option order when it differs from the question's own."""
        keys = answer_keys(question)
        raw = self.recorded(state_key(state), question, tuple(key_text(k) for k in order or keys))
        raw = {key_text(k): float(v) for k, v in raw.items()}
        if question['kind'] == 'proposition':
            yes = raw.get('yes', 0.0)
            return {'question_id': question['id'], 'kind': 'proposition', 'value': yes,
                    'probabilities': {'yes': yes, 'no': round(1 - yes, 6)}, 'model_version': self.model_version}
        probs = {k: raw.get(k, 0.0) for k in keys}
        total = sum(probs.values())
        if total <= 0:
            raise FixtureError(f"recorded probabilities for question {question['id']!r} cover none of its options")
        probs = {k: round(v / total, 6) for k, v in probs.items()}
        best = max(keys, key=lambda k: probs[k])  # ties go to the earlier option, as order effects do
        value = int(best) if question['kind'] == 'score' else best
        return {'question_id': question['id'], 'kind': question['kind'], 'value': value,
                'probabilities': probs, 'confidence': probs[best], 'model_version': self.model_version}

    def ask(self, state, questions):
        """DecisionModel.ask: (state, {id: Question}) -> {answers: {id: Answer}, model_version}."""
        return {'answers': {qid: self.answer(state, q) for qid, q in questions.items()},
                'model_version': self.model_version}


def threshold(decision, confidence, abstain_below):
    """Outcome of a threshold decision, and whether the target abstains at the chosen band."""
    bands = decision['bands']
    outcome = decision['outcome'] if confidence >= bands['act'] else \
        'review' if confidence >= bands['review'] else 'defer'
    floor = {'act': bands['act'], 'review': bands['review'], 'none': 0.0}[abstain_below]
    return outcome, confidence < floor


def partner(question_set, qid):
    """The compare decision a proposition belongs to, and the other proposition in it."""
    for decision in question_set.get('decisions') or []:
        if decision.get('mode') != 'compare':
            continue
        if qid in decision.get('inputs', []):
            return decision, decision.get('rival')
        if decision.get('rival') == qid:
            return decision, decision['inputs'][0]
    return None, None


def respond(model, question_set, case_input, abstain_below='review'):
    """The target face: one case input in, one JSON-ready answer out."""
    if model.model_version != str(question_set.get('model')):
        raise FixtureError(f"recordings answer as model {model.model_version!r}, the question set pins "
                           f"{question_set.get('model')!r}: re-ask, re-run the gates, then re-pin")
    questions = {q['id']: q for q in question_set['questions']}
    qid = case_input.get('question_id')
    if qid not in questions:
        raise FixtureError(f'the question set has no question {qid!r}')
    question = dict(questions[qid])
    order = case_input.get('options')
    if order and question['kind'] == 'choice':
        question['options'] = {k: question['options'][k] for k in order}
    state = case_input.get('state')
    if question['kind'] == 'proposition':
        decision, other = partner(question_set, qid)
        if not decision or other not in questions:
            raise FixtureError(f'proposition {qid!r} has no compare decision: a raw proposition value is never thresholded')
        mine = model.answer(state, question, order)
        theirs = model.answer(state, questions[other])
        delta = round(mine['value'] - theirs['value'], 6)
        out = {'delta': delta, 'probabilities': mine['probabilities'], 'model_version': model.model_version}
        if abs(delta) < decision['margin']:
            return dict(out, abstain=True)
        return dict(out, answer=delta > 0)
    answer = model.answer(state, question)
    out = {'value': answer['value'], 'confidence': answer['confidence'], 'probabilities': answer['probabilities'],
           'model_version': model.model_version}
    for decision in question_set.get('decisions') or []:
        if decision.get('mode') == 'threshold' and decision.get('inputs') == [qid]:
            outcome, abstain = threshold(decision, answer['confidence'], abstain_below)
            out['outcome'] = outcome
            if abstain:
                out['abstain'] = True
            break
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--recordings', required=True, help='recorded answers: {model_version, answers: [...]}')
    parser.add_argument('--question-set', required=True, help='the question set the case inputs refer to')
    parser.add_argument('--abstain-below', choices=('review', 'act', 'none'), default='review',
                        help='abstain below this band of a threshold decision (default review)')
    args = parser.parse_args(argv)
    try:
        model = FixtureModel(args.recordings)
        question_set = yaml.safe_load(Path(args.question_set).read_text(encoding='utf-8'))
        case_input = json.loads(sys.stdin.read())
        if not isinstance(case_input, dict):
            raise FixtureError('the case input is not a JSON object')
        print(json.dumps(respond(model, question_set, case_input, args.abstain_below), sort_keys=True))
    except (FixtureError, OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        print(f'fixture adapter: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
