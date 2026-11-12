"""check_registry.py: the clean fixture passes; each mutated copy fails with its own rule (a negative control per rule)."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'check_registry.py'
FIXTURE = ROOT / 'fixtures' / 'registry'


class CheckRegistry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / 'registry'
        shutil.copytree(FIXTURE, self.dir)
        self.reg = self.dir / 'registry.json'

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, *extra):
        return subprocess.run([sys.executable, '-B', str(SCRIPT), '--registry', str(self.reg), '--manifests',
                               str(self.dir / 'manifests' / '*.json'), '--keep', 'kind,family', *extra],
                              capture_output=True, text=True)

    def edit(self, fn):
        data = json.loads(self.reg.read_text())
        fn(data)
        self.reg.write_text(json.dumps(data))

    def manifest(self, name, data):
        (self.dir / 'manifests' / name).write_text(json.dumps(data))

    def test_clean_fixture_passes(self):
        r = self.run_check('--strict')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(r.stdout.rstrip().endswith('3 manifest(s), 0 error(s), 0 warning(s)'))

    def test_missing_entry(self):
        self.edit(lambda d: d['entries'].pop(0))
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn('ERROR missing-entry button id:', r.stdout)

    def test_orphan_entry(self):
        self.edit(lambda d: d['entries'].append({'id': 'ghost', 'kind': 'control', 'family': 'x', 'path': 'items/button.json'}))
        self.assertIn('ERROR orphan-entry ghost id:', self.run_check().stdout)

    def test_lost_field_missing_and_changed(self):
        def f(d):
            del d['entries'][0]['family']
            d['entries'][1]['kind'] = 'pattern'
        self.edit(f)
        out = self.run_check().stdout
        self.assertIn('ERROR lost-field button family:', out)
        self.assertIn('ERROR lost-field checkbox kind:', out)

    def test_keep_only_checks_named_fields(self):
        self.edit(lambda d: d['entries'][0].pop('status'))
        self.assertEqual(self.run_check().returncode, 0)

    def test_duplicate_and_bad_ids(self):
        self.manifest('copy.manifest.json', {'id': 'button', 'kind': 'control', 'family': 'action'})
        self.manifest('Bad.manifest.json', {'id': 'Bad_Id', 'kind': 'control'})
        out = self.run_check().stdout
        self.assertIn('ERROR duplicate-id button id:', out)
        self.assertIn('ERROR bad-id Bad_Id id:', out)

    def test_duplicate_registry_entry(self):
        self.edit(lambda d: d['entries'].append(dict(d['entries'][0])))
        self.assertIn('ERROR duplicate-id button id: 2 registry entries', self.run_check().stdout)

    def test_warnings_fail_only_when_strict(self):
        def f(d):
            del d['generated']
            d['entries'][0]['path'] = 'items/gone.json'
        self.edit(f)
        r = self.run_check()
        self.assertEqual(r.returncode, 0)
        self.assertIn('WARNING not-generated', r.stdout)
        self.assertIn('WARNING stale-path button path:', r.stdout)
        self.assertEqual(self.run_check('--strict').returncode, 1)

    def test_no_entries_found(self):
        self.reg.write_text(json.dumps({'generated': 'x', 'items': 'none'}))
        self.assertIn('ERROR no-entries', self.run_check().stdout)

    def test_unreadable_registry_exits_2(self):
        self.reg.write_text('{not json')
        self.assertEqual(self.run_check().returncode, 2)

    def test_output_is_deterministic(self):
        self.edit(lambda d: d['entries'].pop(0))
        self.assertEqual(self.run_check().stdout, self.run_check().stdout)


if __name__ == '__main__':
    unittest.main()
