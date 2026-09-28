#!/usr/bin/env python3
"""Cross-host readiness, routing, cancellation, and preserved retry evidence; no model calls."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

import readiness
import run_lifecycle
import codex_exchange

spec = importlib.util.spec_from_file_location('codex_test', Path(__file__).with_name('codex-selftest.py'))
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)

CLAUDE = '''#!/usr/bin/env python3
import json, os, time
if os.environ.get('MODE') == 'timeout': time.sleep(60)
print(json.dumps(dict(type='result',is_error=False,result='## Map\\nseed.txt',total_cost_usd=0,duration_ms=1,num_turns=1)))
'''


class LifecycleTests(fixture.CodexTests):
    # Reuse only fixture methods, not the inherited test suite.
    def test_readiness_controls(self):
        result = readiness.inspect(self.repo, 'claude')
        self.assertTrue(result['ready'], result)
        with patch('readiness.shutil.which', return_value=None):
            self.assertFalse(readiness.inspect(self.repo, 'claude')['ready'])
        self.assertFalse(readiness.inspect(self.base, 'codex')['ready'])
        self.assertFalse(readiness.inspect(self.repo, 'codex', 'subagent')['ready'])
        fixture.codex_roles.install(self.repo)
        self.assertTrue(readiness.inspect(self.repo, 'codex', 'subagent')['ready'])
        target = self.repo/'.codex/agents/sdlc-scout-l1.toml'
        target.write_text(target.read_text()+'# local edit\n')
        self.assertFalse(readiness.inspect(self.repo, 'codex', 'subagent')['ready'])

    def test_both_hosts_cancel_lock_retry_and_routing(self):
        (self.bin/'claude').write_text(CLAUDE)
        for backend in ('claude', 'codex'):
            directory = self.repo/backend
            directory.mkdir()
            handoff = directory/'handoff.md'
            handoff.write_text('## Goal\nMap seed.txt\n')
            env = dict(self.env, SDLC_BACKEND=backend, MODE='timeout', SDLC_ROUTING_REASON='Small repository lookup; scout L1 suffices.')
            cmd = ['bash',str(fixture.ROOT/'scripts/run.sh'),'scout','L1',str(handoff)]
            proc = subprocess.Popen(cmd,cwd=self.repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                deadline = time.monotonic()+10
                while not (directory/'scout-L1.running').exists() and time.monotonic()<deadline:
                    time.sleep(.05)
                self.assertTrue((directory/'scout-L1.running').exists())
                duplicate = subprocess.run(cmd,cwd=self.repo,env=env,capture_output=True,text=True,timeout=10)
                self.assertEqual(duplicate.returncode,2,duplicate.stderr)
                self.assertIn('still owns',duplicate.stderr)
                with self.assertRaisesRegex(ValueError,'still owns'):
                    run_lifecycle.recover(directory)
                proc.send_signal(signal.SIGTERM)
                proc.communicate(timeout=15)
                record = json.loads((directory/'scout-L1.attempt.json').read_text())
                self.assertEqual(record['status'],'interrupted')
                self.assertEqual(record['exit_code'],143)
                env['MODE']='pass'
                retry = subprocess.run(cmd,cwd=self.repo,env=env,capture_output=True,text=True,timeout=20)
                self.assertEqual(retry.returncode,0,retry.stderr)
                latest = json.loads((directory/'scout-L1-2.attempt.json').read_text())
                self.assertEqual(latest['status'],'completed')
                row = json.loads((directory/'runs.jsonl').read_text().splitlines()[-1])
                self.assertEqual(row['attempt_id'],latest['attempt_id'])
                self.assertEqual(row['routing_reason'],env['SDLC_ROUTING_REASON'])
                self.assertNotEqual(record['attempt_id'],latest['attempt_id'])
                self.assertFalse(list(directory.glob('*.running')))
            finally:
                if proc.poll() is None:
                    proc.terminate();proc.communicate(timeout=15)

    def test_recovery_preserves_evidence_and_rejects_late_native_report(self):
        path = self.step/'scout-L1.attempt.json'
        path.write_text(json.dumps(dict(role='scout',level='L1',status='running',attempt_id='old')))
        log = self.step/'scout-L1.log';log.write_text('preserved evidence')
        self.assertEqual(run_lifecycle.recover(self.step),[path.name])
        self.assertEqual(json.loads(path.read_text())['status'],'interrupted')
        self.assertEqual(log.read_text(),'preserved evidence')
        request = self.step/'scout-L1.request.json'
        request.write_text(json.dumps(dict(status='waiting', owner_pid=os.getpid(),owner_identity='wrong process identity', response_path=str(request.with_suffix('.response.json')),request_id='old')))
        report = self.step/'report.md';report.write_text('## Map\nold report')
        with self.assertRaisesRegex(ValueError,'owner is gone'):
            codex_exchange.respond(request,report)
        self.assertFalse(request.with_suffix('.response.json').exists())

    def test_sigkill_recovers_claude_but_codex_native_refuses(self):
        (self.bin/'claude').write_text(CLAUDE)
        directory = self.repo/'killed'
        directory.mkdir()
        handoff = directory/'handoff.md'
        handoff.write_text('## Goal\nMap seed.txt\n')
        command = ['bash', str(fixture.ROOT/'scripts/run.sh'), 'scout', 'L1', str(handoff)]
        env = dict(self.env, SDLC_BACKEND='claude', MODE='timeout')
        owner = subprocess.Popen(command, cwd=self.repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        child_pid = None
        try:
            path = directory/'scout-L1.attempt.json'
            deadline = time.monotonic()+10
            while time.monotonic()<deadline:
                if path.exists():
                    record = json.loads(path.read_text())
                    child_pid = record.get('process_pid')
                    if child_pid and (directory/'scout-L1.running').exists():
                        break
                time.sleep(.05)
            self.assertIsNotNone(child_pid)
            os.kill(owner.pid, signal.SIGKILL)
            owner.wait(timeout=5)
            self.assertEqual(json.loads(path.read_text())['status'], 'running')
            active = subprocess.run(command, cwd=self.repo, env=dict(env, MODE='pass'), capture_output=True, text=True, timeout=10)
            self.assertEqual(active.returncode, 2, active.stderr)
            self.assertIn('still owns', active.stderr)
        finally:
            if child_pid:
                try:
                    os.killpg(child_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if owner.poll() is None:
                owner.kill(); owner.wait(timeout=5)
            owner.stdout.close(); owner.stderr.close()

        # The killed child's inherited descriptor may close just after killpg returns.
        deadline = time.monotonic()+10
        while time.monotonic()<deadline:
            try:
                with run_lifecycle.lock(directory):
                    break
            except ValueError:
                time.sleep(.05)
        else:
            self.fail('killed child did not release the handoff lock')
        retry = subprocess.run(command, cwd=self.repo, env=dict(env, MODE='pass'), capture_output=True, text=True, timeout=20)
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertIn('Recovered stale Claude attempts', retry.stderr)
        recovered = json.loads(path.read_text())
        self.assertEqual((recovered['backend'], recovered['transport'], recovered['status']),
                         ('claude', 'exec', 'interrupted'))
        self.assertEqual(json.loads((directory/'scout-L1-2.attempt.json').read_text())['status'], 'completed')
        self.assertFalse((directory/'scout-L1.running').exists())

        native = self.repo/'native-stale'
        native.mkdir()
        (native/'handoff.md').write_text('## Goal\nMap seed.txt\n')
        stale = native/'scout-L1.attempt.json'
        stale.write_text(json.dumps(dict(role='scout', level='L1', status='running', attempt_id='native-old')))
        fixture.codex_roles.install(self.repo)
        native_env = dict(self.env, SDLC_BACKEND='codex', SDLC_CODEX_TRANSPORT='subagent')
        refused = subprocess.run(command[:-1]+[str(native/'handoff.md')], cwd=self.repo, env=native_env,
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(refused.returncode, 2, refused.stderr)
        self.assertIn('Interrupted attempt needs review', refused.stderr)
        self.assertEqual(json.loads(stale.read_text())['status'], 'running')
        self.assertEqual(len(list(native.glob('*.attempt.json'))), 1)

    def test_claude_retry_refuses_unsafe_or_unknown_stale_records(self):
        (self.bin/'claude').write_text(CLAUDE)
        command = ['bash', str(fixture.ROOT/'scripts/run.sh'), 'scout', 'L1']
        claude = dict(self.env, SDLC_BACKEND='claude', MODE='pass')
        cases = {
            'codex-native': [('codex', 'subagent')],
            'codex-exec': [('codex', 'exec')],
            'mixed': [('claude', 'exec'), ('codex', 'subagent')],
            'missing-backend': [(None, 'exec')],
            'missing-transport': [('claude', None)],
            'unknown-backend': [('other', 'exec')],
            'unknown-transport': [('claude', 'other')],
        }
        for name, attempts in cases.items():
            with self.subTest(name=name):
                directory = self.repo/name
                directory.mkdir()
                handoff = directory/'handoff.md'
                handoff.write_text('## Goal\nMap seed.txt\n')
                originals = {}
                for index, (backend, transport) in enumerate(attempts):
                    stem = 'scout-L1' if index == 0 else 'verifier-L1'
                    record = dict(role=stem.split('-')[0], level='L1', status='running',
                                  attempt_id=name + '-' + str(index))
                    if backend is not None:
                        record['backend'] = backend
                    if transport is not None:
                        record['transport'] = transport
                    path = directory/(stem + '.attempt.json')
                    path.write_text(json.dumps(record))
                    originals[path.name] = path.read_bytes()
                    (directory/(stem + '.running')).write_text('preserved marker')
                    (directory/(stem + '.log')).write_text('preserved log')
                refused = subprocess.run(command + [str(handoff)], cwd=self.repo, env=claude,
                                         capture_output=True, text=True, timeout=10)
                self.assertEqual(refused.returncode, 2, refused.stderr)
                self.assertIn('Interrupted attempt needs review', refused.stderr)
                self.assertEqual({p.name: p.read_bytes() for p in directory.glob('*.attempt.json')}, originals)
                for stem in ('scout-L1', 'verifier-L1')[:len(attempts)]:
                    self.assertEqual((directory/(stem + '.running')).read_text(), 'preserved marker')
                    self.assertEqual((directory/(stem + '.log')).read_text(), 'preserved log')


if __name__ == '__main__':
    names = ['test_readiness_controls','test_both_hosts_cancel_lock_retry_and_routing','test_recovery_preserves_evidence_and_rejects_late_native_report','test_sigkill_recovers_claude_but_codex_native_refuses','test_claude_retry_refuses_unsafe_or_unknown_stale_records']
    result=unittest.TextTestRunner().run(unittest.TestSuite(LifecycleTests(n) for n in names))
    sys.exit(not result.wasSuccessful())
