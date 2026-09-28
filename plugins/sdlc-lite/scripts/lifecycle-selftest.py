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


if __name__ == '__main__':
    names = ['test_readiness_controls','test_both_hosts_cancel_lock_retry_and_routing','test_recovery_preserves_evidence_and_rejects_late_native_report']
    result=unittest.TextTestRunner().run(unittest.TestSuite(LifecycleTests(n) for n in names))
    sys.exit(not result.wasSuccessful())
