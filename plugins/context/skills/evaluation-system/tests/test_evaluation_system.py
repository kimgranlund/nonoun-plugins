import json
import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / 'scripts' / 'validate_suite.py'
RUN = ROOT / 'scripts' / 'run_suite.py'
ECHO = f'{sys.executable} {ROOT / "scripts" / "echo_target.py"}'
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_suite import ERROR_RULES, WARNING_RULES  # noqa: E402
from run_suite import wilson  # noqa: E402

BRIEF_ERRORS = {'duplicate-case-id', 'missing-evidence', 'unknown-grader', 'gate-reference',
                'unvalidated-grader', 'holdout-in-tuning', 'unresolved-label'}
BROKEN = ('fixtures/broken-suite.yaml', '--gates', 'fixtures/gates.yaml', '--vocabulary', 'fixtures/vocabulary.yaml',
          '--tune', 'fixtures/tune.yaml')


def run(script, *args, cwd=ROOT):
    return subprocess.run([sys.executable, '-B', str(script), *args], cwd=cwd, capture_output=True, text=True)


def rules(stdout):
    return Counter(m.group(1) for m in re.finditer(r'^(?:ERROR|WARNING) (\S+) ', stdout, re.M))


def write_suite(folder, cases, slices='[]'):
    path = Path(folder) / 'suite.yaml'
    path.write_text('id: s\nversion: 1\ntarget: t\ntarget_spec: The target shall echo.\n'
                    f'graders: [{{id: g, kind: exact}}]\nslices: {slices}\ncases:\n' + cases)
    return path


class ValidateSuiteTests(unittest.TestCase):
    def test_template_is_clean_stage_0(self):
        result = run(VALIDATE, 'templates/suite.yaml')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(rules(result.stdout), Counter())
        self.assertIn('inferred stage 0', result.stdout)

    def test_template_gates_registry_is_valid_and_empty(self):
        result = run(VALIDATE, 'templates/suite.yaml', '--gates', 'templates/gates.yaml')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('inferred stage 0', result.stdout)

    def test_own_trigger_suite_is_valid(self):
        result = run(VALIDATE, 'evals/trigger-activation.suite.yaml')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fixture_trips_every_rule_but_schema_once(self):
        result = run(VALIDATE, *BROKEN)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(BRIEF_ERRORS <= set(ERROR_RULES))
        self.assertEqual(rules(result.stdout), Counter(ERROR_RULES[1:] + WARNING_RULES))

    def test_output_is_deterministic_and_names_subject_field_and_fix(self):
        first = run(VALIDATE, *BROKEN, '--today', '2026-11-01').stdout
        self.assertEqual(first, run(VALIDATE, *BROKEN, '--today', '2026-11-01').stdout)
        for line in first.splitlines()[:-1]:
            self.assertRegex(line, r'^(ERROR|WARNING) \S+ \S+ \S+: .+ Fix: .+')

    def test_gate_naming_an_unvalidated_suite_is_a_reference_error(self):
        result = run(VALIDATE, 'templates/suite.yaml', '--gates', 'fixtures/gates.yaml')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(rules(result.stdout), Counter({'gate-reference': 3}))

    def test_unreadable_input_exits_2(self):
        self.assertEqual(run(VALIDATE, 'missing.yaml').returncode, 2)


class RunSuiteTests(unittest.TestCase):
    def test_wilson_interval(self):
        self.assertEqual(wilson(8, 10), [0.4902, 0.9433])
        self.assertEqual(wilson(0, 3), [0.0, 0.5615])
        self.assertIsNone(wilson(0, 0))

    def test_template_against_echo_target_reports_intervals_and_insufficient_n(self):
        with tempfile.TemporaryDirectory() as out:
            result = run(RUN, 'templates/suite.yaml', '--target', ECHO, '--gates', 'fixtures/template-gates.yaml',
                         '--out', out)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads((Path(out) / 'run.json').read_text())
            self.assertEqual(data['metrics']['all'], {'value': 0.0, 'n': 3, 'interval': [0.0, 0.5615], 'passes': 0})
            self.assertEqual([g['status'] for g in data['gates']], ['insufficient_n'])
            self.assertTrue({'id', 'suite_id', 'suite_version', 'target_version', 'started_at', 'results',
                             'metrics'} <= set(data))
            report = (Path(out) / 'report.md').read_text()
            self.assertIn('| all | 3 | 0 | 0.00 | 0.00 to 0.56 |', report)
            self.assertIn('`insufficient_n`', report)
            self.assertEqual(run(RUN, 'templates/suite.yaml', '--target', ECHO, '--gates', 'fixtures/template-gates.yaml',
                                 '--out', out, '--strict').returncode, 1)

    def test_failed_gate_exits_1_and_passing_slice_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            suite = write_suite(tmp, '  - {id: a, input: x, expected: x, tags: [k], source: production, added_because: log 1}\n'
                                     '  - {id: b, input: y, expected: z, tags: [k], source: production, added_because: log 2}\n',
                                slices='[k]')
            gates = Path(tmp) / 'gates.yaml'
            gates.write_text('gates:\n  - {id: g1, suite_id: s, metric: pass_rate, slice: k, threshold: 0.9, min_n: 2,'
                             ' action: ship, owner: me}\n')
            result = run(RUN, str(suite), '--target', ECHO, '--gates', str(gates), '--out', tmp)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            data = json.loads((Path(tmp) / 'run.json').read_text())
            self.assertEqual(data['metrics']['k']['passes'], 1)
            self.assertEqual(data['gates'][0]['status'], 'failed')

    def test_holdout_with_tune_is_refused_and_holdout_runs_are_logged(self):
        with tempfile.TemporaryDirectory() as tmp:
            suite = write_suite(tmp, '  - {id: a, input: x, expected: x, source: production, added_because: log 1, split: holdout}\n')
            tune = Path(tmp) / 'tune.yaml'
            tune.write_text('cases: []\n')
            refused = run(RUN, str(suite), '--target', ECHO, '--split', 'holdout', '--tune', str(tune), '--out', tmp)
            self.assertEqual(refused.returncode, 2)
            self.assertIn('refused', refused.stderr)
            self.assertEqual(run(RUN, str(suite), '--target', ECHO, '--split', 'holdout', '--out', tmp).returncode, 0)
            self.assertEqual(len((Path(tmp) / 'holdout-runs.jsonl').read_text().splitlines()), 1)

    def test_suite_with_validation_errors_is_refused(self):
        with tempfile.TemporaryDirectory() as out:
            result = run(RUN, 'fixtures/broken-suite.yaml', '--target', ECHO, '--out', out)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((Path(out) / 'run.json').exists())

    def test_human_suite_runs_without_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            graded = Path(tmp) / 'human.yaml'
            graded.write_text('- {case_id: a1, grader_id: observed-activation, outcome: pass}\n'
                              '- {case_id: n1, grader_id: observed-activation, outcome: fail, detail: activated}\n')
            result = run(RUN, 'evals/trigger-activation.suite.yaml', '--human-results', str(graded), '--out', tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            metrics = json.loads((Path(tmp) / 'run.json').read_text())['metrics']
            self.assertEqual((metrics['all']['n'], metrics['all']['passes']), (2, 1))


if __name__ == '__main__':
    unittest.main()
