"""check_move.py: a sound move passes before and after; each mutated plan or result fails with its own rule (a negative control per rule)."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'check_move.py'

CORPUS = {
    'README.md': '# Entry\n\n[voice](voice.md) · [notes](context.md)\n',
    'voice.md': '# Voice\n',
    'context.md': '# Background notes\n',
    'old-format.md': '# Retired format\n\nHEADER: x\n',
    'run-01.md': '# Run 1\n',
}
PLAN = {'moves': [{'from': 'voice.md', 'to': 'shared/voice.md'}, {'from': 'context.md', 'to': 'shared/background.md'}],
        'adds': ['CONTEXT.md'], 'removes': []}


class CheckMove(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.before, self.after, self.jobs = self.dir / 'before' / 'corpus', self.dir / 'after' / 'corpus', self.dir / 'jobs'
        for rel, text in CORPUS.items():
            self.write(self.before / rel, text)
        self.write(self.jobs / 'README.md', '# Jobs\n\nNothing here reads another folder.\n')
        self.plan = json.loads(json.dumps(PLAN))

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def apply(self):
        """Make the move the plan describes, soundly: copy everything, place the moved files, remove their sources."""
        shutil.copytree(self.before, self.after)
        for m in self.plan['moves']:
            (self.after / m['to']).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(self.after / m['from']), str(self.after / m['to']))
        for a in self.plan['adds']:
            self.write(self.after / a, '# New\n')
        for r in self.plan['removes']:
            (self.after / r).unlink()

    def run_check(self, *extra, after=False):
        plan = self.dir / 'map.json'
        plan.write_text(json.dumps(self.plan), encoding='utf-8')
        args = ['--before', str(self.before), '--map', str(plan), '--consumers', str(self.jobs), *extra]
        if after:
            args += ['--after', str(self.after)]
        return subprocess.run([sys.executable, '-B', str(SCRIPT), *args], capture_output=True, text=True)

    def assert_rule(self, result, rule, code=1):
        self.assertEqual(result.returncode, code, result.stdout)
        self.assertIn(f' {rule} ', result.stdout)

    def test_sound_move_passes_before_and_after_strict(self):
        self.assertEqual(self.run_check('--strict').returncode, 0)
        self.apply()
        r = self.run_check('--strict', after=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('0 error(s), 0 warning(s)', r.stdout)

    def test_unknown_source(self):
        self.plan['moves'].append({'from': 'Voice.md', 'to': 'shared/v.md'})  # the directory lists voice.md
        self.assert_rule(self.run_check(), 'unknown-source')

    def test_overwrite(self):
        self.plan['adds'].append('README.md')
        self.assert_rule(self.run_check(), 'overwrite')

    def test_case_collision_with_a_file_that_stays(self):
        self.plan['moves'] = [m for m in self.plan['moves'] if m['from'] != 'context.md']  # context.md now stays
        r = self.run_check()
        self.assert_rule(r, 'case-collision')
        self.assertIn('CONTEXT.md', r.stdout)

    def test_case_collision_between_destinations(self):
        self.plan['adds'].append('shared/Voice.md')
        self.assert_rule(self.run_check(), 'case-collision')

    def test_outside_referrer(self):
        self.plan['moves'].append({'from': 'old-format.md', 'to': 'archive/old-format.md'})
        self.assertEqual(self.run_check().returncode, 0)  # nothing outside names it yet
        self.write(self.jobs / 'publish.sh', '#!/bin/sh\nHEADER="$DIR/old-format.md"\n')  # a suffix a prose link check does not read
        r = self.run_check()
        self.assert_rule(r, 'outside-referrer')
        self.assertIn('publish.sh:2', r.stdout)
        self.plan['consumersUpdated'] = ['publish.sh']
        self.assertEqual(self.run_check().returncode, 0)

    def test_outside_reader_is_a_warning(self):
        self.write(self.jobs / 'publish.sh', '#!/bin/sh\nls ../corpus/run-*.md\n')
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn(' outside-reader ', r.stdout)
        self.assert_rule(self.run_check('--strict'), 'outside-reader')

    def test_lost_file(self):
        self.apply()
        (self.after / 'run-01.md').unlink()
        self.assert_rule(self.run_check(after=True), 'lost-file')

    def test_parity(self):
        self.apply()
        self.write(self.after / 'shared/voice.md', '# Voice\n\nchanged\n')
        self.assert_rule(self.run_check(after=True), 'parity')
        self.plan['moves'][0]['edited'] = True
        self.assertEqual(self.run_check(after=True).returncode, 0)

    def test_count_catches_a_write_that_replaced_a_file(self):
        # What a case-folding file system leaves when CONTEXT.md is written while context.md is still there:
        # one file under the old spelling, holding the new text. Built by hand so the test runs on any file system.
        self.plan['moves'] = [m for m in self.plan['moves'] if m['from'] != 'context.md']
        self.apply()
        (self.after / 'CONTEXT.md').unlink()
        self.write(self.after / 'context.md', '# New\n')
        r = self.run_check(after=True)
        self.assert_rule(r, 'count')
        self.assertIn('5 files, expected 6', r.stdout)

    def test_unaccounted_and_not_removed(self):
        self.apply()
        self.write(self.after / 'stray.md', 'x\n')
        self.assert_rule(self.run_check(after=True), 'unaccounted')
        (self.after / 'stray.md').unlink()
        self.write(self.after / 'voice.md', '# Voice\n')
        r = self.run_check(after=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn(' not-removed ', r.stdout)

    def test_unreadable_input_exits_2(self):
        self.assertEqual(subprocess.run([sys.executable, '-B', str(SCRIPT), '--before', str(self.dir / 'none'), '--map', 'x'],
                                        capture_output=True, text=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
