"""check.py, refresh_profile.py and package.py: the skill passes its own checks, an empty corpus reports absent layers
without failing, and each layer fails when its artifact is broken (a negative control per layer)."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tool(name, *args, cwd=None):
    return subprocess.run([sys.executable, '-B', str(ROOT / 'scripts' / name), *map(str, args)], capture_output=True, text=True, cwd=cwd)


class Check(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / 'corpus'
        self.dir.mkdir()
        (self.dir / 'ENTRY.md').write_text('# Entry\n\nRead [the policy](policy.md).\n')
        (self.dir / 'policy.md').write_text('# Policy\n\nKeep keyboard navigation.\n')

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, *extra, root=None):
        return tool('check.py', '--root', root or self.dir, *extra)

    def add_profile(self):
        (self.dir / 'profile.json').write_text(json.dumps({'schemaVersion': 1, 'entry': 'ENTRY.md', 'routes': [{'intent': 'read-policy', 'target': 'policy'}],
            'artifacts': [{'id': 'policy', 'location': 'policy.md', 'kind': 'contract', 'summary': 'Keyboard policy', 'revision': '1', 'sha256': ''}]}))
        self.assertEqual(tool('refresh_profile.py', '--root', self.dir, '--profile', self.dir / 'profile.json').returncode, 0)
        (self.dir / 'suite.json').write_text(json.dumps({'version': 1, 'cases': [{'id': 'read-policy', 'intent': 'read-policy',
            'acceptance': {'required': {'policy': ['Keep keyboard navigation.']}}}]}))

    def test_the_skill_passes_every_check_it_has_files_for(self):
        r = self.check('--strict', root=ROOT)
        self.assertEqual(r.returncode, 0, r.stdout)
        for layer in ('vocabulary', 'routing', 'links'):
            self.assertRegex(r.stdout, rf'(?m)^{layer}\s+PASS')
        self.assertIn('route replay 10 of 10 passed', r.stdout)

    def test_a_corpus_with_only_an_entry_reports_absent_layers_and_passes(self):
        r = self.check('--strict')
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(r.stdout.count('not present'), 5)  # four layers and the summary line
        self.assertRegex(r.stdout, r'(?m)^links\s+PASS')

    def test_a_broken_vocabulary_fails_its_layer_only(self):
        (self.dir / 'vocabulary.json').write_text(json.dumps({'schemes': [{'id': 'main', 'definition': 'Docs.'}],
            'concepts': [{'id': 'policy', 'prefLabel': 'policy', 'scheme': 'main'}]}))
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertRegex(r.stdout, r'(?m)^vocabulary\s+FAIL')
        self.assertRegex(r.stdout, r'(?m)^links\s+PASS')
        self.assertIn('missing-definition', r.stdout)

    def test_a_profile_and_suite_are_validated_and_replayed(self):
        self.add_profile()
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('route replay 1 of 1 passed', r.stdout)

    def test_a_profile_with_no_suite_says_the_replay_did_not_run_and_fails_only_under_strict(self):
        self.add_profile()
        self.assertEqual(self.check('--strict').returncode, 0)  # control: with the suite, --strict passes
        (self.dir / 'suite.json').unlink()
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertRegex(r.stdout, r'(?m)^routing\s+PASS\s+profile valid; no suite.json, replay not run$')
        r = self.check('--strict')
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertRegex(r.stdout, r'(?m)^routing\s+FAIL\s+profile valid; no suite.json, replay not run')

    def test_a_required_layer_that_is_not_present_fails(self):
        r = self.check('--require', 'links')
        self.assertEqual(r.returncode, 0, r.stdout)  # control: a required layer that is present passes
        r = self.check('--require', 'vocabulary,routing')
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertRegex(r.stdout, r'(?m)^vocabulary\s+FAIL\s+no vocabulary.json; required by --require')
        self.assertRegex(r.stdout, r'(?m)^routing\s+FAIL')
        self.assertRegex(r.stdout, r'(?m)^statements\s+not present')
        self.assertIn('2 layer(s) failed: vocabulary, routing', r.stdout)
        r = self.check('--require', 'routes')
        self.assertEqual(r.returncode, 2)
        self.assertIn('no layer named routes', r.stderr)

    def test_a_failed_replay_names_the_cases_that_failed(self):
        self.add_profile()
        suite = json.loads((self.dir / 'suite.json').read_text())
        suite['cases'].append({'id': 'read-missing', 'intent': 'read-policy', 'acceptance': {'required': {'policy': ['A sentence the policy does not hold.']}}})
        (self.dir / 'suite.json').write_text(json.dumps(suite))
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn('route replay 1 of 2 passed; failed: read-missing', r.stdout)
        self.assertNotIn('failed: read-policy', r.stdout)

    def test_a_source_edited_after_its_hash_was_recorded_fails_routing_until_refreshed(self):
        self.add_profile()
        (self.dir / 'policy.md').write_text('# Policy\n\nKeep keyboard navigation. Added later.\n')
        self.assertRegex(self.check().stdout, r'(?m)^routing\s+FAIL')
        stale = tool('refresh_profile.py', '--root', self.dir, '--profile', self.dir / 'profile.json', '--check')
        self.assertEqual(stale.returncode, 1)
        self.assertIn('1 stale hash(es): policy', stale.stdout)
        self.assertEqual(tool('refresh_profile.py', '--root', self.dir, '--profile', self.dir / 'profile.json').returncode, 0)
        self.assertRegex(self.check().stdout, r'(?m)^routing\s+PASS')

    def test_a_config_file_names_artifacts_kept_elsewhere(self):
        self.add_profile()
        (self.dir / 'ctx').mkdir()
        shutil.move(str(self.dir / 'profile.json'), str(self.dir / 'ctx' / 'profile.json'))
        shutil.move(str(self.dir / 'suite.json'), str(self.dir / 'ctx' / 'suite.json'))
        self.assertRegex(self.check().stdout, r'(?m)^routing\s+not present')
        (self.dir / 'context-system.json').write_text(json.dumps({'profile': 'ctx/profile.json', 'suite': 'ctx/suite.json'}))
        self.assertRegex(self.check().stdout, r'(?m)^routing\s+PASS')

    def test_the_consumer_package_carries_nothing_that_points_at_what_was_left_out(self):
        out = Path(self.tmp.name) / 'package'
        r = tool('package.py', '--out', out)
        self.assertEqual(r.returncode, 0, r.stdout)
        for gone in ('tests', 'fixtures', 'evals', 'README.md', 'profile.json'):
            self.assertFalse((out / gone).exists(), gone)
        self.assertTrue((out / 'SKILL.md').is_file() and (out / 'scripts' / 'check.py').is_file())

    def test_packaging_fails_when_a_consumer_file_names_an_author_only_path(self):
        copy = Path(self.tmp.name) / 'skill'
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
        with (copy / 'SKILL.md').open('a') as f:
            f.write('\nRun the cases in evals/trigger-activation.suite.yaml.\n')
        r = subprocess.run([sys.executable, '-B', str(copy / 'scripts' / 'package.py'), '--out', str(Path(self.tmp.name) / 'bad')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn('stale-path', r.stdout)


if __name__ == '__main__':
    unittest.main()
