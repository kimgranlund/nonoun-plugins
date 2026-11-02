import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'lint_cnl.py'
KOS = ROOT.parent / 'knowledge-organization-system'
sys.path.insert(0, str(ROOT / 'scripts'))
from lint_cnl import ERROR_RULES, WARNING_RULES  # noqa: E402

BRIEF_ERRORS = {'hidden-label', 'no-pattern', 'unresolved-slot', 'banned-word', 'unknown-concept'}
BRIEF_WARNINGS = {'alt-label', 'no-source'}
FAIL_RUN = ('fixtures/rules.yaml', 'fixtures/vocabulary.yaml', 'fixtures/violations.md')
DQ_RUN = ('templates/decision-question.rules.yaml', 'fixtures/decision-question.vocabulary.yaml')


def run(*args, cwd=ROOT):
    return subprocess.run([sys.executable, '-B', str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True)


def rules(stdout):
    return Counter(m.group(1) for m in re.finditer(r'^(?:ERROR|WARNING) (\S+) ', stdout, re.M))


class LintCnlTests(unittest.TestCase):
    def test_clean_sample_passes_with_template_rules_and_kos_template_vocabulary(self):
        result = run('templates/rules.yaml', str(KOS / 'templates' / 'vocabulary.yaml'), 'fixtures/clean.md')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(rules(result.stdout), Counter())
        self.assertIn('1 governed doc(s)', result.stdout)

    def test_violations_trip_every_rule_once(self):
        result = run(*FAIL_RUN)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(BRIEF_ERRORS <= set(ERROR_RULES) and BRIEF_WARNINGS <= set(WARNING_RULES))
        self.assertEqual(rules(result.stdout), Counter(ERROR_RULES + WARNING_RULES))

    def test_messages_name_file_line_rule_and_fix(self):
        lines = run(*FAIL_RUN).stdout.splitlines()[:-1]
        self.assertEqual(len(lines), len(ERROR_RULES + WARNING_RULES))
        for line in lines:
            self.assertRegex(line, r'^(ERROR|WARNING) [a-z-]+ fixtures/\S+:\d+: .+ Fix: .+')
        self.assertIn("ERROR hidden-label fixtures/violations.md:10:", '\n'.join(lines))
        self.assertIn("Fix: write 'checkout service'.", '\n'.join(lines))

    def test_output_is_deterministic(self):
        self.assertEqual(run(*FAIL_RUN).stdout, run(*FAIL_RUN).stdout)

    def test_fixture_vocabulary_is_valid_kos(self):
        result = subprocess.run([sys.executable, '-B', str(KOS / 'scripts' / 'validate_kos.py'),
                                 str(ROOT / 'fixtures' / 'vocabulary.yaml')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_warnings_fail_only_under_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / 'doc.md'
            doc.write_text('---\ncnl: requirement\n---\nThe checkout shall email a receipt.\n')
            args = ('fixtures/vocabulary.yaml', str(doc))
            rules_file = Path(tmp) / 'rules.yaml'
            rules_file.write_text((ROOT / 'templates' / 'rules.yaml').read_text())
            self.assertEqual(run(str(rules_file), *args).returncode, 0)
            self.assertEqual(run(str(rules_file), *args, '--strict').returncode, 1)

    def test_glob_wrapped_paragraph_code_and_text_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'rules.yaml').write_text((ROOT / 'templates' / 'rules.yaml').read_text())
            (Path(tmp) / 'vocabulary.yaml').write_text((ROOT / 'fixtures' / 'vocabulary.yaml').read_text())
            req = Path(tmp) / 'requirements' / 'pay'
            req.mkdir(parents=True)
            (req / 'checkout.md').write_text(
                '# Checkout\n\n'
                'When a payment fails, the checkout service\nshall show the `cart service` error.\n\n'
                '```\nanything goes in code\n```\n\n'
                '- The checkout service shall retry once for each one of the many many many many many many many '
                'many many many many many many failed payments.\n')
            (Path(tmp) / 'notes.md').write_text('Free prose is not governed.\n')
            result = run('rules.yaml', 'vocabulary.yaml', '.', cwd=tmp)
            self.assertEqual(rules(result.stdout), Counter({'no-pattern': 1}), result.stdout)
            self.assertIn('requirements/pay/checkout.md:10:', result.stdout)
            self.assertIn('limit 20', result.stdout)
            self.assertIn('1 governed doc(s), 3 ungoverned file(s)', result.stdout)

    def test_front_matter_naming_an_undeclared_doc_type_is_a_schema_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / 'doc.md'
            doc.write_text('---\ncnl: runbook\n---\nRestart the service.\n')
            result = run('templates/rules.yaml', 'fixtures/vocabulary.yaml', str(doc))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(rules(result.stdout), Counter({'schema': 1}))

    def test_deprecated_concept_labels_are_retired(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.yaml'
            vocab.write_text(
                'schemes: [{id: main, definition: Docs.}]\n'
                'concepts:\n'
                '  - {id: defect, prefLabel: defect, scheme: main,\n'
                '     definition: Behavior that differs from the agreed specification.}\n'
                '  - {id: bug, prefLabel: bug, deprecated: true, replacedBy: defect, scheme: main,\n'
                '     definition: Former name for a defect.}\n')
            doc = Path(tmp) / 'doc.md'
            doc.write_text('---\ncnl: requirement\n---\nThe defect shall block the release of bugs.\n')
            result = run('templates/rules.yaml', str(vocab), str(doc))
            self.assertEqual(rules(result.stdout), Counter({'hidden-label': 1}), result.stdout)
            self.assertIn("Fix: write 'defect'.", result.stdout)

    def test_decision_question_clean_fixture_passes(self):
        result = run(*DQ_RUN, 'fixtures/decision-question.md')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(rules(result.stdout), Counter())
        self.assertIn('1 governed doc(s)', result.stdout)

    def test_decision_question_violations_name_negation_and_two_propositions(self):
        result = run(*DQ_RUN, 'fixtures/decision-question-violations.md')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(rules(result.stdout), Counter({'banned-word': 4, 'no-pattern': 1, 'unresolved-slot': 1}))
        for expected in ("ERROR banned-word fixtures/decision-question-violations.md:10: banned word 'not'.",
                         "ERROR banned-word fixtures/decision-question-violations.md:11: banned word 'not'.",
                         "ERROR banned-word fixtures/decision-question-violations.md:12: banned word 'and'. "
                         "Fix: One proposition per statement",
                         "ERROR banned-word fixtures/decision-question-violations.md:13: banned word 'more than'."):
            self.assertIn(expected, result.stdout)

    def test_decision_question_rules_stay_out_of_other_doc_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / 'doc.md'
            doc.write_text('---\ncnl: requirement\n---\nThe checkout service shall store each order and refund.\n')
            result = run('templates/rules.yaml', 'fixtures/vocabulary.yaml', str(doc))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_decision_question_fixture_vocabulary_is_valid_kos(self):
        result = subprocess.run([sys.executable, '-B', str(KOS / 'scripts' / 'validate_kos.py'),
                                 str(ROOT / 'fixtures' / 'decision-question.vocabulary.yaml')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unreadable_vocabulary_exits_2(self):
        result = run('templates/rules.yaml', 'fixtures/violations.md')
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
