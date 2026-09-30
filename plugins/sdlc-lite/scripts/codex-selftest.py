#!/usr/bin/env python3
"""Behavioral Codex-backend tests with a stub CLI; no model calls."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

import codex_roles

ROOT = codex_roles.ROOT
# One deadline for every wait and child timeout, generous enough for a loaded host.
DEADLINE = 120
STUB = '''#!/usr/bin/env python3
import json, os, pathlib, sys, time
args=sys.argv[1:]
prompt=sys.stdin.read()
pathlib.Path(os.environ['PROBE']).write_text(json.dumps({'args':args,'prompt':prompt,'backend':os.environ.get('SDLC_BACKEND')}))
mode=os.environ.get('MODE','pass')
if mode=='timeout': time.sleep(600)
if mode=='exit': sys.exit(7)
if mode!='missing':
 text='## Map\\n- seed.txt:1: fixture\\n\\n## Entry points\\nseed.txt\\n\\n## Not found\\nNone'
 if mode=='bad': text='No required section'
 if mode=='verdict': text='## Verdict\\npass\\n\\n## Evidence\\nfixture'
 pathlib.Path(args[args.index('--output-last-message')+1]).write_text(text)
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':5}}))
'''


class CodexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='sdlc native test ')
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'project'; self.repo.mkdir()
        self.bin = self.base / 'bin'; self.bin.mkdir()
        for name, text in [('codex', STUB), ('claude', '#!/bin/sh\nexit 99\n')]:
            p = self.bin / name; p.write_text(text); p.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ['PATH'], SDLC_BACKEND='codex', SDLC_CODEX_TRANSPORT='exec', PROBE=str(self.base/'probe.json'))
        for args in [('init', '-q'), ('config','user.email','test@example.invalid'), ('config','user.name','Test')]:
            self.git(*args)
        (self.repo/'seed.txt').write_text('seed=3\n')
        self.git('add','seed.txt'); self.git('commit','-qm','fixture')
        self.step = self.repo/'work'; self.step.mkdir()
        self.handoff = self.step/'handoff.md'; self.handoff.write_text('## Goal\nLocate seed.\n')

    def tearDown(self):
        self.tmp.cleanup()

    def wait_for(self,predicate,describe=lambda:'',deadline=DEADLINE,directory=None,owner=None):
        """Poll predicate every 0.05 s; fail with the observed state on timeout or owner exit."""
        def state(reason):
            listing=sorted(p.name for p in directory.iterdir()) if directory is not None and directory.exists() else None
            parts=[reason,f'directory {directory}: {listing}',f'observed: {describe()}']
            if owner is not None:
                parts.append(f'owner returncode: {owner.poll()}')
                if owner.poll() is not None and owner.stderr is not None:
                    parts.append(f'owner stderr: {owner.stderr.read()}')
            return '; '.join(parts)
        end=time.monotonic()+deadline
        while True:
            value=predicate()
            if value:return value
            if owner is not None and owner.poll() is not None:
                value=predicate()
                if value:return value
                self.fail(state('owner exited before the condition held'))
            if time.monotonic()>=end:self.fail(state(f'condition not met within {deadline} s'))
            time.sleep(0.05)

    def git(self,*args):
        return subprocess.check_output(['git',*args],cwd=self.repo,stderr=subprocess.DEVNULL,text=True)

    def role(self,mode='pass',dry=False):
        env=dict(self.env,MODE=mode)
        if dry:env['SDLC_DRY_RUN']='1'
        if mode=='timeout':env['SDLC_CODEX_TIMEOUT_SECONDS']='1'
        return subprocess.run(['bash',str(ROOT/'scripts/run.sh'),'scout','L1',str(self.handoff)],cwd=self.repo,env=env,capture_output=True,text=True,timeout=DEADLINE)

    def test_result_and_rerun(self):
        for suffix in ['', '-2']:
            p=self.role(); self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn('## Map',(self.step/f'scout-L1{suffix}.md').read_text())
        records=[json.loads(s) for s in (self.step/'runs.jsonl').read_text().splitlines()]
        self.assertEqual([r['file'] for r in records],['scout-L1.md','scout-L1-2.md'])
        self.assertEqual(records[-1]['backend'],'codex')
        self.assertIsNone(records[-1]['cost_usd'])
        self.assertEqual(records[-1]['usage']['output_tokens'],5)
        probe=json.loads((self.base/'probe.json').read_text())
        self.assertEqual(probe['backend'],'codex')
        self.assertIn('approval_policy="never"',probe['args'])
        self.assertEqual(probe['args'][probe['args'].index('--sandbox')+1],'read-only')
        self.assertFalse(any('dangerously' in a for a in probe['args']))
        self.assertIn(str(self.handoff),probe['prompt'])
        self.assertFalse(list(self.step.glob('*.running')))

    def test_invalid_result_is_kept_but_fails(self):
        p=self.role('bad');self.assertEqual(p.returncode,3,p.stderr)
        self.assertTrue((self.step/'scout-L1.md').exists())
        self.assertIn('lacks ## Map',p.stderr)

    def test_failed_or_missing_result_never_passes(self):
        for mode in ['exit','missing','timeout']:
            p=self.role(mode);self.assertNotEqual(p.returncode,0)
            self.assertFalse((self.step/'scout-L1.md').exists())
            self.assertFalse(list(self.step.glob('*.running')))

    def test_dry_run(self):
        before=set(self.step.iterdir());p=self.role(dry=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('codex_exec.py',p.stdout)
        self.assertEqual(before,set(self.step.iterdir()))
        self.assertFalse((self.base/'probe.json').exists())

    def test_install_is_idempotent_and_preserves_edits(self):
        codex_roles.install(self.repo)
        codex_roles.install(self.repo,check=True)
        self.assertNotIn('.codex/',self.git('ls-files','--others','--exclude-standard'))
        target=self.repo/'.codex/agents/sdlc-scout-l1.toml'
        data=codex_roles.loads(target)
        self.assertNotIn(codex_roles.TOKEN,data['developer_instructions'])
        target.write_text(target.read_text()+'# user edit\n')
        with self.assertRaisesRegex(ValueError,'refusing to overwrite'):
            codex_roles.install(self.repo)
        self.assertTrue(target.read_text().endswith('# user edit\n'))
        target.unlink();target.symlink_to(self.handoff)
        with self.assertRaisesRegex(ValueError,'symlinked agent'):
            codex_roles.install(self.repo)

    def test_project_conductor_preserves_existing_config_and_removes_only_its_block(self):
        config=self.repo/'.codex/config.toml';config.parent.mkdir()
        original='''# keep this project comment
developer_instructions = ''' + "'''Keep the user's review rules.'''" + ''' # keep this inline comment
model = "gpt-6-sol"

[features] # keep this table
apps = true
tags = ["a", "b"]
'''
        config.write_text(original)
        config.chmod(0o600)
        codex_roles.install(self.repo,conductor=True)
        self.assertEqual(config.stat().st_mode & 0o777,0o600)
        import tomlkit
        doc=tomlkit.parse(config.read_text())
        self.assertTrue(str(doc['developer_instructions']).startswith("Keep the user's review rules.\n\n"))
        self.assertIn(codex_roles.CONDUCTOR_TEXT,str(doc['developer_instructions']))
        self.assertEqual(doc['features']['tags'],['a','b'])
        self.assertIn('# keep this project comment',config.read_text())
        self.assertIn('# keep this inline comment',config.read_text())
        self.assertIn('[features] # keep this table',config.read_text())
        first=config.read_text()
        codex_roles.install(self.repo,conductor=True)
        codex_roles.install(self.repo,check=True,conductor=True)
        self.assertEqual(config.read_text(),first)
        path,updated=codex_roles.conductor_config(self.repo,False)
        codex_roles.write_conductor_config(path,updated)
        self.assertEqual(str(tomlkit.parse(config.read_text())['developer_instructions']),
                         "Keep the user's review rules.")
        codex_roles.install(self.repo,conductor=True)
        doc=tomlkit.parse(config.read_text())
        doc['developer_instructions']=str(doc['developer_instructions'])+'\nExtra user rule.'
        config.write_text(tomlkit.dumps(doc))
        path,updated=codex_roles.conductor_config(self.repo,False)
        codex_roles.write_conductor_config(path,updated)
        restored=tomlkit.parse(config.read_text())
        self.assertEqual(str(restored['developer_instructions']),"Keep the user's review rules.\nExtra user rule.")
        self.assertEqual(restored['features']['tags'],['a','b'])
        self.assertNotIn(codex_roles.CONDUCTOR_MARKER,config.read_text())

    def test_project_conductor_fresh_config_check_and_removal(self):
        codex_roles.install(self.repo)
        with self.assertRaisesRegex(ValueError,'conductor instructions are missing'):
            codex_roles.install(self.repo,check=True,conductor=True)
        codex_roles.install(self.repo,conductor=True)
        config=self.repo/'.codex/config.toml'
        self.assertEqual(config.stat().st_mode & 0o777,0o600)
        self.assertIn('created-key',config.read_text())
        path,updated=codex_roles.conductor_config(self.repo,False)
        codex_roles.write_conductor_config(path,updated)
        import tomlkit
        self.assertNotIn('developer_instructions',tomlkit.parse(config.read_text()))
        self.assertTrue((self.repo/'.codex/agents/sdlc-scout-l1.toml').exists())
        self.assertEqual(codex_roles.conductor_config(self.repo,False)[1],None)
        codex_roles.install(self.repo,conductor=True)
        parsed=tomlkit.parse(config.read_text())
        parsed['developer_instructions']=str(parsed['developer_instructions'])+'\nA later user rule.'
        config.write_text(tomlkit.dumps(parsed))
        path,updated=codex_roles.conductor_config(self.repo,False)
        codex_roles.write_conductor_config(path,updated)
        self.assertEqual(str(tomlkit.parse(config.read_text())['developer_instructions']),
                         '\nA later user rule.')

    def test_project_conductor_preserves_an_existing_empty_key_and_unrelated_markers(self):
        config=self.repo/'.codex/config.toml';config.parent.mkdir()
        config.write_text('''# <!-- SDLC Lite Codex project conductor: unrelated note -->
developer_instructions = ""
[features]
apps = true
[other]
message = "<!-- SDLC Lite Codex project conductor: example -->"
''')
        codex_roles.install(self.repo,conductor=True)
        self.assertIn('appended begin',config.read_text())
        path,updated=codex_roles.conductor_config(self.repo,False)
        codex_roles.write_conductor_config(path,updated)
        import tomlkit
        parsed=tomlkit.parse(config.read_text())
        self.assertIn('developer_instructions',parsed)
        self.assertEqual(str(parsed['developer_instructions']),'')
        self.assertEqual(str(parsed['other']['message']),
                         '<!-- SDLC Lite Codex project conductor: example -->')
        self.assertIn('# <!-- SDLC Lite Codex project conductor: unrelated note -->',config.read_text())

    def test_project_conductor_preserves_crlf_instruction_and_file_newlines(self):
        config=self.repo/'.codex/config.toml';config.parent.mkdir()
        with config.open('w',encoding='utf-8',newline='') as output:
            output.write('developer_instructions = "a\\r\\nb"\r\n[features]\r\napps = true\r\n')
        codex_roles.install(self.repo,conductor=True)
        path,updated=codex_roles.conductor_config(self.repo,False)
        codex_roles.write_conductor_config(path,updated)
        import tomlkit
        with config.open('r',encoding='utf-8',newline='') as source:
            result=source.read()
        self.assertEqual(str(tomlkit.parse(result)['developer_instructions']),'a\r\nb')
        self.assertIn('[features]\r\napps = true\r\n',result)

    def test_project_conductor_refuses_invalid_or_edited_config_before_agent_writes(self):
        config=self.repo/'.codex/config.toml';config.parent.mkdir()
        config.write_text('developer_instructions = [broken\n')
        with self.assertRaisesRegex(ValueError,'invalid project config TOML'):
            codex_roles.install(self.repo,conductor=True)
        self.assertFalse((self.repo/'.codex/agents').exists())
        config.write_text('developer_instructions = 7\n')
        with self.assertRaisesRegex(ValueError,'must be a string'):
            codex_roles.install(self.repo,conductor=True)
        config.write_text('developer_instructions = "User rules"\n')
        codex_roles.install(self.repo,conductor=True)
        edited=config.read_text().replace('act as the SDLC Lite conductor','ignore the SDLC Lite conductor')
        config.write_text(edited)
        with self.assertRaisesRegex(ValueError,'edited SDLC Lite conductor'):
            codex_roles.conductor_config(self.repo,False)
        with self.assertRaisesRegex(ValueError,'edited SDLC Lite conductor'):
            codex_roles.install(self.repo,conductor=True)
        self.assertEqual(config.read_text(),edited)
        config.write_text('developer_instructions = "Quote: <!-- SDLC Lite Codex project conductor: user note -->"\n')
        codex_roles.install(self.repo,conductor=True)
        path,updated=codex_roles.conductor_config(self.repo,False)
        codex_roles.write_conductor_config(path,updated)
        import tomlkit
        self.assertEqual(str(tomlkit.parse(config.read_text())['developer_instructions']),
                         'Quote: <!-- SDLC Lite Codex project conductor: user note -->')

    def test_verifier_shares_builder_model_without_alternate(self):
        from unittest import mock
        (self.step/'builder-L1.md').write_text('<!-- role=builder level=L1 model=gpt-6-luna effort=low -->\n## Status\ndone\n')
        with mock.patch.object(codex_roles,'verifier_alternates',return_value={}):
            self.assertEqual(codex_roles.resolve('verifier','L1',self.step),('gpt-6-luna','low',True))
            (self.step/'builder-L1.md').write_text('<!-- role=builder level=L1 model=other-model effort=low -->\n')
            self.assertEqual(codex_roles.resolve('verifier','L1',self.step),('gpt-6-luna','low',False))
            self.assertFalse(any(name.endswith('-alternate') for name,_ in codex_roles.definitions()))

    def test_verifier_alternate_comes_from_config(self):
        from unittest import mock
        (self.step/'builder-L1.md').write_text('<!-- role=builder level=L1 model=gpt-6-luna effort=low -->\n## Status\ndone\n')
        with mock.patch.object(codex_roles,'verifier_alternates',return_value={'gpt-6-luna':'fixture-alt'}):
            self.assertEqual(codex_roles.resolve('verifier','L1',self.step),('fixture-alt','low',False))
            defs=dict(codex_roles.definitions())
        self.assertEqual(defs['sdlc-verifier-l1-alternate']['model'],'fixture-alt')
        self.assertEqual(defs['sdlc-verifier-l1-alternate']['model_reasoning_effort'],'low')

    def test_runner_records_verifier_model_with_and_without_alternate(self):
        import shutil
        plugin=self.base/'plugin'
        shutil.copytree(ROOT,plugin,ignore=shutil.ignore_patterns('__pycache__','*.log'))
        (self.step/'builder-L1.md').write_text('<!-- role=builder level=L1 model=gpt-6-luna effort=low -->\n## Status\ndone\n')
        for alternates,model,shared in [({},'gpt-6-luna',True),({'gpt-6-luna':'fixture-alt'},'fixture-alt',False)]:
            with self.subTest(alternates=alternates):
                config=codex_roles.config();config['verifier_alternates']=alternates
                (plugin/'adapters/codex/models.json').write_text(json.dumps(config))
                subprocess.run(['python3',str(plugin/'scripts/codex_roles.py'),'generate'],check=True,
                               capture_output=True,text=True,timeout=DEADLINE)
                p=subprocess.run(['bash',str(plugin/'scripts/run.sh'),'verifier','L1',str(self.handoff)],cwd=self.repo,
                                 env=dict(self.env,MODE='verdict'),capture_output=True,text=True,timeout=DEADLINE)
                self.assertEqual(p.returncode,0,p.stderr)
                record=json.loads((self.step/'runs.jsonl').read_text().splitlines()[-1])
                header=(self.step/record['file']).read_text().splitlines()[0]
                self.assertIn('model='+model,header)
                self.assertEqual('shared_with_builder=yes' in header,shared)
                self.assertEqual(record['role'],'verifier')
                self.assertEqual(record['model'],model)
                self.assertIs(record['shared_with_builder'],shared)
                probe=json.loads((self.base/'probe.json').read_text())
                self.assertEqual(probe['args'][probe['args'].index('--model')+1],model)

    def test_plan_reviewer_alternate_follows_newest_planner(self):
        from unittest import mock
        planner=self.step/'planner-L3.md'
        planner.write_text('<!-- role=planner level=L3 model=gpt-6-astra effort=high -->\n## Goal\nx\n')
        self.assertEqual(codex_roles.resolve('plan-reviewer','L1',self.step),('gpt-6.1-sol','high',False))
        with mock.patch.object(codex_roles,'verifier_alternates',return_value={}):
            self.assertEqual(codex_roles.resolve('plan-reviewer','L1',self.step),('gpt-6-astra','high',True))
        planner.unlink()
        (self.step/'planner-L2.md').write_text('<!-- role=planner level=L2 model=gpt-6.1-sol effort=high -->\n## Goal\nx\n')
        self.assertEqual(codex_roles.resolve('plan-reviewer','L1',self.step),('gpt-6-astra','high',False))
        defs=dict(codex_roles.definitions())
        self.assertEqual(defs['sdlc-plan-reviewer-l1-alternate']['model'],'gpt-6.1-sol')
        self.assertEqual(defs['sdlc-plan-reviewer-l1-alternate']['model_reasoning_effort'],'high')
        self.assertEqual(defs['sdlc-plan-reviewer-l1-alternate']['sandbox_mode'],'read-only')

    def test_runner_records_plan_reviewer_alternate_agent(self):
        import codex_exchange
        codex_roles.install(self.repo)
        env=dict(self.env,SDLC_CODEX_TRANSPORT='subagent',SDLC_CODEX_TIMEOUT_SECONDS=str(DEADLINE))
        planner=self.step/'planner-L3.md'
        planner.write_text('<!-- role=planner level=L3 model=gpt-6-astra effort=high -->\n## Goal\nx\n')
        proc=subprocess.Popen(['bash',str(ROOT/'scripts/run.sh'),'plan-reviewer','L1',str(self.handoff)],
                              cwd=self.repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        request=self.step/'plan-reviewer-L1.request.json'
        try:
            self.wait_for(request.exists,directory=self.step,owner=proc)
            payload=json.loads(request.read_text())
            self.assertEqual(payload['agent'],'sdlc-plan-reviewer-l1-alternate')
            self.assertEqual(payload['model'],'gpt-6.1-sol')
            report=self.step/'child-report.txt';report.write_text('## Verdict\npass\n\n## Findings\nNone\n')
            codex_exchange.respond(request,report)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,0,stderr)
            header=(self.step/'plan-reviewer-L1.md').read_text().splitlines()[0]
            self.assertIn('model=gpt-6.1-sol',header)
            record=json.loads((self.step/'runs.jsonl').read_text().splitlines()[-1])
            self.assertEqual(record['role'],'plan-reviewer')
            self.assertEqual(record['model'],'gpt-6.1-sol')
            self.assertIs(record['shared_with_builder'],False)
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()
        # Negative control: a Sol plan keeps the reviewer on its default Astra profile.
        planner.write_text('<!-- role=planner level=L3 model=gpt-6.1-sol effort=high -->\n## Goal\nx\n')
        proc=subprocess.Popen(['bash',str(ROOT/'scripts/run.sh'),'plan-reviewer','L1',str(self.handoff)],
                              cwd=self.repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        request=self.step/'plan-reviewer-L1-2.request.json'
        try:
            self.wait_for(request.exists,directory=self.step,owner=proc)
            payload=json.loads(request.read_text())
            self.assertEqual(payload['agent'],'sdlc-plan-reviewer-l1')
            self.assertEqual(payload['model'],'gpt-6-astra')
            codex_exchange.respond(request,report)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,0,stderr)
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()

    def test_definitions_match_shared_contracts(self):
        for name,data in codex_roles.definitions():
            self.assertEqual(codex_roles.loads(ROOT/'adapters/codex/agents'/(name+'.toml')),data)
        verifier=codex_roles.loads(ROOT/'adapters/codex/agents/sdlc-verifier-l1.toml')
        self.assertIn('# Required skill: checks-that-bite',verifier['developer_instructions'])
        self.assertIn('# Required skill: checking-rules',verifier['developer_instructions'])

    def test_toml_contains_unicode_scalars_not_surrogates(self):
        import re
        text=codex_roles.dumps({'developer_instructions':'Status: 🟢 done'})
        # TOML forbids surrogate escapes, even though a JSON reader would accept them.
        self.assertIsNone(re.search(r'\\u[dD][89a-fA-F][0-9a-fA-F]{2}',text))
        self.assertIn('🟢',text)

    def test_benchmark_native_driver_and_unknown_cost(self):
        bench=self.repo/'bench';(bench/'tasks').mkdir(parents=True)
        (bench/'tasks/demo.md').write_text('Fixture benchmark')
        p=subprocess.run(['bash',str(ROOT/'scripts/bench.sh'),'--bench-dir',str(bench),'demo'],
                         cwd=self.repo,env=self.env,capture_output=True,text=True,timeout=DEADLINE)
        self.assertEqual(p.returncode,0,p.stderr)
        probe=json.loads((self.base/'probe.json').read_text())
        self.assertIn('/sdlc-lite:bench demo',probe['prompt'])
        self.assertIn('agents.enabled=true',probe['args'])
        self.assertNotIn('sandbox_workspace_write.network_access=true',probe['args'])
        results=bench/'results/demo';results.mkdir(parents=True)
        (results/'runs.jsonl').write_text(json.dumps({'backend':'codex','cost_usd':None})+'\n')
        p=subprocess.run(['bash',str(ROOT/'scripts/bench-summary.sh'),'--bench-dir',str(bench)],
                         cwd=self.repo,env=self.env,capture_output=True,text=True,timeout=DEADLINE)
        self.assertEqual(p.returncode,0,p.stderr);self.assertIn('unknown',p.stdout)
        p=subprocess.run(['bash',str(ROOT/'scripts/bench.sh'),'--bench-dir',str(bench),'demo'],
                         cwd=self.repo,env=dict(self.env,MODE='exit'),capture_output=True,text=True,timeout=DEADLINE)
        self.assertNotEqual(p.returncode,0,'A failed Codex conductor must fail the benchmark launcher')

    def test_native_exchange_preserves_runner_artifacts(self):
        import codex_exchange
        codex_roles.install(self.repo)
        env=dict(self.env,SDLC_CODEX_TRANSPORT='subagent',SDLC_CODEX_TIMEOUT_SECONDS=str(DEADLINE))
        proc=subprocess.Popen(['bash',str(ROOT/'scripts/run.sh'),'scout','L1',str(self.handoff)],
                              cwd=self.repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        request=self.step/'scout-L1.request.json'
        try:
            self.wait_for(request.exists,directory=self.step,owner=proc)
            payload=json.loads(request.read_text())
            self.assertEqual(payload['agent'],'sdlc-scout-l1')
            self.assertIn('SDLC_TMP_WORKTREES=',payload['prompt'])
            report=self.step/'child-report.txt';report.write_text('## Map\nseed.txt:1\n')
            codex_exchange.respond(request,report)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,0,stderr)
            self.assertTrue((self.step/'scout-L1.md').exists())
            self.assertFalse((self.base/'probe.json').exists(),'Subagent transport must not launch codex or claude')
            record=json.loads((self.step/'runs.jsonl').read_text())
            self.assertEqual(record['transport'],'subagent')
            with self.assertRaises(ValueError):codex_exchange.respond(request,report)
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()

    def test_conductor_exchange_needs_no_nested_cli(self):
        import codex_exchange
        codex_roles.install(self.repo)
        env=dict(self.env,SDLC_CODEX_TRANSPORT='subagent',SDLC_CODEX_TIMEOUT_SECONDS=str(DEADLINE))
        proc=subprocess.Popen(['python3',str(ROOT/'scripts/codex_exec.py'),'conductor','L1','Process fixture task'],
                              cwd=self.repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            requests=self.wait_for(lambda:list((self.repo/'.sdlc').glob('native-conductor-*.request.json')),
                                   directory=self.repo/'.sdlc',owner=proc)
            request=requests[0];payload=json.loads(request.read_text())
            self.assertEqual(payload['agent'],'sdlc-conductor-l1')
            self.assertIn(str(self.repo),payload['prompt'])
            report=self.repo/'conductor-report.txt';report.write_text('Fixture completed')
            codex_exchange.respond(request,report)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,0,stderr)
            self.assertEqual(json.loads(stdout)['result'],'Fixture completed')
            self.assertFalse((self.base/'probe.json').exists())
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()

    def test_unanswered_native_request_fails_and_cleans_marker(self):
        codex_roles.install(self.repo)
        self.env['SDLC_CODEX_TRANSPORT']='subagent'
        p=self.role('timeout')
        self.assertNotEqual(p.returncode,0)
        self.assertFalse((self.step/'scout-L1.md').exists())
        self.assertFalse(list(self.step.glob('*.running')))
        request=json.loads((self.step/'scout-L1.request.json').read_text())
        self.assertEqual(request['status'],'failed')

    def test_fanout_uses_codex(self):
        import fanout
        previous=os.environ.get('SDLC_BACKEND')
        try:
            os.environ['SDLC_BACKEND']='codex'
            command=fanout.default_driver('work/handoff.md')
            self.assertIn('codex_exec.py',command)
            self.assertNotIn('claude',command)
            os.environ['SDLC_BACKEND']='wrong'
            with self.assertRaises(fanout.Refuse):fanout.default_driver('work/handoff.md')
        finally:
            if previous is None:os.environ.pop('SDLC_BACKEND',None)
            else:os.environ['SDLC_BACKEND']=previous


if __name__=='__main__':
    unittest.main()
