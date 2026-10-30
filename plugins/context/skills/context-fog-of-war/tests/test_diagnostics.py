"""Diagnostic attribution regressions, including the recorded Cueforge failure."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from diagnostics import diagnose, lookup_request, validate_diagnostics


def fixture(command, output, exit_code=1):
    args = json.dumps({'cmd': command})
    call = {'id': 'e0', 'seq': 0, 'kind': 'call', 'exposures': [], 'evidence': {'traceLine': 1, 'text': args}}
    result = {'id': 'e1', 'seq': 1, 'kind': 'result', 'exposures': [], 'evidence': {'traceLine': 2, 'text': output}, 'toolCalls': [{'arguments': args, 'output': json.dumps({'exit_code': exit_code, 'output': output}), 'outcome': 'failed' if exit_code else 'success'}]}
    return {'events': [call, result], 'sources': [], 'links': [{'from': 'e0', 'to': 'e1'}]}


class Diagnostics(unittest.TestCase):
    def findings(self, command, output, exit_code=1):
        data = diagnose(fixture(command, output, exit_code))
        validate_diagnostics(data)
        return [f['detector'] for f in data['diagnostics']['findings']]

    def test_real_lookup(self):
        self.assertEqual(self.findings('cat /tmp/missing.md', 'cat: /tmp/missing.md: No such file or directory'), ['failed-discovery'])

    def test_cueforge_write_build_copy_is_not_discovery(self):
        command = "cat > /tmp/controller.js <<'EOF'\nconst x=1;\nEOF\nnode build.mjs\ncp app.html first-runnable.html"
        self.assertEqual(self.findings(command, 'Error: Unknown UI tokens: --position\ncp: app.html: No such file or directory'), [])

    def test_redirect_write_is_not_read(self):
        self.assertFalse(lookup_request({'cmd': 'cat > controller.js'}))

    def test_compound_failure_not_attributed_to_successful_read(self):
        self.assertEqual(self.findings('cat guide.md; cp absent.html first.html', 'Guidance returned successfully\ncp: absent.html: No such file or directory'), [])

    def test_literal_launcher_lookup(self):
        self.assertTrue(lookup_request({'cmd': 'python3 /kit/scripts/run.py read guide.md --page 1'}))
        self.assertEqual(self.findings('python3 /kit/scripts/run.py component-context.mjs nonexistent', 'Unknown component id: nonexistent'), ['failed-discovery'])

    def test_no_match_and_success_excluded(self):
        self.assertEqual(self.findings('rg unknown guide.md', ''), [])
        self.assertEqual(self.findings('cat guide.md', 'No such file or directory is an example', 0), [])

    def test_words_inside_script_not_lookup(self):
        self.assertFalse(lookup_request({'cmd': "python3 -c 'print(\"cat missing.md\")'"}))

    def test_truncation_independent_of_lookup(self):
        self.assertEqual(self.findings('node check.mjs', 'Warning: truncated output\nFAIL preview advances', 0), ['truncation'])

    def test_claude_character_truncation_in_returned_block(self):
        for content in ('Before\n... [10015 characters truncated] ...\nAfter',
                        [{'type': 'text', 'text': '... [10264 characters truncated] ...'}]):
            with self.subTest(content=content):
                data = fixture('cat guide.md', '', 0)
                data['events'][1]['evidence']['text'] = json.dumps({
                    'block': {'type': 'tool_result', 'content': content}})
                report = diagnose(data)
                signals = [f for f in report['diagnostics']['findings'] if f['detector'] == 'truncation']
                self.assertEqual(len(signals), 1)
                self.assertIn('Downstream harm is unproven', signals[0]['observation'])
                self.assertTrue(signals[0]['metrics']['truncationSites'][0]['location'].startswith('/block/content'))

    def test_claude_truncation_does_not_read_call_arguments(self):
        self.assertEqual(self.findings('echo "[10015 characters truncated]"', 'Complete output', 0), [])
        data = fixture('cat guide.md', '', 0)
        data['events'][1]['evidence']['text'] = json.dumps({
            'block': {'type': 'tool_use', 'input': {'command': '[10015 characters truncated]'}}})
        self.assertEqual(diagnose(data)['diagnostics']['findings'], [])
        self.assertEqual(self.findings('cat guide.md', 'Truncated text is discussed here; no explicit marker', 0), [])


    def test_persisted_preview_envelope(self):
        envelope = '<persisted-output>\nOutput too large (52.7KB). Full output saved to: /tmp/not-opened.txt\n\nPreview (first 2KB):\nSome returned text\n</persisted-output>'
        for content in (envelope, [{'type': 'text', 'text': envelope}]):
            data = fixture('cat guide.md', '', 0)
            data['events'][1]['evidence']['text'] = json.dumps({'block': {'type': 'tool_result', 'content': content}})
            report = diagnose(data)
            signals = [f for f in report['diagnostics']['findings'] if f['detector'] == 'truncation']
            self.assertEqual(len(signals), 1)
            self.assertEqual(signals[0]['metrics']['truncationSites'][0]['marker'].strip(), '<persisted-output>')
            self.assertIn('Downstream harm is unproven', signals[0]['observation'])

    def test_persisted_preview_negative_controls(self):
        envelope = '<persisted-output>\nOutput too large (40.5KB). Full output saved to: /tmp/not-opened.txt\n\nPreview (first 2KB):\nSome text\n</persisted-output>'
        for output in ('All output returned', '<persisted-output>\nFull output saved to: /tmp/output.txt\n</persisted-output>',
                       'Output too large (40.5KB)', 'Documentation example:\n' + envelope,
                       '```text\n' + envelope + '\n```', envelope.replace('Preview (first 2KB):', 'Complete output:')):
            self.assertNotIn('truncation', self.findings('cat guide.md', output, 0))
        self.assertEqual(self.findings('echo ' + envelope, 'Complete output', 0), [])
        data = fixture('cat guide.md', '', 0)
        data['events'][1]['evidence']['text'] = json.dumps({'block': {'type': 'tool_use', 'input': {'command': envelope}}})
        self.assertEqual(diagnose(data)['diagnostics']['findings'], [])

    def test_unknown_wrapped_arguments_remain_unknown(self):
        self.assertFalse(lookup_request('text(await tools.exec_command({cmd: dynamic}));'))

    def test_stderr_redirect_and_pipe_keep_lookup(self):
        self.assertEqual(lookup_request({'cmd': "cat /tmp/task.output 2>/dev/null | grep -v '^$' | head -3; echo live"}), ['/tmp/task.output'])
        self.assertEqual(lookup_request({'cmd': 'cat guide.md 2>&1 | head'}), ['guide.md'])
        self.assertFalse(lookup_request({'cmd': 'cat guide.md 2>/dev/null > copy.md'}))
        self.assertFalse(lookup_request({'cmd': 'cat guide.md 1> copy.md'}))
        self.assertEqual(self.findings('cat /tmp/missing.md 2>&1 | head -3', 'cat: /tmp/missing.md: No such file or directory'), ['failed-discovery'])

    def test_cd_compound_keeps_relative_target(self):
        self.assertEqual(lookup_request({'cmd': "cd /repo/main; sed -n '40,60p;90,130p' scripts/check.mjs"}), ['scripts/check.mjs'])
        self.assertEqual(lookup_request({'cmd': 'cd /repo/main && cat docs/guide.md'}), ['docs/guide.md'])
        self.assertFalse(lookup_request({'cmd': "cd /repo/main && sed -i 's/a/b/' docs/guide.md"}))
        self.assertEqual(self.findings("cd /repo/main; sed -n '1,9p' scripts/check.mjs", 'sed: scripts/check.mjs: No such file or directory'), ['failed-discovery'])

    def test_variable_target_matches_expanded_tail_only(self):
        command = 'S=/kit/scripts; R=$(pwd); ST=$R/.claude/ops/queue.json\npython3 $S/queue.py list --store $ST; ls -la $ST'
        self.assertEqual(self.findings(command, '[]\nls: /work/repo/.claude/ops/queue.json: No such file or directory'), ['failed-discovery'])
        self.assertEqual(self.findings(command, '[]\nls: /work/repo/.claude/ops/other.json: No such file or directory'), [])
        data = diagnose(fixture('ls -la $ST', 'ls: /work/repo/.claude/ops/queue.json: No such file or directory'))
        self.assertEqual(data['diagnostics']['findings'], [])
        row = next(r for r in data['diagnostics']['coverage'] if r['detector'] == 'failed-discovery')
        self.assertIn('Lookup target is an unresolved variable', [g['reason'] for g in row['explanation']['gaps']])


if __name__ == '__main__':
    unittest.main()
