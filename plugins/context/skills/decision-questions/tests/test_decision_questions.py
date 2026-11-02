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
VALIDATE = SCRIPTS / 'validate_questions.py'
COMPILE = SCRIPTS / 'compile_questions.py'
MAKE_CASES = SCRIPTS / 'make_eval_cases.py'
FIXTURE = ROOT / 'adapters' / 'fixture.py'
PEERS = ROOT.parent
KOS_TEMPLATE = PEERS / 'knowledge-organization-system' / 'templates' / 'vocabulary.yaml'
VALIDATE_KOS = PEERS / 'knowledge-organization-system' / 'scripts' / 'validate_kos.py'
VALIDATE_SUITE = PEERS / 'evaluation-system' / 'scripts' / 'validate_suite.py'
RUN_SUITE = PEERS / 'evaluation-system' / 'scripts' / 'run_suite.py'
LINT_CNL = PEERS / 'controlled-natural-language' / 'scripts' / 'lint_cnl.py'
sys.path.insert(0, str(ROOT / 'adapters'))
import fixture  # noqa: E402

BRIEF_ERRORS = {'threshold-on-proposition', 'compare-incomplete', 'unpinned-model', 'ungated-role',
                'missing-question', 'missing-assemble', 'cnl'}
MODEL = 'example-model-2026-11-01'
TARGET = (f'{sys.executable} -B adapters/fixture.py --recordings fixtures/recorded-answers.yaml '
          '--question-set {qs}')


def run(script, *args, cwd=ROOT):
    return subprocess.run([sys.executable, '-B', str(script), *args], cwd=cwd, capture_output=True, text=True)


def rules(text):
    return Counter(m.group(1) for m in re.finditer(r'^(?:ERROR|WARNING) (\S+) ', text, re.M))


def load(path):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def template():
    return load(ROOT / 'templates' / 'question-set.yaml')


def write(folder, name, data):
    path = Path(folder) / name
    path.write_text(data if isinstance(data, str) else yaml.safe_dump(data, sort_keys=False), encoding='utf-8')
    return str(path)


class ValidateQuestionsTests(unittest.TestCase):
    def test_template_passes_clean(self):
        result = run(VALIDATE, 'templates/question-set.yaml')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(rules(result.stdout), Counter())

    @unittest.skipUnless(LINT_CNL.exists(), 'controlled-natural-language is not installed beside this skill')
    def test_broken_fixture_trips_each_brief_rule_once(self):
        result = run(VALIDATE, 'fixtures/broken-question-set.yaml')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        found = rules(result.stdout)
        self.assertEqual(found, Counter({rule: 1 for rule in BRIEF_ERRORS}), result.stdout)
        messages = [line.split(': ', 1)[1] for line in result.stdout.splitlines() if line.startswith('ERROR')]
        self.assertEqual(len(set(messages)), len(BRIEF_ERRORS))

    def test_suggester_needs_a_passed_gate_pinned_to_the_model(self):
        folder = tempfile.mkdtemp()
        qs = template()
        qs['role'], qs['gate_ids'] = 'suggester', ['g1']
        path = write(folder, 'qs.yaml', qs)
        gate = {'id': 'g1', 'suite_id': 'support-team-cases', 'question_id': 'team', 'metric': 'pass_rate',
                'slice': 'team', 'threshold': 0.9, 'min_n': 100, 'pinned_target_version': MODEL,
                'action': 'preselect the team', 'owner': 'support-ops', 'status': 'passed'}
        passed = write(folder, 'passed.yaml', {'gates': [gate]})
        stale = write(folder, 'stale.yaml', {'gates': [dict(gate, pinned_target_version='example-model-2026-09-01')]})
        other = write(folder, 'other.yaml', {'gates': [dict(gate, question_id='urgency')]})
        self.assertEqual(run(VALIDATE, path, '--gates', passed).returncode, 0)
        for gates in (stale, other, None):
            result = run(VALIDATE, path, *(['--gates', gates] if gates else []))
            self.assertEqual(result.returncode, 1, gates)
            self.assertEqual(rules(result.stdout), Counter({'ungated-role': 1}), result.stdout)

    def test_moving_alias_is_not_a_pin(self):
        folder = tempfile.mkdtemp()
        for alias in ('latest', 'model-latest', 'gpt-*'):
            result = run(VALIDATE, write(folder, 'qs.yaml', dict(template(), model=alias)))
            self.assertEqual(rules(result.stdout), Counter({'unpinned-model': 1}), alias)

    @unittest.skipUnless(LINT_CNL.exists(), 'controlled-natural-language is not installed beside this skill')
    def test_inline_option_text_is_linted_but_kos_text_is_not(self):
        folder = tempfile.mkdtemp()
        qs = template()
        qs['questions'][0]['options']['billing']['definition'] = 'The customer is not asking about an outage.'
        result = run(VALIDATE, write(folder, 'inline.yaml', qs))
        self.assertEqual(rules(result.stdout), Counter({'cnl': 1}), result.stdout)
        self.assertIn('options.billing.definition', result.stdout)
        qs['questions'][0]['options']['billing']['concept_id'] = 'billing'
        self.assertEqual(run(VALIDATE, write(folder, 'kos.yaml', qs)).returncode, 0)

    def test_missing_cnl_peer_is_a_warning(self):
        result = run(VALIDATE, 'templates/question-set.yaml', '--rules', 'no-such-rules.yaml')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(rules(result.stdout), Counter({'peer-absent': 1}))
        self.assertEqual(run(VALIDATE, 'templates/question-set.yaml', '--rules', 'no-such-rules.yaml',
                             '--strict').returncode, 1)

    def test_unreadable_input_exits_2(self):
        self.assertEqual(run(VALIDATE, 'no-such-file.yaml').returncode, 2)


class CompileQuestionsTests(unittest.TestCase):
    @unittest.skipUnless(KOS_TEMPLATE.exists(), 'knowledge-organization-system is not installed beside this skill')
    def test_kos_template_vocabulary_compiles_to_a_valid_set(self):
        out = Path(tempfile.mkdtemp()) / 'compiled.yaml'
        result = run(COMPILE, str(KOS_TEMPLATE), '--template', 'templates/question-set.yaml',
                     '--shape', 'single-choice', '--out', str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        option = load(out)['questions'][0]['options']['example-term']
        self.assertEqual(option['concept_id'], 'example-term')
        self.assertEqual(option['definition'], load(KOS_TEMPLATE)['concepts'][0]['definition'])
        check = run(VALIDATE, str(out), '--vocabulary', str(KOS_TEMPLATE))
        self.assertEqual(check.returncode, 0, check.stdout)

    def test_missing_definition_refuses_and_writes_nothing(self):
        out = Path(tempfile.mkdtemp()) / 'compiled.yaml'
        result = run(COMPILE, 'fixtures/no-definition.vocabulary.yaml', '--template', 'templates/question-set.yaml',
                     '--shape', 'single-choice', '--out', str(out))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(rules(result.stderr), Counter({'missing-definition': 1}), result.stderr)
        self.assertFalse(out.exists())

    def test_excludes_are_copied_verbatim_and_none_comes_from_the_template(self):
        result = run(COMPILE, 'fixtures/support.vocabulary.yaml', '--template', 'templates/question-set.yaml',
                     '--shape', 'single-choice', '--allow-none')
        self.assertEqual(result.returncode, 0, result.stderr)
        options = yaml.safe_load(result.stdout)['questions'][0]['options']
        vocab = {c['id']: c for c in load(ROOT / 'fixtures' / 'support.vocabulary.yaml')['concepts']}
        self.assertEqual(options['account-access']['excludes'], vocab['account-access']['excludes'])
        self.assertNotIn('excludes', options['billing'])
        self.assertEqual(list(options), ['billing', 'outage', 'account-access', 'none'])
        self.assertTrue(options['none']['examples'])

    def test_option_count_none_and_duplicates_are_errors(self):
        folder = tempfile.mkdtemp()
        vocab = load(ROOT / 'fixtures' / 'support.vocabulary.yaml')
        path = write(folder, 'v.yaml', vocab)
        result = run(COMPILE, path, '--template', 'templates/question-set.yaml', '--shape', 'single-choice',
                     '--max-options', '2')
        self.assertEqual(rules(result.stderr), Counter({'too-many-options': 1}), result.stderr)
        self.assertEqual(run(COMPILE, path, '--template', 'templates/question-set.yaml', '--shape',
                             'retrieve-then-choose', '--max-options', '2').returncode, 0)
        bare = template()
        del bare['questions'][0]['options']['none']['examples']
        result = run(COMPILE, path, '--template', write(folder, 't.yaml', bare), '--shape', 'single-choice',
                     '--allow-none')
        self.assertEqual(rules(result.stderr), Counter({'none-without-examples': 1}), result.stderr)
        vocab['concepts'].append(dict(vocab['concepts'][0]))
        result = run(COMPILE, write(folder, 'dup.yaml', vocab), '--template', 'templates/question-set.yaml',
                     '--shape', 'single-choice')
        self.assertEqual(rules(result.stderr), Counter({'duplicate-option': 1}), result.stderr)

    def test_confusion_without_excludes_is_warned(self):
        folder = tempfile.mkdtemp()
        run_json = write(folder, 'run.json', json.dumps({'results': [
            {'case_id': 't13', 'grader_id': 'value-match', 'outcome': 'fail',
             'detail': 'expected "billing", got "account-access"'}]}))
        vocab = load(ROOT / 'fixtures' / 'support.vocabulary.yaml')
        without = write(folder, 'v.yaml', dict(vocab, concepts=[{k: v for k, v in c.items() if k != 'excludes'}
                                                               for c in vocab['concepts']]))
        args = ('--template', 'templates/question-set.yaml', '--shape', 'single-choice', '--run', run_json)
        result = run(COMPILE, without, *args)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(rules(result.stderr), Counter({'unaddressed-confusion': 1}), result.stderr)
        self.assertEqual(rules(run(COMPILE, 'fixtures/support.vocabulary.yaml', *args).stderr), Counter())

    @unittest.skipUnless(VALIDATE_KOS.exists(), 'knowledge-organization-system is not installed beside this skill')
    def test_fixture_vocabularies_are_kos_files(self):
        self.assertEqual(run(VALIDATE_KOS, 'fixtures/support.vocabulary.yaml').returncode, 0)
        result = run(VALIDATE_KOS, 'fixtures/no-definition.vocabulary.yaml')
        self.assertEqual(result.returncode, 1)
        self.assertIn('missing-definition', result.stdout)


class MakeEvalCasesTests(unittest.TestCase):
    def suite(self, question_set, seeds):
        out = Path(tempfile.mkdtemp()) / 'suite.yaml'
        result = run(MAKE_CASES, question_set, '--seeds', seeds, '--out', str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        return out, load(out)

    def test_boundary_pair_suite_has_invariance_negation_and_balance(self):
        out, suite = self.suite('fixtures/needs-human.question-set.yaml', 'fixtures/needs-human.seeds.yaml')
        cases = suite['cases']
        kinds = Counter(c.get('kind', 'standard') for c in cases)
        self.assertEqual(kinds, Counter({'standard': 6, 'invariance': 6, 'negation': 6}))
        self.assertTrue(all(c['basis'] in ('owner', 'judgment') for c in cases))
        ids = {c['id'] for c in cases}
        self.assertTrue(all(c['variant_of'] in ids for c in cases if 'variant_of' in c))
        answers = Counter(c['expected']['answer'] for c in cases if c.get('kind') != 'invariance')
        self.assertEqual(answers[True], answers[False])
        negation = next(c for c in cases if c.get('kind') == 'negation')
        self.assertEqual(negation['input']['question_id'], 'self-serve')
        self.assertIn('needs-human', negation['tags'])
        if VALIDATE_SUITE.exists():
            result = run(VALIDATE_SUITE, str(out))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn('WARNING', result.stdout)

    def test_choice_suite_permutes_options_and_keeps_variants_in_the_base_split(self):
        out, suite = self.suite('templates/question-set.yaml', 'templates/seed-cases.yaml')
        by_id = {c['id']: c for c in suite['cases']}
        perms = [c for c in suite['cases'] if c.get('kind') == 'invariance']
        self.assertEqual(len(perms), 2 * len([c for c in suite['cases'] if 'kind' not in c]))
        for case in perms:
            base = by_id[case['variant_of']]
            self.assertEqual(case['split'], base['split'])
            self.assertEqual(sorted(case['input']['options']), sorted(template()['questions'][0]['options']))
            self.assertEqual(case['expected'], base['expected'])
        self.assertIn('holdout', {c['split'] for c in suite['cases']})
        if VALIDATE_SUITE.exists():
            self.assertEqual(run(VALIDATE_SUITE, str(out)).returncode, 0)

    def test_missing_basis_and_imbalance_refuse(self):
        folder = tempfile.mkdtemp()
        seeds = load(ROOT / 'fixtures' / 'needs-human.seeds.yaml')
        no_basis = [dict(s) for s in seeds]
        del no_basis[0]['basis']
        result = run(MAKE_CASES, 'fixtures/needs-human.question-set.yaml', '--seeds', write(folder, 'a.yaml', no_basis))
        self.assertEqual(result.returncode, 1)
        self.assertIn('basis', result.stderr)
        per_value = dict(load(ROOT / 'fixtures' / 'needs-human.question-set.yaml'), shape='per-value-propositions')
        result = run(MAKE_CASES, write(folder, 'pv.yaml', per_value), '--seeds', write(folder, 'b.yaml', seeds[:4]))
        self.assertEqual(result.returncode, 1)
        self.assertIn('3 true and 1 false', result.stderr)


class FixtureAdapterTests(unittest.TestCase):
    def test_ask_replays_recorded_answers(self):
        model = fixture.FixtureModel(ROOT / 'fixtures' / 'recorded-answers.yaml')
        questions = {q['id']: q for q in template()['questions']}
        reply = model.ask({'id': 't01', 'message': 'I was charged twice for March.'}, questions)
        self.assertEqual(reply['model_version'], MODEL)
        answer = reply['answers']['team']
        self.assertEqual((answer['value'], answer['confidence'], answer['question_id']), ('billing', 0.93, 'team'))
        self.assertAlmostEqual(sum(answer['probabilities'].values()), 1.0, places=5)

    def target(self, question_set, case_input):
        return subprocess.run([sys.executable, '-B', str(FIXTURE), '--recordings', 'fixtures/recorded-answers.yaml',
                               '--question-set', question_set], cwd=ROOT, input=json.dumps(case_input),
                              capture_output=True, text=True)

    def test_target_bands_margins_and_refusals(self):
        low = json.loads(self.target('templates/question-set.yaml',
                                     {'question_id': 'team', 'state': {'id': 't09'}}).stdout)
        self.assertEqual((low['abstain'], low['outcome']), (True, 'defer'))
        tie = json.loads(self.target('fixtures/needs-human.question-set.yaml',
                                     {'question_id': 'needs-human', 'state': {'id': 'h03'}}).stdout)
        self.assertTrue(tie['abstain'])
        yes = json.loads(self.target('fixtures/needs-human.question-set.yaml',
                                     {'question_id': 'needs-human', 'state': {'id': 'h01'}}).stdout)
        self.assertIs(yes['answer'], True)
        self.assertEqual(self.target('templates/question-set.yaml',
                                     {'question_id': 'team', 'state': {'id': 'unrecorded'}}).returncode, 1)
        folder = tempfile.mkdtemp()
        moved = write(folder, 'qs.yaml', dict(template(), model='example-model-2026-12-01'))
        result = self.target(moved, {'question_id': 'team', 'state': {'id': 't01'}})
        self.assertEqual(result.returncode, 1)
        self.assertIn('re-pin', result.stderr)

    @unittest.skipUnless(RUN_SUITE.exists(), 'evaluation-system is not installed beside this skill')
    def test_template_runs_through_run_suite_with_bands_and_coverage(self):
        folder = Path(tempfile.mkdtemp())
        suite = folder / 'suite.yaml'
        self.assertEqual(run(MAKE_CASES, 'templates/question-set.yaml', '--seeds', 'templates/seed-cases.yaml',
                             '--out', str(suite)).returncode, 0)
        result = run(RUN_SUITE, str(suite), '--target', TARGET.format(qs='templates/question-set.yaml'),
                     '--target-version', MODEL, '--out', str(folder / 'run'))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = (folder / 'run' / 'report.md').read_text(encoding='utf-8')
        self.assertIn('## Calibration (dev)', report)
        self.assertIn('Coverage', report)
        metrics = json.loads((folder / 'run' / 'run.json').read_text(encoding='utf-8'))['metrics']['all']
        self.assertLess(metrics['coverage'], 1)


class PackagingTests(unittest.TestCase):
    def test_skill_md_is_short_and_vendor_neutral(self):
        text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertLessEqual(len(text.splitlines()), 300)
        self.assertIsNone(re.search(r'\b(jev|typesafe|system one)\b', text, re.I))

    @unittest.skipUnless(VALIDATE_SUITE.exists(), 'evaluation-system is not installed beside this skill')
    def test_trigger_suite_has_ten_activating_and_five_not(self):
        result = run(VALIDATE_SUITE, 'evals/trigger-activation.suite.yaml')
        self.assertEqual(result.returncode, 0, result.stdout)
        cases = load(ROOT / 'evals' / 'trigger-activation.suite.yaml')['cases']
        self.assertEqual(Counter(c['expected']['activates'] for c in cases), Counter({True: 10, False: 5}))


if __name__ == '__main__':
    unittest.main()
