"""Independent authored replay oracle. No fixture command is ever executed.

Semantics frozen before implementation in evidence batch 0765. Keep this test
self-contained so canonical skill validation does not depend on a project tree.
"""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from diagnostics import diagnose, validate_diagnostics

REQUIRED = 'required-source-before-write'
INCOMPLETE = 'incomplete-source-delivery'
CONTINUATION = 'unfinished-continuation'
EXCLUDED = 'excluded-source-read'
BODY = 'alpha βeta\n'
CONTENT_HASH = hashlib.sha256(BODY.encode()).hexdigest()
IDENTITY = hashlib.sha256(('source-body-v1:' + BODY).encode()).hexdigest()


def citation(event):
    return {'eventId': event['id'], 'traceLine': event['evidence']['traceLine'],
            'excerpt': event['evidence']['text']}


def event(identity, kind, text, exposures=None):
    return {'id': identity, 'kind': kind, 'exposures': exposures or [],
            'evidence': {'traceLine': 1, 'text': text}}


def report():
    declaration = event('declaration', 'message',
                        'Fresh builder requires complete docs/api.md body before writing app/. '
                        'Exclude history/. All source returns through write were observed.')
    result = {'events': [declaration], 'sources': [
        {'id': 'api', 'path': 'docs/api.md'},
        {'id': 'app', 'path': 'app/main.ts'},
        {'id': 'history', 'path': 'history/solution.md'}], 'links': []}
    result['deliveryContract'] = {
        'intent': 'fresh-builder',
        'requiredSources': [{'path': 'docs/api.md', 'contentHash': CONTENT_HASH,
                             'evidence': citation(declaration)}],
        'applicationPaths': ['app/'], 'excludedPaths': ['history/'],
        'sanctionedPaths': [], 'evidence': citation(declaration),
        'observationWindow': {'throughEventId': 'write', 'sourceReturnsComplete': True,
                              'evidence': citation(declaration)}}
    return result


def resequence(data):
    for seq, item in enumerate(data['events']):
        item['seq'] = seq
    return data


def write(data):
    data['events'].append(event('write', 'result', 'Mutation returned: app/main.ts updated.',
                                [{'sourceId': 'app', 'state': 'edited',
                                  'basis': 'Structured mutation result'}]))


def returned(data, name, command, payload, exposures=None):
    args = json.dumps({'cmd': command})
    call = event(name + '-call', 'call', args)
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    outcome = {'exit_code': 0, 'output': raw}
    output = event(name, 'result', json.dumps(outcome, ensure_ascii=False), exposures)
    output['toolCalls'] = [{'arguments': args, 'output': json.dumps(outcome, ensure_ascii=False),
                            'outcome': 'succeeded'}]
    data['events'].extend([call, output])
    data['links'].append({'from': call['id'], 'to': output['id']})


def page(data, name='body', start=0, end=None, identity=IDENTITY, content_hash=CONTENT_HASH):
    end = len(BODY) if end is None else end
    final = end == len(BODY)
    payload = {'kind': 'source-body-page', 'source': 'docs/api.md',
               'sha256': identity, 'contentSha256': content_hash,
               'offset': start, 'end': end, 'total': len(BODY),
               'content': BODY[start:end], 'complete': final,
               'next': None if final else {'args': ['--read', 'docs/api.md', str(end), identity]}}
    returned(data, name, 'node registry.mjs --read docs/api.md', payload)


def fixture_cases():
    cases = []

    def save(name, data, present=(), absent=(), unknown=()):
        cases.append({'name': name, 'data': resequence(data), 'present': list(present),
                      'absent': list(absent), 'unknown': list(unknown)})

    data = report(); write(data)
    save('complete-observation-no-return', data, [REQUIRED])

    data = report()
    returned(data, 'metadata', 'node registry.mjs api', {
        'kind': 'metadata', 'id': 'api', 'source': 'docs/api.md',
        'sha256': IDENTITY, 'contentSha256': CONTENT_HASH,
        'references': ['docs/api.md'], 'complete': True})
    write(data); save('metadata-is-not-body', data, [REQUIRED])

    data = report(); page(data); write(data)
    save('complete-body-before-write', data, absent=[REQUIRED, CONTINUATION])

    data = report()
    data['events'].append(event('request', 'call', json.dumps({'cmd': 'cat docs/api.md'}),
                                [{'sourceId': 'api', 'state': 'requested'}]))
    write(data); save('request-only-complete-observation', data, [REQUIRED])
    data = copy.deepcopy(data); del data['deliveryContract']['observationWindow']
    save('request-only-unknown-observation', data, absent=[REQUIRED], unknown=[REQUIRED])

    data = report(); page(data, end=5); write(data)
    save('skipped-next', data, [REQUIRED, CONTINUATION])

    data = report(); page(data, 'page-one', end=5); page(data, 'page-two', start=5); write(data)
    save('completed-recovery-before-write', data, absent=[REQUIRED, CONTINUATION])

    data = report(); page(data, 'page-one', end=5); write(data); page(data, 'page-two', start=5)
    save('recovery-after-write', data, [REQUIRED, CONTINUATION])

    data = report(); page(data, content_hash=hashlib.sha256(b'other version').hexdigest()); write(data)
    save('wrong-revision', data, [REQUIRED])

    data = report(); page(data, 'page-one', end=5)
    page(data, 'page-two', start=5, identity=hashlib.sha256(b'other identity').hexdigest()); write(data)
    save('different-identity-cannot-close-next', data, [CONTINUATION])

    data = report(); page(data, end=5)
    save('first-write-unknown', data, absent=[REQUIRED], unknown=[REQUIRED])

    data = report(); data['deliveryContract']['requiredSources'] = []; write(data)
    save('requirements-unknown', data, absent=[REQUIRED], unknown=[REQUIRED])

    data = report(); del data['deliveryContract']; write(data)
    save('contract-absent', data, absent=[REQUIRED, EXCLUDED])

    data = report()
    returned(data, 'clipped', 'cat docs/api.md', 'Warning: truncated output\nalpha',
             [{'sourceId': 'api', 'state': 'partial', 'startLine': 1, 'endLine': 1}])
    write(data); save('returned-tool-clipping', data, ['truncation', REQUIRED])

    data = report()
    returned(data, 'head', 'head -n 1 docs/api.md', 'alpha',
             [{'sourceId': 'api', 'state': 'partial', 'startLine': 1, 'endLine': 1}])
    write(data); save('agent-head-limit-not-tool-clipping', data, [REQUIRED], ['truncation'])

    data = report()
    returned(data, 'argument-marker', 'echo "Warning: truncated output"', 'Complete ordinary return')
    write(data); save('request-marker-not-return-clipping', data, absent=['truncation'])

    for name, path, intent, sanctioned, state, has_return, excluded in [
        ('forbidden-fresh-read', 'history/solution.md', 'fresh-builder', [], 'read', True, True),
        ('sibling-prefix', 'history-extra/solution.md', 'fresh-builder', [], 'read', True, False),
        ('sanctioned-example', 'history/examples/guide.md', 'fresh-builder', ['history/examples/'], 'read', True, False),
        ('maintenance-read', 'history/solution.md', 'maintenance', [], 'read', True, False),
        ('intent-unknown', 'history/solution.md', None, [], 'read', True, False),
        ('request-only-excluded-path', 'history/solution.md', 'fresh-builder', [], 'requested', False, False),
        ('mention-is-not-read', 'history/solution.md', 'fresh-builder', [], 'mentioned', True, False),
        ('available-is-not-read', 'history/solution.md', 'fresh-builder', [], 'available', True, False),
    ]:
        data = report(); data['sources'][2]['path'] = path
        data['deliveryContract']['intent'] = intent
        data['deliveryContract']['sanctionedPaths'] = sanctioned
        exposure = [{'sourceId': 'history', 'state': state, 'basis': 'Authored observed exposure'}]
        if has_return:
            returned(data, 'history-read', 'cat ' + path, 'Historical example content', exposure)
        else:
            data['events'].append(event('history-request', 'call', json.dumps({'cmd': 'cat ' + path}), exposure))
        write(data)
        save(name, data, [EXCLUDED] if excluded else [], [] if excluded else [EXCLUDED])

    data = report(); data['deliveryContract']['excludedPaths'] = []
    returned(data, 'history-read', 'cat history/solution.md', 'History content',
             [{'sourceId': 'history', 'state': 'read'}]); write(data)
    save('exclusion-policy-unknown', data, absent=[EXCLUDED])
    return cases


def supplemental_cases():
    """Review-derived regressions added after the original oracle was frozen."""
    cases = []
    for original in fixture_cases():
        if original['name'] in ['agent-head-limit-not-tool-clipping', 'skipped-next']:
            case = copy.deepcopy(original)
            case['name'] += '-incomplete-detector'
            case['present'].append(INCOMPLETE)
            cases.append(case)

    def save(name, data, present=(), absent=()):
        cases.append({'name': name, 'data': resequence(data), 'present': list(present),
                      'absent': list(absent), 'unknown': []})

    data = report(); data['deliveryContract']['requiredSources'] = []
    for index in range(2):
        returned(data, 'metadata-' + str(index), 'node registry.mjs api', {
            'kind': 'metadata-page', 'source': 'docs/api.md', 'sha256': IDENTITY,
            'offset': index, 'end': index + 1, 'total': 2, 'complete': index == 1,
            'next': {'args': ['api', '--cursor', '1', '--hash', IDENTITY]} if index == 0 else None})
    write(data)
    save('complete-metadata-page-recovery', data, absent=[CONTINUATION])

    data = report(); page(data, 'page-one', end=5); page(data, 'page-two', start=5)
    data['deliveryContract']['observationWindow']['throughEventId'] = 'page-two'
    save('no-write-window-includes-through-event', data, absent=[CONTINUATION, REQUIRED])

    data = report(); data['deliveryContract']['requiredSources'] = []
    returned(data, 'excluded-body', 'node registry.mjs --read history/solution.md', {
        'kind': 'source-body-page', 'source': 'history/solution.md', 'sha256': IDENTITY,
        'contentSha256': CONTENT_HASH, 'offset': 0, 'end': len(BODY), 'total': len(BODY),
        'content': BODY, 'complete': True, 'next': None})
    write(data)
    save('excluded-structured-body-return', data, present=[EXCLUDED])
    return cases


class DeliveryOracle(unittest.TestCase):
    def check_cases(self, cases):
        for case in cases:
            with self.subTest(case=case['name']):
                result = diagnose(copy.deepcopy(case['data']))
                validate_diagnostics(result)
                detectors = {finding['detector'] for finding in result['diagnostics']['findings']}
                for detector in case['present']:
                    self.assertIn(detector, detectors)
                for detector in case['absent']:
                    self.assertNotIn(detector, detectors)
                for detector in case['unknown']:
                    row = next(row for row in result['diagnostics']['coverage'] if row['detector'] == detector)
                    self.assertIn(row['explanation']['status'],
                                  ['insufficient-evidence', 'unavailable-telemetry', 'partial'])
                    self.assertTrue(row['explanation']['gaps'])

    def test_authored_replay_oracle(self):
        self.check_cases(fixture_cases())

    def test_review_derived_regressions(self):
        self.check_cases(supplemental_cases())


if __name__ == '__main__':
    unittest.main()
