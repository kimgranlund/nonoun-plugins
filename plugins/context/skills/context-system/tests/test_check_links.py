"""check_links.py: a clean corpus passes; each mutated copy fails with its own rule (a negative control per rule); the skill passes its own check."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'check_links.py'

CLEAN = {
    'ENTRY.md': '# Entry\n\nRead the [guide](references/guide.md). Template: [form](templates/form.md). Tool: scripts/tool.py.\n',
    'references/guide.md': '# Guide\n\nRules are in references/rules.md. Remote: [site](https://example.org/x).\n'
                           'A placeholder: references/<layer>/guide.md.\n\n```\nSee [code](../ENTRY.md).\n```\n',
    'references/rules.md': '# Rules\n\nBack to the [guide](guide.md#top).\n',
    'templates/form.md': '# Form\n',
    'scripts/tool.py': '"""Semantics: references/rules.md."""\n',
    'tests/test_tool.py': '# nothing names this file, and tests are not checked for orphans\n',
}


class CheckLinks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        for rel, text in CLEAN.items():
            p = self.dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, *extra, root=None):
        return subprocess.run([sys.executable, '-B', str(SCRIPT), '--root', str(root or self.dir), *extra],
                              capture_output=True, text=True)

    def edit(self, rel, old, new):
        p = self.dir / rel
        text = p.read_text(encoding='utf-8')
        self.assertIn(old, text)
        p.write_text(text.replace(old, new), encoding='utf-8')

    def assert_rule(self, result, rule, code=1):
        self.assertEqual(result.returncode, code, result.stdout)
        self.assertIn(f' {rule} ', result.stdout)

    def test_clean_corpus_passes_strict(self):
        r = self.run_check('--strict')
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('0 error(s), 0 warning(s)', r.stdout)

    def test_broken_link(self):
        self.edit('ENTRY.md', '(references/guide.md)', '(references/gone.md)')
        self.assert_rule(self.run_check(), 'broken-link')

    def test_stale_path_in_a_docstring(self):
        (self.dir / 'references' / 'rules.md').rename(self.dir / 'references' / 'moved.md')
        self.edit('references/guide.md', 'Rules are in references/rules.md.', 'Rules are in references/moved.md.')
        r = self.run_check()
        self.assert_rule(r, 'stale-path')
        self.assertIn('scripts/tool.py:1', r.stdout)

    def test_example_link_warns_and_fails_only_when_strict(self):
        self.edit('references/guide.md', '(../ENTRY.md)', '(./src/review.ts)')
        r = self.run_check()
        self.assert_rule(r, 'example-link', code=0)
        self.assertEqual(self.run_check('--strict').returncode, 1)

    def test_unreferenced_file_warns(self):
        (self.dir / 'templates' / 'orphan.md').write_text('# Orphan\n', encoding='utf-8')
        r = self.run_check()
        self.assert_rule(r, 'unreferenced', code=0)
        self.assertIn('templates/orphan.md', r.stdout)

    def test_a_markdown_file_at_the_root_that_nothing_names_warns(self):
        self.assertNotIn(' unreferenced ', self.run_check().stdout)  # control: the clean corpus has none
        (self.dir / 'notes.md').write_text('# Notes\n', encoding='utf-8')
        r = self.run_check()
        self.assert_rule(r, 'unreferenced', code=0)
        self.assertIn('WARNING unreferenced notes.md', r.stdout)
        self.assertIn('check_move.py --consumers', r.stdout)
        self.assertEqual(self.run_check('--strict').returncode, 1)
        self.assertNotIn(' unreferenced ', self.run_check('--orphans', 'templates').stdout)  # the root was not asked for
        self.assertIn('unreferenced notes.md', self.run_check('--orphans', '.').stdout)
        entry = next(p for p in self.dir.iterdir() if p.is_file() and p.suffix == '.md' and p.name != 'notes.md')
        entry.write_text(entry.read_text(encoding='utf-8') + '\nSee notes.md.\n', encoding='utf-8')
        self.assertNotIn(' unreferenced ', self.run_check().stdout)  # named: no longer reported

    def test_a_root_file_that_names_another_file_may_be_an_entry_and_is_not_reported(self):
        (self.dir / 'START.md').write_text('# Start\n\nRead references/guide.md.\n', encoding='utf-8')
        self.assertNotIn(' unreferenced ', self.run_check().stdout)
        (self.dir / 'README.md').write_text('# Readme\n', encoding='utf-8')  # control: with a known entry, it is reported
        self.assertIn('unreferenced START.md', self.run_check().stdout)
        (self.dir / 'README.md').unlink()
        (self.dir / 'START.md').write_text('# Start\n', encoding='utf-8')  # control: naming nothing, it is reported
        self.assertIn('unreferenced START.md', self.run_check().stdout)

    def test_entry_files_and_other_kinds_at_the_root_are_not_reported(self):
        for name in ('AGENTS.md', 'CLAUDE.md', 'README.md', 'LICENSE.md', 'Makefile', 'settings.json'):
            if not (self.dir / name).exists():
                (self.dir / name).write_text('x\n', encoding='utf-8')
        self.assertNotIn(' unreferenced ', self.run_check().stdout)

    def test_unreadable_root_exits_2(self):
        self.assertEqual(self.run_check(root=self.dir / 'nowhere').returncode, 2)

    def test_the_skill_passes_its_own_check(self):
        r = self.run_check('--strict', root=ROOT)
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == '__main__':
    unittest.main()
