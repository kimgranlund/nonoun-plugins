import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'validate_kos.py'
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_kos import ERROR_RULES, WARNING_RULES  # noqa: E402

BRIEF_ERRORS = {'duplicate-preflabel', 'label-collision', 'missing-definition', 'circular-definition',
                'dangling-link', 'broader-cycle', 'unknown-scheme'}


def run(*args):
    return subprocess.run([sys.executable, '-B', str(SCRIPT), *args], cwd=ROOT,
                          capture_output=True, text=True)


def rules(stdout):
    return Counter(m.group(1) for m in re.finditer(r'^(?:ERROR|WARNING) (\S+) ', stdout, re.M))


class ValidateKosTests(unittest.TestCase):
    def test_template_is_clean(self):
        result = run('templates/vocabulary.yaml')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(rules(result.stdout), Counter())
        self.assertIn('inferred stage 0', result.stdout)

    def test_fixture_trips_every_vocabulary_rule_once(self):
        result = run('fixtures/broken.yaml')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(BRIEF_ERRORS <= set(ERROR_RULES))
        self.assertEqual(rules(result.stdout), Counter(ERROR_RULES + ('stage-gate',)))

    def test_fixture_with_corpus_trips_every_rule_once(self):
        result = run('fixtures/broken.yaml', '--corpus', 'fixtures/corpus')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(rules(result.stdout), Counter(ERROR_RULES + WARNING_RULES))
        self.assertIn("retired label 'incidnet' appears at fixtures/corpus/notes.md:7", result.stdout)

    def test_output_is_deterministic(self):
        self.assertEqual(run('fixtures/broken.yaml', '--corpus', 'fixtures/corpus').stdout,
                         run('fixtures/broken.yaml', '--corpus', 'fixtures/corpus').stdout)

    def test_messages_name_concept_field_and_fix(self):
        for line in run('fixtures/broken.yaml').stdout.splitlines()[:-1]:
            self.assertRegex(line, r'^(ERROR|WARNING) \S+ \S+ \S+: .+ Fix: .+')

    def test_warnings_fail_only_under_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.yaml'
            vocab.write_text((ROOT / 'templates' / 'vocabulary.yaml').read_text())
            (Path(tmp) / 'doc.md').write_text('Nothing here uses the seed term.\n')
            self.assertEqual(run(str(vocab), '--corpus', tmp).returncode, 0)
            self.assertEqual(run(str(vocab), '--corpus', tmp, '--strict').returncode, 1)

    def test_deprecated_concept_label_moves_to_hidden_without_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.yaml'
            vocab.write_text(
                'schemes: [{id: main, definition: Docs.}]\n'
                'concepts:\n'
                '  - {id: defect, prefLabel: defect, hiddenLabel: [bug], scheme: main,\n'
                '     definition: Behavior that differs from the agreed specification.}\n'
                '  - {id: bug, prefLabel: bug, deprecated: true, replacedBy: defect, scheme: main,\n'
                '     definition: Former name for a defect.}\n')
            (Path(tmp) / 'doc.md').write_text('Report each defect.\nOne bug remains.\n')
            result = run(str(vocab), '--corpus', str(Path(tmp) / 'doc.md'))
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(rules(result.stdout), Counter({'retired-label-used': 1}))
            self.assertIn("Fix: write 'defect' instead.", result.stdout)

    def test_same_label_in_two_schemes_is_stage_3_not_a_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.yaml'
            vocab.write_text(
                'schemes: [{id: billing, definition: Money.}, {id: ops, definition: Running systems.}]\n'
                'concepts:\n'
                '  - {id: billing-account, prefLabel: account, scheme: billing,\n'
                '     definition: The party invoiced for usage.}\n'
                '  - {id: ops-account, prefLabel: account, scheme: ops,\n'
                '     definition: A login on a production host.}\n')
            result = run(str(vocab))
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(rules(result.stdout), Counter())
            self.assertIn('inferred stage 3', result.stdout)

    def test_missing_scheme_is_unknown_scheme(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.yaml'
            vocab.write_text(
                'schemes: [{id: main, definition: Docs.}]\n'
                'concepts:\n'
                '  - {id: alpha, prefLabel: alpha, definition: The first release channel., scheme: main}\n'
                '  - {id: beta, prefLabel: beta, definition: The second release channel.}\n')
            result = run(str(vocab))
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(result.stderr, '')
            self.assertEqual(rules(result.stdout), Counter({'unknown-scheme': 1}))
            self.assertIn("scheme '(none)'", result.stdout)

    def test_unparseable_file_is_a_schema_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.yaml'
            vocab.write_text('concepts: [\n')
            result = run(str(vocab))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(rules(result.stdout), Counter({'schema': 1}))


if __name__ == '__main__':
    unittest.main()
