import json
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

try:
    import yaml  # noqa: F401
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

BRIEF_ERRORS = {'duplicate-preflabel', 'label-collision', 'missing-definition', 'circular-definition',
                'dangling-link', 'broader-cycle', 'unknown-scheme'}


SCHEME = {'id': 'main', 'definition': 'Docs.'}


def concept(cid, definition, scheme='main', **more):
    return dict({'id': cid, 'prefLabel': cid, 'definition': definition}, **({'scheme': scheme} if scheme else {}), **more)


def write(path, schemes, concepts):
    path.write_text(json.dumps({'schemes': schemes, 'concepts': concepts}, indent=2))


def run(*args):
    return subprocess.run([sys.executable, '-B', str(SCRIPT), *args], cwd=ROOT,
                          capture_output=True, text=True)


def rules(stdout):
    return Counter(m.group(1) for m in re.finditer(r'^(?:ERROR|WARNING) (\S+) ', stdout, re.M))


class ValidateKosTests(unittest.TestCase):
    def test_template_is_clean(self):
        result = run('templates/vocabulary.json')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(rules(result.stdout), Counter())
        self.assertIn('inferred stage 0', result.stdout)

    def test_fixture_trips_every_vocabulary_rule_once(self):
        result = run('fixtures/broken.json')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(BRIEF_ERRORS <= set(ERROR_RULES))
        self.assertEqual(rules(result.stdout), Counter(ERROR_RULES + ('stage-gate',)))

    def test_fixture_with_corpus_trips_every_rule_once(self):
        result = run('fixtures/broken.json', '--corpus', 'fixtures/corpus')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(rules(result.stdout), Counter(ERROR_RULES + WARNING_RULES))
        self.assertIn("retired label 'incidnet' appears at fixtures/corpus/notes.md:7", result.stdout)

    def test_output_is_deterministic(self):
        self.assertEqual(run('fixtures/broken.json', '--corpus', 'fixtures/corpus').stdout,
                         run('fixtures/broken.json', '--corpus', 'fixtures/corpus').stdout)

    def test_messages_name_concept_field_and_fix(self):
        for line in run('fixtures/broken.json').stdout.splitlines()[:-1]:
            self.assertRegex(line, r'^(ERROR|WARNING) \S+ \S+ \S+: .+ Fix: .+')

    def test_warnings_fail_only_under_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.json'
            vocab.write_text((ROOT / 'templates' / 'vocabulary.json').read_text())
            (Path(tmp) / 'doc.md').write_text('Nothing here uses the seed term.\n')
            self.assertEqual(run(str(vocab), '--corpus', tmp).returncode, 0)
            self.assertEqual(run(str(vocab), '--corpus', tmp, '--strict').returncode, 1)

    def test_deprecated_concept_label_moves_to_hidden_without_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.json'
            write(vocab, [SCHEME], [concept('defect', 'Behavior that differs from the agreed specification.', hiddenLabel=['bug']),
                                    concept('bug', 'Former name for a defect.', deprecated=True, replacedBy='defect')])
            (Path(tmp) / 'doc.md').write_text('Report each defect.\nOne bug remains.\n')
            result = run(str(vocab), '--corpus', str(Path(tmp) / 'doc.md'))
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(rules(result.stdout), Counter({'retired-label-used': 1}))
            self.assertIn("Fix: write 'defect' instead.", result.stdout)

    def test_same_label_in_two_schemes_is_stage_3_not_a_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.json'
            write(vocab, [{'id': 'billing', 'definition': 'Money.'}, {'id': 'ops', 'definition': 'Running systems.'}],
                  [dict(concept('billing-account', 'The party invoiced for usage.', scheme='billing'), prefLabel='account'),
                   dict(concept('ops-account', 'A login on a production host.', scheme='ops'), prefLabel='account')])
            result = run(str(vocab))
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(rules(result.stdout), Counter())
            self.assertIn('inferred stage 3', result.stdout)

    def test_missing_scheme_is_unknown_scheme(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.json'
            write(vocab, [SCHEME], [concept('alpha', 'The first release channel.'), concept('beta', 'The second release channel.', scheme=None)])
            result = run(str(vocab))
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(result.stderr, '')
            self.assertEqual(rules(result.stdout), Counter({'unknown-scheme': 1}))
            self.assertIn("scheme '(none)'", result.stdout)

    def test_fixture_reports_each_excludes_error_once(self):
        stdout = run('fixtures/broken.json').stdout
        self.assertIn("ERROR excludes-neighbor outage-report excludes: neighbor 'on-call-shift' is not a concept id.", stdout)
        self.assertIn("ERROR excludes-statement outage-report excludes: the entry for neighbor 'incident' has an empty statement.", stdout)

    def test_excludes_entries(self):
        alert = concept('alert', 'A machine signal that a threshold was crossed.')
        cases = [
            ({'neighbor': 'alert', 'statement': 'Not every alert; one incident may raise many.'}, Counter()),
            ({'neighbor': 'incident', 'statement': 'Not an alert.'}, Counter({'excludes-statement': 1})),
            ({'neighbor': 'alert', 'statement': 'The incident.'}, Counter({'excludes-statement': 1})),
            ({'neighbor': 'alert'}, Counter({'excludes-statement': 1})),
            ({'neighbor': 'alert', 'statement': 'Not an alert.', 'why': 'eval'}, Counter({'schema': 1})),
            ('alert', Counter({'schema': 1})),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.json'
            for entry, expected in cases:
                write(vocab, [SCHEME], [alert, concept('incident', 'An interruption someone must respond to.', excludes=[entry])])
                result = run(str(vocab))
                self.assertEqual(rules(result.stdout), expected, str(entry) + result.stdout)
                self.assertEqual(result.returncode, 1 if expected else 0, str(entry))
                if not expected:
                    self.assertIn('inferred stage 0', result.stdout)

    def test_unparseable_file_is_a_schema_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.json'
            vocab.write_text('{"concepts": [\n')
            result = run(str(vocab))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(rules(result.stdout), Counter({'schema': 1}))

    def test_dollar_keys_are_notes_and_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            vocab = Path(tmp) / 'vocabulary.json'
            vocab.write_text(json.dumps({'$comment': ['a note'], 'schemes': [SCHEME], 'concepts': [concept('alpha', 'The first release channel.')]}))
            self.assertEqual(rules(run(str(vocab)).stdout), Counter())


@unittest.skipUnless(HAS_YAML, 'PyYAML is not installed: the earlier YAML format cannot be read here')
class EarlierYamlFormat(unittest.TestCase):
    def test_a_yaml_vocabulary_is_still_read(self):
        result = run('fixtures/yaml/vocabulary.yaml')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


@unittest.skipIf(HAS_YAML, 'PyYAML is installed, so the missing-dependency message cannot be shown')
class YamlWithoutPyYaml(unittest.TestCase):
    def test_a_yaml_vocabulary_names_the_way_out(self):
        result = run('fixtures/yaml/vocabulary.yaml')
        self.assertEqual(result.returncode, 1)
        self.assertIn('PyYAML is not installed', result.stdout)
        self.assertIn('rewrite the file as JSON', result.stdout)


if __name__ == '__main__':
    unittest.main()
