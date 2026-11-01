import json
import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
VALIDATE = SCRIPTS / 'validate_pipeline.py'
TO_CASES = SCRIPTS / 'logs_to_cases.py'
REPORT = SCRIPTS / 'unclassified_report.py'
PEERS = ROOT.parent
VALIDATE_SUITE = PEERS / 'evaluation-system' / 'scripts' / 'validate_suite.py'
VALIDATE_KOS = PEERS / 'knowledge-organization-system' / 'scripts' / 'validate_kos.py'
sys.path.insert(0, str(SCRIPTS))
import validate_pipeline as vp  # noqa: E402
from logs_to_cases import split_for  # noqa: E402

BROKEN = ('fixtures/broken-pipeline.yaml', '--vocabulary', 'fixtures/broken-vocabulary.yaml',
          '--gates', 'fixtures/broken-gates.yaml')
SAMPLE = ('fixtures/sample-log.jsonl', '--pipeline', 'fixtures/sample-pipeline.yaml')
BRIEF_ERRORS = {'unrouted-class', 'unknown-resolver', 'unresolved-route', 'missing-unclassified-route',
                'auto-unclassified', 'no-fallthrough', 'autonomy-matrix', 'unknown-gate', 'gate-not-passed',
                'abstain-range'}


def run(script, *args, cwd=ROOT):
    return subprocess.run([sys.executable, '-B', str(script), *args], cwd=cwd, capture_output=True, text=True)


def rules(stdout):
    return Counter(m.group(1) for m in re.finditer(r'^(?:ERROR|WARNING) (\S+) ', stdout, re.M))


PIPELINE = '''id: p
version: 1
classes: [{id: a, definition: The first kind.}, {id: b, definition: The second kind.}]
scheme: main
cascade: [{classifier_id: desk, kind: human}]
routes: {a: ra, b: rb}
unclassified_route: backlog
resolvers:
  - {id: ra, accepts: [a], output_type: x, side_effects: none, autonomy: manual}
  - {id: backlog, accepts: [unclassified], output_type: x, side_effects: none, autonomy: manual}
'''


def write(folder, name, text):
    path = Path(folder) / name
    path.write_text(text, encoding='utf-8')
    return str(path)


def with_rb(rb, gates=None):
    """The inline pipeline above, with resolver rb as given, validated with an optional gates registry."""
    folder = tempfile.mkdtemp()
    pipeline = write(folder, 'p.yaml', PIPELINE + f'  - {rb}\n')
    args = [pipeline]
    if gates is not None:
        args += ['--gates', write(folder, 'gates.yaml', yaml.safe_dump({'gates': gates}))]
    return run(VALIDATE, *args)


class ValidatePipelineTests(unittest.TestCase):
    def test_template_passes_with_starter_scheme_and_empty_gates(self):
        result = run(VALIDATE, 'templates/pipeline.yaml', '--vocabulary', 'templates/scheme.yaml',
                     '--gates', str(PEERS / 'evaluation-system' / 'templates' / 'gates.yaml'))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(rules(result.stdout), Counter())
        self.assertIn('inferred stage 0', result.stdout)

    @unittest.skipUnless(VALIDATE_KOS.exists(), 'knowledge-organization-system is not installed beside this skill')
    def test_starter_scheme_is_a_valid_kos_vocabulary(self):
        for path in ('templates/scheme.yaml', 'fixtures/sample-vocabulary.yaml'):
            result = run(VALIDATE_KOS, path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_broken_fixture_trips_every_error_rule_but_schema_once(self):
        result = run(VALIDATE, *BROKEN)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(set(vp.ERROR_RULES[1:]), BRIEF_ERRORS)
        self.assertEqual(rules(result.stdout), Counter(vp.ERROR_RULES[1:]))

    def test_output_is_deterministic_and_names_subject_field_and_fix(self):
        first = run(VALIDATE, *BROKEN).stdout
        self.assertEqual(first, run(VALIDATE, *BROKEN).stdout)
        for line in first.splitlines()[:-1]:
            self.assertRegex(line, r'^(ERROR|WARNING) \S+ \S+ \S+: .+ Fix: .+')

    def test_autonomy_matrix_cells(self):
        passed = [{'id': 'g', 'status': 'passed'}]
        cases = [
            ('{id: rb, accepts: [b], output_type: x, side_effects: none, autonomy: suggest}', None, Counter()),
            ('{id: rb, accepts: [b], output_type: x, side_effects: reversible, autonomy: suggest}', None, Counter()),
            ('{id: rb, accepts: [b], output_type: x, side_effects: irreversible, autonomy: manual}', None, Counter()),
            ('{id: rb, accepts: [b], output_type: x, side_effects: none, autonomy: auto, promotion_gate: g}',
             passed, Counter()),
            ('{id: rb, accepts: [b], output_type: x, side_effects: irreversible, autonomy: suggest}', None,
             Counter({'autonomy-matrix': 1})),
            ('{id: rb, accepts: [b], output_type: x, side_effects: irreversible, autonomy: suggest, promotion_gate: g}',
             passed, Counter()),
            ('{id: rb, accepts: [b], output_type: x, side_effects: irreversible, autonomy: auto, promotion_gate: g}',
             passed, Counter({'autonomy-matrix': 1})),
            ('{id: rb, accepts: [b], output_type: x, side_effects: irreversible, autonomy: auto, promotion_gate: g, '
             'review_sample_rate: 0.1}', passed, Counter()),
            ('{id: rb, accepts: [b], output_type: x, side_effects: reversible, autonomy: auto, promotion_gate: g}',
             [{'id': 'g', 'status': 'insufficient_n'}], Counter({'gate-not-passed': 1})),
        ]
        for rb, gates, expected in cases:
            with self.subTest(rb=rb):
                result = with_rb(rb, gates)
                found = rules(result.stdout)
                found.pop('peer-absent', None)
                self.assertEqual(found, expected, result.stdout)

    def test_promoted_stage_and_no_registry_means_no_gate_can_pass(self):
        rb = '{id: rb, accepts: [b], output_type: x, side_effects: none, autonomy: auto, promotion_gate: g}'
        passed = with_rb(rb, [{'id': 'g', 'status': 'passed'}])
        self.assertEqual(passed.returncode, 0, passed.stdout)
        self.assertIn('inferred stage 3', passed.stdout)
        missing = with_rb(rb)
        self.assertEqual(missing.returncode, 1)
        self.assertEqual(rules(missing.stdout), Counter({'gate-not-passed': 1, 'peer-absent': 2}))

    def test_inline_classes_without_vocabulary_warn_peer_absent(self):
        result = with_rb('{id: rb, accepts: [b], output_type: x, side_effects: none, autonomy: manual}')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(rules(result.stdout), Counter({'peer-absent': 1}))

    def test_final_rule_step_can_fall_through_but_final_model_needs_a_threshold(self):
        folder = tempfile.mkdtemp()
        base = PIPELINE + '  - {id: rb, accepts: [b], output_type: x, side_effects: none, autonomy: manual}\n'
        for cascade, expected in [('[{classifier_id: r, kind: rule}]', Counter()),
                                  ('[{classifier_id: m, kind: model, abstain_below: 0.7}]', Counter()),
                                  ('[{classifier_id: m, kind: model, abstain_below: 0}]', Counter({'no-fallthrough': 1}))]:
            with self.subTest(cascade=cascade):
                text = base.replace('[{classifier_id: desk, kind: human}]', cascade)
                found = rules(run(VALIDATE, write(folder, 'p.yaml', text)).stdout)
                found.pop('peer-absent', None)
                self.assertEqual(found, expected)

    def test_unknown_key_and_reserved_route_are_schema_errors(self):
        folder = tempfile.mkdtemp()
        text = PIPELINE.replace('routes: {a: ra, b: rb}', 'routes: {a: ra, b: ra, unclassified: backlog}\nqueue: x')
        result = run(VALIDATE, write(folder, 'p.yaml', text))
        self.assertEqual(rules(result.stdout)['schema'], 2, result.stdout)

    def test_log_warnings(self):
        result = run(VALIDATE, 'fixtures/sample-pipeline.yaml', '--vocabulary', 'fixtures/sample-vocabulary.yaml',
                     '--log', 'fixtures/sample-log.jsonl', '--today', '2026-10-31')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(rules(result.stdout), Counter({'unclassified-share': 1}))
        self.assertIn('6 of 15 items', result.stdout)
        folder = tempfile.mkdtemp()
        text = Path(ROOT / 'fixtures/sample-pipeline.yaml').read_text().replace(
            'accepts: [outage]\n    output_type: an incident record\n    side_effects: none\n    autonomy: manual',
            'accepts: [outage]\n    output_type: an incident record\n    side_effects: none\n    autonomy: suggest')
        vocab = Path(ROOT / 'fixtures/sample-vocabulary.yaml').read_text() + (
            '  - {id: legal-hold, prefLabel: legal hold, definition: A ticket from counsel asking to keep records.,'
            ' scheme: support}\n')
        text = text.replace('  account-access: access-desk\n', '  account-access: access-desk\n  legal-hold: on-call\n')
        result = run(VALIDATE, write(folder, 'p.yaml', text), '--vocabulary', write(folder, 'v.yaml', vocab),
                     '--log', 'fixtures/sample-log.jsonl', '--today', '2026-10-31', '--max-unclassified-share', '0.5',
                     '--strict')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(rules(result.stdout), Counter({'idle-class': 1, 'unreviewed-suggest': 1}))

    def test_malformed_log_record_is_a_schema_error(self):
        folder = tempfile.mkdtemp()
        lines = Path(ROOT / 'fixtures/sample-log.jsonl').read_text().splitlines()[:2]
        record = json.loads(lines[1])
        del record['decided_by']
        record['confidence'] = 0.9
        log = write(folder, 'bad.jsonl', lines[0] + '\n' + json.dumps(record) + '\nnot json\n')
        result = run(VALIDATE, 'fixtures/sample-pipeline.yaml', '--vocabulary', 'fixtures/sample-vocabulary.yaml',
                     '--log', log)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(rules(result.stdout)['schema'], 2, result.stdout)
        self.assertIn('`decided_by` is missing', result.stdout)
        self.assertIn('`confidence` is not a resolution field', result.stdout)
        self.assertEqual(run(TO_CASES, log, '--pipeline', 'fixtures/sample-pipeline.yaml').returncode, 1)

    def test_unreadable_input_exits_2(self):
        self.assertEqual(run(VALIDATE, 'missing.yaml').returncode, 2)
        self.assertEqual(run(VALIDATE, 'templates/pipeline.yaml', '--vocabulary', 'missing.yaml').returncode, 2)
        self.assertEqual(run(REPORT, 'missing.jsonl', '--pipeline', 'fixtures/sample-pipeline.yaml').returncode, 2)

    def test_log_schema_names_the_spine_fields(self):
        schema = json.loads((ROOT / 'templates' / 'log.schema.json').read_text())
        self.assertEqual(set(schema['properties']),
                         set(vp.ENVELOPE_FIELDS + vp.CLASSIFICATION_FIELDS + vp.RESOLUTION_FIELDS))
        self.assertEqual(set(schema['required']), set(vp.ENVELOPE_FIELDS))
        branches = {b['properties']['record']['const']: set(b['required']) for b in schema['oneOf']}
        self.assertEqual(branches, {'classification': set(vp.CLASSIFICATION_REQUIRED),
                                    'resolution': set(vp.RESOLUTION_REQUIRED)})
        self.assertEqual(set(schema['definitions']['Item']['properties']), set(vp.ITEM_FIELDS))


class LogsToCasesTests(unittest.TestCase):
    def suite(self, *extra):
        result = run(TO_CASES, *SAMPLE, *extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        return yaml.safe_load(result.stdout), result

    def test_sample_log_becomes_production_cases(self):
        suite, result = self.suite()
        self.assertEqual(len(Path(ROOT / 'fixtures/sample-log.jsonl').read_text().splitlines()), 30)
        cases = {c['id']: c for c in suite['cases']}
        self.assertEqual(len(cases), 10)
        self.assertIn('left out: 5 unclassified', result.stderr)
        self.assertEqual(cases['case-i-004']['expected'], 'account-access')   # corrected_label wins
        self.assertEqual(cases['case-i-004']['added_because'], 'l-008')
        self.assertEqual(cases['case-i-015']['expected'], 'billing')          # unclassified, then corrected
        self.assertEqual(cases['case-i-001']['added_because'], 'l-001')       # human cascade step
        self.assertEqual(cases['case-i-001']['input']['subject'], 'Charged twice for October')
        for case in cases.values():
            self.assertEqual(case['source'], 'production')
            self.assertEqual(case['split'], split_for(case['id'][len('case-'):], 20))
        self.assertEqual(suite['slices'], ['account-access', 'billing', 'outage'])

    def test_split_is_a_stable_hash(self):
        self.assertEqual(split_for('i-004', 20), 'holdout')
        self.assertEqual(split_for('i-001', 20), 'dev')
        self.assertEqual(split_for('i-001', 100), 'holdout')
        self.assertEqual(split_for('i-004', 0), 'dev')

    def test_human_step_is_matched_by_classifier_id_after_a_step_is_added_in_front(self):
        folder = tempfile.mkdtemp()
        text = Path(ROOT / 'fixtures/sample-pipeline.yaml').read_text().replace(
            'cascade:\n', 'cascade:\n  - {classifier_id: billing-keywords, kind: rule}\n')
        result = run(TO_CASES, 'fixtures/sample-log.jsonl', '--pipeline', write(folder, 'p.yaml', text))
        cases = {c['id']: c for c in yaml.safe_load(result.stdout)['cases']}
        self.assertEqual(cases['case-i-001']['added_because'], 'l-001')

    @unittest.skipUnless(VALIDATE_SUITE.exists(), 'evaluation-system is not installed beside this skill')
    def test_suite_passes_the_evaluation_system_validator(self):
        folder = tempfile.mkdtemp()
        out = str(Path(folder) / 'suite.yaml')
        self.assertEqual(run(TO_CASES, *SAMPLE, '--out', out).returncode, 0)
        for extra in ([], ['--vocabulary', 'fixtures/sample-vocabulary.yaml']):
            result = run(VALIDATE_SUITE, out, *extra)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class UnclassifiedReportTests(unittest.TestCase):
    def test_sample_log_yields_a_candidate_with_evidence_ids(self):
        result = run(REPORT, *SAMPLE, '--vocabulary', 'fixtures/sample-vocabulary.yaml')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('### 1. `data-export` (4 items, rationale tag `data-export`)', result.stdout)
        self.assertIn('Evidence: i-010 (l-019), i-011 (l-021), i-012 (l-023), i-013 (l-025)', result.stdout)
        self.assertIn('| billing | account-access | i-004 (l-008) |', result.stdout)
        self.assertIn('- i-014 (l-027): #feedback', result.stdout)
        self.assertEqual(result.stdout, run(REPORT, *SAMPLE, '--vocabulary', 'fixtures/sample-vocabulary.yaml').stdout)

    def test_min_items_and_keyword_grouping(self):
        self.assertIn('None: no rationale tag', run(REPORT, *SAMPLE, '--min-items', '5').stdout)
        folder = tempfile.mkdtemp()
        records = []
        for n, subject in enumerate(['Invoice archive missing', 'Old invoice archive', 'Archive of receipts']):
            records.append({'log_id': f'l-{n}', 'at': '2026-10-01', 'pipeline_id': 'support-triage',
                            'pipeline_version': 1, 'record': 'classification', 'item_id': f'x-{n}',
                            'item': {'id': f'x-{n}', 'source': 's', 'payload': {'subject': subject},
                                     'received_at': '2026-10-01'},
                            'label': 'unclassified', 'confidence': None, 'rationale': 'unsure',
                            'classifier_id': 'triage-lead', 'cascade_step': 0})
        log = write(folder, 'log.jsonl', ''.join(json.dumps(r) + '\n' for r in records))
        result = run(REPORT, log, '--pipeline', 'fixtures/sample-pipeline.yaml')
        self.assertIn('`archive` (3 items, shared keyword `archive`)', result.stdout)
        self.assertIn('evidence: [l-0, l-1, l-2]', result.stdout)

    def test_candidate_matching_an_existing_concept_is_a_definition_gap(self):
        folder = tempfile.mkdtemp()
        vocab = Path(ROOT / 'fixtures/sample-vocabulary.yaml').read_text() + (
            '  - {id: data-export, prefLabel: data export, definition: Records delivered as a file., scheme: support}\n')
        result = run(REPORT, *SAMPLE, '--vocabulary', write(folder, 'v.yaml', vocab))
        self.assertIn('Matches the existing concept `data-export`', result.stdout)
        self.assertNotIn('Proposed `knowledge-organization-system` change', result.stdout)


class PackagingTests(unittest.TestCase):
    def test_skill_md_is_at_most_300_lines(self):
        self.assertLessEqual(len((ROOT / 'SKILL.md').read_text().splitlines()), 300)

    def test_trigger_suite_has_10_activating_and_5_non_activating_cases(self):
        suite = yaml.safe_load((ROOT / 'evals' / 'trigger-activation.suite.yaml').read_text())
        counts = Counter(c['expected']['activates'] for c in suite['cases'])
        self.assertEqual(counts, Counter({True: 10, False: 5}))
        for case in suite['cases']:
            self.assertEqual(case['tags'], ['should-activate' if case['expected']['activates'] else 'should-not-activate'])

    @unittest.skipUnless(VALIDATE_SUITE.exists(), 'evaluation-system is not installed beside this skill')
    def test_trigger_suite_validates(self):
        result = run(VALIDATE_SUITE, 'evals/trigger-activation.suite.yaml')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
