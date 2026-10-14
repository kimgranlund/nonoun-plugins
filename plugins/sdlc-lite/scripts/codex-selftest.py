#!/usr/bin/env python3
"""Behavioral Codex-backend tests with a stub CLI; no model calls."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import time
import unittest

import codex_roles
import order

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

    @property
    def rec(self):
        """The records dir of the step (order.records_dir): results, runs.jsonl, requests and markers land there."""
        return order.records_dir(self.step)

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
            self.assertIn('## Map',(self.rec/f'scout-L1{suffix}.md').read_text())
        records=[json.loads(s) for s in (self.rec/'runs.jsonl').read_text().splitlines()]
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
        self.assertFalse(list(self.rec.glob('*.running')))

    def test_invalid_result_is_kept_but_fails(self):
        p=self.role('bad');self.assertEqual(p.returncode,3,p.stderr)
        self.assertTrue((self.rec/'scout-L1.md').exists())
        self.assertIn('lacks ## Map',p.stderr)

    def test_failed_or_missing_result_never_passes(self):
        for mode in ['exit','missing','timeout']:
            p=self.role(mode);self.assertNotEqual(p.returncode,0)
            self.assertFalse((self.rec/'scout-L1.md').exists())
            self.assertFalse(list(self.rec.glob('*.running')))

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

    def catalog(self,without=()):
        return {name for name,_ in codex_roles.definitions() if name not in without}

    def test_preflight_current_definitions_stale_live_catalog_is_not_ready(self):
        codex_roles.install(self.repo)
        problems=codex_roles.preflight(self.repo,['sdlc-solo-l2'],self.catalog(without=('sdlc-solo-l1','sdlc-solo-l2','sdlc-solo-l3')))
        self.assertEqual(len(problems),1,problems)
        self.assertIn('sdlc-solo-l2',problems[0]);self.assertIn('Fresh session required',problems[0])
        self.assertNotIn('Generation required',problems[0])

    def test_preflight_stale_definitions_with_older_roles_loaded_is_not_ready(self):
        codex_roles.install(self.repo)
        for target in (self.repo/'.codex/agents').glob('sdlc-solo-*.toml'):target.unlink()
        older=self.catalog(without=('sdlc-solo-l1','sdlc-solo-l2','sdlc-solo-l3'))
        problems=codex_roles.preflight(self.repo,['sdlc-solo-l2'],older)
        text='\n'.join(problems)
        self.assertIn('Generation required',text);self.assertIn('sdlc-solo-l2.toml',text)
        self.assertIn('after generation, start a fresh Codex session',text)

    def test_preflight_fresh_session_with_required_role_is_ready(self):
        codex_roles.install(self.repo)
        self.assertEqual(codex_roles.preflight(self.repo,['sdlc-solo-l2','sdlc-verifier-l3'],self.catalog()),[])
        self.assertEqual(codex_roles.parse_catalog('sdlc-solo-l2, sdlc-verifier-l3\nsdlc-builder-l1'),{'sdlc-solo-l2','sdlc-verifier-l3','sdlc-builder-l1'})

    def test_preflight_unknown_role_and_edited_definition_need_launcher_repair_and_install_check_unchanged(self):
        codex_roles.install(self.repo)
        problems=codex_roles.preflight(self.repo,['sdlc-solo-l9'],self.catalog()|{'sdlc-solo-l9'})
        self.assertIn('Launcher repair',problems[0])
        target=self.repo/'.codex/agents/sdlc-scout-l1.toml'
        target.write_text(target.read_text()+'# user edit\n')
        problems=codex_roles.preflight(self.repo,['sdlc-solo-l2'],self.catalog())
        self.assertIn('Launcher repair',problems[0]);self.assertIn('refusing to overwrite',problems[0])
        self.assertTrue(target.read_text().endswith('# user edit\n'))
        with self.assertRaisesRegex(ValueError,'refusing to overwrite'):
            codex_roles.install(self.repo,check=True)

    def test_handshake_loaded_fingerprint_equals_binding_is_ready(self):
        fp=codex_roles.fingerprint('sdlc-solo-l2')
        self.assertRegex(fp,r'^\d+\.\d+\.\d+\+[0-9a-f]{12}$')
        status,message=codex_roles.check_loaded('sdlc-solo-l2','profile: '+fp+'\nDone.')
        self.assertEqual(status,'ready',message)

    def test_handshake_different_fingerprint_is_refused_with_fresh_session_action(self):
        status,message=codex_roles.check_loaded('sdlc-solo-l2','profile: 0.21.3+000000000000\nDone.')
        self.assertEqual(status,'refused');self.assertIn('Start a fresh Codex session',message);self.assertIn('0.21.3+000000000000',message)

    def test_handshake_absent_fingerprint_is_unknown_and_requires_handshake(self):
        for report in ('','All done, edits made.\nprofile: '+codex_roles.fingerprint('sdlc-solo-l2')):
            status,message=codex_roles.check_loaded('sdlc-solo-l2',report)
            self.assertEqual(status,'unknown');self.assertIn('live freshness unknown',message);self.assertIn('Handshake required',message)

    def test_profile_carries_its_fingerprint_and_it_tracks_the_content(self):
        text=dict(codex_roles.definitions())['sdlc-solo-l2']['developer_instructions']
        self.assertIn('exactly `profile: '+codex_roles.fingerprint('sdlc-solo-l2')+'`',text)
        self.assertNotEqual(codex_roles.fingerprint('sdlc-solo-l2'),codex_roles.fingerprint('sdlc-solo-l3'))
        raw=dict(codex_roles.raw_definitions())['sdlc-solo-l2']
        self.assertEqual(codex_roles.fingerprint_of(raw),codex_roles.fingerprint('sdlc-solo-l2'))
        self.assertNotEqual(codex_roles.fingerprint_of(dict(raw,developer_instructions=raw['developer_instructions']+' x')),codex_roles.fingerprint('sdlc-solo-l2'))

    # T-0506: the fingerprint line is a host envelope in front of the shared role body, and every profile says so.
    def test_every_profile_defines_one_compatible_envelope_and_body_format(self):
        for name,data in codex_roles.definitions():
            text=data['developer_instructions']
            self.assertIsNone(codex_roles.envelope_conflict(text),name)
            self.assertIn(codex_roles.ENVELOPE_MARK,text,name)
            self.assertIn('keeps the envelope as its second line',text,name)

    def test_contradictory_envelope_contract_is_rejected_and_the_corrected_one_passes(self):
        raw=dict(codex_roles.raw_definitions())['sdlc-scout-l1']['developer_instructions']
        self.assertIn('nothing before the first heading',raw)
        fp='0.0.0+000000000000'
        # Observed defect: the pre-T-0506 note demanded a `profile:` first line beside the shared first-heading rule.
        legacy=raw+('\n\n# Profile fingerprint\nThis profile is revision `'+fp+'`. Before any edit, make the first line of your first message '
                    'and the first line of your final report exactly `profile: '+fp+'`.')
        self.assertIn('no envelope rule',codex_roles.envelope_conflict(legacy))
        fixed=raw+codex_roles.envelope_note(fp)
        self.assertIsNone(codex_roles.envelope_conflict(fixed))

    def test_fingerprinted_report_passes_the_native_exchange_and_result_parser(self):
        import codex_exchange,results
        codex_roles.install(self.repo)
        fp=codex_roles.fingerprint('sdlc-scout-l1')
        env=dict(self.env,SDLC_CODEX_TRANSPORT='subagent',SDLC_CODEX_TIMEOUT_SECONDS=str(DEADLINE))
        def exchange(text):
            for old in self.rec.glob('scout-L1*'):old.unlink()
            proc=subprocess.Popen(['bash',str(ROOT/'scripts/run.sh'),'scout','L1',str(self.handoff)],
                                  cwd=self.repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            request=self.rec/'scout-L1.request.json'
            try:
                self.wait_for(request.exists,directory=self.rec,owner=proc)
                report=self.step/'child-report.txt';report.write_text(text)
                codex_exchange.respond(request,report)
                _,stderr=proc.communicate(timeout=DEADLINE)
                return proc.returncode,stderr
            finally:
                if proc.poll() is None:proc.kill();proc.communicate()
        body='## Map\n- seed.txt:1: fixture\n\n## Entry points\nseed.txt\n\n## Not found\nNone\n'
        code,err=exchange('profile: '+fp+'\n\n'+body)
        self.assertEqual(code,0,err)
        stored=self.rec/'scout-L1.md'
        lines=stored.read_text().splitlines()
        self.assertTrue(lines[0].startswith('<!-- role=scout'));self.assertEqual(lines[1],'profile: '+fp)
        self.assertIsNone(results.validate(str(stored),'scout'))
        for heading in ('## Map','## Entry points','## Not found'):self.assertIn(heading,lines)
        self.assertEqual(codex_roles.check_loaded('sdlc-scout-l1',stored.read_text().split('\n',1)[1])[0],'ready')
        # The envelope is valid but the body is malformed: the parser still rejects it.
        code,err=exchange('profile: '+fp+'\n\nNo required section\n')
        self.assertEqual(code,3,err);self.assertIn('lacks ## Map',err)
        code,err=exchange('profile: '+fp+'\n\n'+body.replace('## Map','## Mapping'))
        self.assertEqual(code,3,err);self.assertIn('lacks ## Map',err)

    def test_handshake_cli_exit_codes(self):
        script=str(ROOT/'scripts/codex_roles.py');fp=codex_roles.fingerprint('sdlc-solo-l2')
        run=lambda *a:subprocess.run(['python3',script,'handshake','sdlc-solo-l2',*a],capture_output=True,text=True,timeout=DEADLINE)
        rep=self.base/'first.txt'
        rep.write_text('profile: '+fp+'\n');self.assertEqual(run('--report-file',str(rep)).returncode,0)
        rep.write_text('profile: 0.21.3+aaaaaaaaaaaa\n');bad=run('--report-file',str(rep));self.assertEqual(bad.returncode,2);self.assertIn('fresh Codex session',bad.stderr)
        self.assertEqual(run().returncode,3);self.assertEqual(run('--report-file',str(self.base/'none.txt')).returncode,3)
        rep.write_text('profile: 9.9.9+bbbbbbbbbbbb\n');self.assertEqual(run('--report-file',str(rep),'--binding','9.9.9+bbbbbbbbbbbb').returncode,0)

    def test_preflight_cli_requires_a_supplied_catalog(self):
        codex_roles.install(self.repo)
        script=str(ROOT/'scripts/codex_roles.py')
        run=lambda *a:subprocess.run(['python3',script,'preflight',str(self.repo),'sdlc-solo-l2',*a],capture_output=True,text=True,timeout=DEADLINE)
        none=run();self.assertEqual(none.returncode,2);self.assertIn('no callable catalog supplied',none.stderr)
        stale=run('--catalog','sdlc-builder-l1 sdlc-planner-l1');self.assertEqual(stale.returncode,2);self.assertIn('Fresh session required',stale.stderr)
        listing=self.base/'catalog.txt';listing.write_text('\n'.join(sorted(self.catalog())))
        ok=run('--catalog-file',str(listing));self.assertEqual(ok.returncode,0,ok.stderr);self.assertIn('ready: sdlc-solo-l2',ok.stdout)

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

    def test_verifier_task_dir_reads_newest_live_step_builder(self):
        from unittest import mock
        alts={'gpt-6-luna':'fixture-alt','gpt-6-astra':'fixture-alt'}
        def build(name,files):
            d=self.repo/name
            for rel,model in files.items():
                (d/rel).parent.mkdir(parents=True,exist_ok=True)
                text='## Step\n' if model is None else f'<!-- role=builder level=L1 model={model} effort=low -->\n## Status\ndone\n'
                (d/rel).write_text(text)
            return d
        with mock.patch.object(codex_roles,'verifier_alternates',return_value=alts):
            d=build('td1',{'step-1/builder-L1.md':'gpt-6-luna'})
            self.assertEqual(codex_roles.resolve('verifier','L1',d),('fixture-alt','low',False))
            with mock.patch.object(codex_roles,'verifier_alternates',return_value={}):
                self.assertEqual(codex_roles.resolve('verifier','L1',d),('gpt-6-luna','low',True))
            d=build('td2a',{'step-1/builder-L1.md':'gpt-6-luna','step-2/handoff.md':None,
                            'step-2.superseded-1/builder-L1.md':'other-model'})
            self.assertEqual(codex_roles.resolve('verifier','L1',d),('fixture-alt','low',False))
            d=build('td2b',{'step-1/builder-L1.md':'other-model','step-2.superseded-1/builder-L1.md':'gpt-6-luna'})
            self.assertEqual(codex_roles.resolve('verifier','L1',d),('gpt-6-luna','low',False))
            d=build('td3a',{'step-2/builder-L1.md':'other-model','step-10/builder-L1.md':'gpt-6-luna'})
            self.assertEqual(codex_roles.resolve('verifier','L1',d),('fixture-alt','low',False))
            d=build('td3b',{'step-2/builder-L1.md':'gpt-6-luna','step-10/builder-L1.md':'other-model'})
            self.assertEqual(codex_roles.resolve('verifier','L1',d),('gpt-6-luna','low',False))
            d=build('td4',{'builder-L3.md':'other-model','step-1/builder-L1.md':'gpt-6-luna'})
            self.assertEqual(codex_roles.resolve('verifier','L1',d),('gpt-6-luna','low',False))
            d=self.repo/'td5';(d/'step-1').mkdir(parents=True)
            (d/'step-1'/'planner-L3.md').write_text('<!-- role=planner level=L3 model=gpt-6-astra effort=high -->\n## Steps\n')
            self.assertEqual(codex_roles.resolve('plan-reviewer','L1',d),('gpt-6-astra','high',False))

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
                record=json.loads((self.rec/'runs.jsonl').read_text().splitlines()[-1])
                header=(self.rec/record['file']).read_text().splitlines()[0]
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
        self.assertEqual(defs['sdlc-ui-designer-l1']['sandbox_mode'],'workspace-write')

    def test_runner_records_plan_reviewer_alternate_agent(self):
        import codex_exchange
        codex_roles.install(self.repo)
        env=dict(self.env,SDLC_CODEX_TRANSPORT='subagent',SDLC_CODEX_TIMEOUT_SECONDS=str(DEADLINE))
        planner=self.step/'planner-L3.md'
        planner.write_text('<!-- role=planner level=L3 model=gpt-6-astra effort=high -->\n## Goal\nx\n')
        proc=subprocess.Popen(['bash',str(ROOT/'scripts/run.sh'),'plan-reviewer','L1',str(self.handoff)],
                              cwd=self.repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        request=self.rec/'plan-reviewer-L1.request.json'
        try:
            self.wait_for(request.exists,directory=self.rec,owner=proc)
            payload=json.loads(request.read_text())
            self.assertEqual(payload['agent'],'sdlc-plan-reviewer-l1-alternate')
            self.assertEqual(payload['model'],'gpt-6.1-sol')
            self.assertEqual(payload['profile_fingerprint'],codex_roles.fingerprint('sdlc-plan-reviewer-l1-alternate'))
            report=self.step/'child-report.txt';report.write_text('profile: '+payload['profile_fingerprint']+'\n## Verdict\npass\n\n## Findings\nNone\n')
            codex_exchange.respond(request,report)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,0,stderr)
            header=(self.rec/'plan-reviewer-L1.md').read_text().splitlines()[0]
            self.assertIn('model=gpt-6.1-sol',header)
            record=json.loads((self.rec/'runs.jsonl').read_text().splitlines()[-1])
            self.assertEqual(record['role'],'plan-reviewer')
            self.assertEqual(record['model'],'gpt-6.1-sol')
            self.assertIs(record['shared_with_builder'],False)
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()
        # Negative control: a Sol plan keeps the reviewer on its default Astra profile.
        planner.write_text('<!-- role=planner level=L3 model=gpt-6.1-sol effort=high -->\n## Goal\nx\n')
        proc=subprocess.Popen(['bash',str(ROOT/'scripts/run.sh'),'plan-reviewer','L1',str(self.handoff)],
                              cwd=self.repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        request=self.rec/'plan-reviewer-L1-2.request.json'
        try:
            self.wait_for(request.exists,directory=self.rec,owner=proc)
            payload=json.loads(request.read_text())
            self.assertEqual(payload['agent'],'sdlc-plan-reviewer-l1')
            self.assertEqual(payload['model'],'gpt-6-astra')
            self.assertEqual(payload['profile_fingerprint'],codex_roles.fingerprint('sdlc-plan-reviewer-l1'))
            report.write_text('profile: '+payload['profile_fingerprint']+'\n## Verdict\npass\n\n## Findings\nNone\n')
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
        request=self.rec/'scout-L1.request.json'
        try:
            self.wait_for(request.exists,directory=self.rec,owner=proc)
            payload=json.loads(request.read_text())
            self.assertEqual(payload['agent'],'sdlc-scout-l1')
            self.assertIn('SDLC_TMP_WORKTREES=',payload['prompt'])
            fp=codex_roles.fingerprint('sdlc-scout-l1')
            self.assertEqual(payload['profile_fingerprint'],fp)
            report=self.step/'child-report.txt';report.write_text('profile: '+payload['profile_fingerprint']+'\n## Map\nseed.txt:1\n')
            codex_exchange.respond(request,report)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,0,stderr)
            self.assertTrue((self.rec/'scout-L1.md').exists())
            self.assertFalse((self.base/'probe.json').exists(),'Subagent transport must not launch codex or claude')
            record=json.loads((self.rec/'runs.jsonl').read_text())
            self.assertEqual(record['transport'],'subagent')
            # T-0507: the kept request and the runs.jsonl line hold the dispatched binding.
            self.assertEqual((record['profile_fingerprint'],record['profile_check']),(fp,'ready'))
            self.assertEqual(json.loads(request.read_text())['profile_fingerprint'],fp)
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
            requests=self.wait_for(lambda:list((self.repo/'.sdlc'/'runtime').glob('native-conductor-*.request.json')),
                                   directory=self.repo/'.sdlc'/'runtime',owner=proc)
            request=requests[0];payload=json.loads(request.read_text())
            self.assertEqual(payload['agent'],'sdlc-conductor-l1')
            self.assertIn(str(self.repo),payload['prompt'])
            text='profile: '+payload['profile_fingerprint']+'\nFixture completed'
            report=self.repo/'conductor-report.txt';report.write_text(text)
            codex_exchange.respond(request,report)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,0,stderr)
            self.assertEqual(json.loads(stdout)['result'],text)
            self.assertFalse((self.base/'probe.json').exists())
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()

    def test_unanswered_native_request_fails_and_cleans_marker(self):
        codex_roles.install(self.repo)
        self.env['SDLC_CODEX_TRANSPORT']='subagent'
        p=self.role('timeout')
        self.assertNotEqual(p.returncode,0)
        self.assertFalse((self.rec/'scout-L1.md').exists())
        self.assertFalse(list(self.rec.glob('*.running')))
        request=json.loads((self.rec/'scout-L1.request.json').read_text())
        self.assertEqual(request['status'],'failed')

    # T-0507: the native exchange binds each request to the dispatched profile fingerprint. A real waiter process and the CLI responder.
    WAITER=('import sys;sys.path.insert(0,sys.argv[1]);import codex_roles,codex_exchange\n'
            'if sys.argv[4]:codex_roles.fingerprint=lambda agent:sys.argv[4]\n'
            'sys.exit(codex_exchange.wait_for_agent("scout","L1","Read seed",sys.argv[3],"low",sys.argv[2],float(sys.argv[5])))')
    SCOUT_BODY='## Map\n- seed.txt:1: fixture\n\n## Entry points\nseed.txt\n\n## Not found\nNone\n'

    def native_waiter(self,name,fake=''):
        """Start a scout L1 waiter child; fake, when given, is the fingerprint its process computes at dispatch."""
        request=self.step/(name+'.request.json')
        proc=subprocess.Popen(['python3','-c',self.WAITER,str(ROOT/'scripts'),str(request),codex_roles.models()['scout']['L1'][0],fake,str(DEADLINE)],
                              cwd=self.repo,env=self.env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:self.wait_for(request.exists,directory=self.rec,owner=proc)
        except BaseException:
            if proc.poll() is None:proc.kill();proc.communicate()
            raise
        return proc,request

    def native_respond(self,request,text,failed=False):
        report=request.parent/(request.name.split('.')[0]+'.report.txt');report.write_text(text)
        cmd=['python3',str(ROOT/'scripts/codex_exchange.py'),str(request),str(report)]+(['--failed'] if failed else [])
        return subprocess.run(cmd,cwd=self.repo,env=self.env,capture_output=True,text=True,timeout=DEADLINE)

    def test_native_exchange_enforces_the_dispatched_profile_binding(self):
        fp=codex_roles.fingerprint('sdlc-scout-l1')
        proc,request=self.native_waiter('bind')
        try:
            response=Path(json.loads(request.read_text())['response_path'])
            for label,first,said in (('missing','','stated no loaded profile fingerprint'),('stale','profile: 0.0.0+stale\n\n','loaded profile 0.0.0+stale')):
                done=self.native_respond(request,first+self.SCOUT_BODY)
                self.assertEqual(done.returncode,2,f'a report with a {label} profile line must be refused: {done.stderr}')
                self.assertIn(said,done.stderr,label)
                self.assertFalse(response.exists(),label+': a refused report writes no response file')
                self.assertEqual(json.loads(request.read_text())['status'],'waiting',label)
            self.assertEqual(json.loads(request.read_text())['profile_fingerprint'],fp)
            done=self.native_respond(request,'profile: '+fp+'\n\n'+self.SCOUT_BODY)
            self.assertEqual(done.returncode,0,done.stderr)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,0,stderr)
            final=json.loads(request.read_text());event=json.loads(stdout)
            self.assertEqual((final['status'],final['profile_fingerprint'],final['profile_check']),('received',fp,'ready'))
            self.assertEqual((event['is_error'],event['profile_fingerprint'],event['profile_check']),(False,fp,'ready'))
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()
        # A response file written past respond(): the waiter runs the same check against its own payload.
        proc,request=self.native_waiter('direct')
        try:
            payload=json.loads(request.read_text())
            response=Path(payload['response_path']);temp=response.with_suffix('.tmp')
            temp.write_text(json.dumps(dict(request_id=payload['request_id'],report='profile: 0.0.0+stale\n\n'+self.SCOUT_BODY,is_error=False))+'\n')
            temp.replace(response)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,1,stderr)
            final=json.loads(request.read_text());event=json.loads(stdout)
            self.assertEqual((final['status'],final['profile_check']),('failed','refused'))
            self.assertIn('refused: sdlc-scout-l1 loaded profile 0.0.0+stale',final['error'])
            self.assertIn('the attempt binding is '+fp,final['error'])
            self.assertEqual((event['is_error'],event['profile_check']),(True,'refused'))
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()

    def test_native_exchange_binding_survives_profile_change_after_dispatch(self):
        fake='0.0.0+dispatched';live=codex_roles.fingerprint('sdlc-scout-l1')
        self.assertNotEqual(fake,live)
        # The waiter dispatched with `fake`; the responder process computes `live`, as after a plugin update mid-run.
        proc,request=self.native_waiter('changed',fake=fake)
        try:
            done=self.native_respond(request,'profile: '+live+'\n\n'+self.SCOUT_BODY)
            self.assertEqual(done.returncode,2,'the live fingerprint is not the dispatched binding: '+done.stderr)
            self.assertIn('the attempt binding is '+fake,done.stderr)
            payload=json.loads(request.read_text())
            self.assertEqual((payload['status'],payload['profile_fingerprint']),('waiting',fake))
            done=self.native_respond(request,'profile: '+fake+'\n\n'+self.SCOUT_BODY)
            self.assertEqual(done.returncode,0,done.stderr)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,0,stderr)
            final=json.loads(request.read_text());event=json.loads(stdout)
            self.assertEqual((final['status'],final['profile_fingerprint'],final['profile_check']),('received',fake,'ready'))
            self.assertEqual((event['profile_fingerprint'],event['profile_check']),(fake,'ready'))
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()

    def test_native_exchange_failed_response_needs_no_profile_line(self):
        reason='could not finish: the fixture tool is missing'
        proc,request=self.native_waiter('gaveup')
        try:
            done=self.native_respond(request,'\n'+reason+'\nsecond line of detail\n',failed=True)
            self.assertEqual(done.returncode,0,done.stderr)
            stdout,stderr=proc.communicate(timeout=DEADLINE)
            self.assertEqual(proc.returncode,1,stderr)
            final=json.loads(request.read_text());event=json.loads(stdout)
            self.assertEqual(final['status'],'failed')
            self.assertEqual(final.get('error'),'native agent reported failure: '+reason)
            self.assertEqual(final.get('profile_check'),'not-checked')
            self.assertTrue(event['is_error'])
            self.assertIn(reason,event['result']);self.assertIn('second line of detail',event['result'])
            self.assertEqual(event.get('profile_check'),'not-checked')
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()

    def test_fanout_uses_codex(self):
        import fanout
        previous=os.environ.get('SDLC_BACKEND')
        try:
            os.environ['SDLC_BACKEND']='codex'
            command=fanout.default_driver('work/handoff.md')
            argv=shlex.split(command)
            self.assertEqual(os.path.basename(argv[1]),'codex_exec.py')
            self.assertNotEqual(os.path.basename(argv[0]),'claude')
            self.assertNotIn('--agent',argv)
            os.environ['SDLC_BACKEND']='wrong'
            with self.assertRaises(fanout.Refuse):fanout.default_driver('work/handoff.md')
        finally:
            if previous is None:os.environ.pop('SDLC_BACKEND',None)
            else:os.environ['SDLC_BACKEND']=previous

    # T-0372: solo through the native transport creates, waits on and records a request exchange; no model, no nested CLI.
    def solo_launch(self,tier,timeout=DEADLINE):
        ticket=self.base/'ticket'; ticket.mkdir(exist_ok=True)
        (ticket/'handoff.md').write_text('## Goal\nProbe.\n')
        env=dict(self.env,SDLC_CODEX_TRANSPORT='subagent',SDLC_CODEX_TIMEOUT_SECONDS=str(timeout))
        env.pop('SDLC_ATTEMPT_ID',None)
        proc=subprocess.Popen(['python3',str(ROOT/'scripts/solo_run.py'),'run','--backend','codex','--task-dir',str(ticket),
                               '--tier',tier,'--brief','Transport probe','--cwd',str(self.repo),'--no-worktree'],
                              cwd=self.repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        return proc,ticket

    def solo_requests(self,ticket,proc,known=()):
        return self.wait_for(lambda:[r for r in order.records_dir(ticket).glob('solo-*.request.json') if r not in known],directory=order.records_dir(ticket),owner=proc)

    def solo_respond(self,request,text=None,failed=False):
        # T-0507: a normal response states the request's dispatched profile fingerprint on its first line.
        if text is None:text='profile: '+json.loads(request.read_text())['profile_fingerprint']+'\n## Result\nsolo fixture done'
        report=request.parent/(request.stem+'.report.txt');report.write_text(text)
        cmd=['python3',str(ROOT/'scripts/codex_exchange.py'),str(request),str(report)]+(['--failed'] if failed else [])
        done=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(done.returncode,0,done.stderr)

    def solo_records(self,ticket):
        return [json.loads(l) for l in (order.records_dir(ticket)/'runs.jsonl').read_text().splitlines()]

    def test_solo_native_exchange_levels(self):
        for tier,agent,effort in (('L1','sdlc-solo-l1','medium'),('L2','sdlc-solo-l2','high'),('L3','sdlc-solo-l3','xhigh')):
            with self.subTest(tier=tier):
                (order.records_dir(self.base/'ticket')/'runs.jsonl').unlink(missing_ok=True)
                known=tuple(order.records_dir(self.base/'ticket').glob('solo-*.request.json'))
                proc,ticket=self.solo_launch(tier)
                try:
                    request=self.solo_requests(ticket,proc,known)[0]
                    payload=json.loads(request.read_text())
                    self.assertEqual((payload['agent'],payload['role'],payload['level'],payload['status'],payload['effort']),(agent,'solo',tier,'waiting',effort))
                    self.assertIn('Transport probe',payload['prompt'])
                    self.assertEqual(payload['profile_fingerprint'],codex_roles.fingerprint(agent))
                    self.solo_respond(request)
                    stdout,stderr=proc.communicate(timeout=DEADLINE)
                    self.assertEqual(proc.returncode,0,stderr)
                    self.assertIn('solo fixture done',stdout)
                finally:
                    if proc.poll() is None:proc.kill();proc.communicate()
                self.assertEqual(json.loads(request.read_text())['status'],'received')
                self.assertEqual([p.name for p in order.records_dir(ticket).iterdir() if p.name.startswith('solo-') and not p.name.endswith('.request.json') and not p.name.endswith('.report.txt') and not (p.name.startswith('solo-L') and p.name.endswith('.md'))],[])
                self.assertEqual(len([p for p in order.records_dir(ticket).iterdir() if p.name.startswith(f'solo-{tier}-') and p.name.endswith('.md')]),1,'T-0485: one solo result file')
                rec=self.solo_records(ticket)[-1]
                self.assertEqual((rec['backend'],rec['transport'],rec['role'],rec['level'],rec['model'],rec['exit_code']),('codex','subagent','solo',tier,'gpt-6.1-sol',0))
                self.assertIsNone(rec['cost_usd']);self.assertTrue(rec['cost_reason'])
                self.assertEqual((rec['profile_fingerprint'],rec['profile_check']),(codex_roles.fingerprint(agent),'ready'))
                self.assertEqual(json.loads(request.read_text())['profile_fingerprint'],codex_roles.fingerprint(agent))
                self.assertFalse((self.base/'probe.json').exists(),'a nested codex exec ran')

    def test_solo_native_response_failure(self):
        proc,ticket=self.solo_launch('L2')
        try:
            request=self.solo_requests(ticket,proc)[0]
            self.solo_respond(request,'agent could not finish',failed=True)
            proc.communicate(timeout=DEADLINE)
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()
        self.assertNotEqual(proc.returncode,0)
        self.assertEqual(json.loads(request.read_text())['status'],'failed')
        rec=self.solo_records(ticket)[-1]
        self.assertEqual((rec['backend'],rec['transport']),('codex','subagent'))
        self.assertNotEqual(rec['exit_code'],0)

    def test_solo_native_timeout(self):
        proc,ticket=self.solo_launch('L1',timeout=2)
        try:
            request=self.solo_requests(ticket,proc)[0]
            stdout,stderr=proc.communicate(timeout=DEADLINE)
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()
        self.assertNotEqual(proc.returncode,0)
        self.assertEqual(json.loads(request.read_text())['status'],'failed')
        self.assertIn('timed out',stderr)
        rec=self.solo_records(ticket)[-1]
        self.assertEqual((rec['backend'],rec['transport']),('codex','subagent'))
        self.assertIsNone(rec['cost_usd'])

    def test_solo_native_rerun_keeps_earlier_request(self):
        proc,ticket=self.solo_launch('L2')
        try:
            first=self.solo_requests(ticket,proc)[0]
            self.solo_respond(first,failed=True);proc.communicate(timeout=DEADLINE)
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()
        before=first.read_text()
        proc,ticket=self.solo_launch('L2')
        try:
            second=self.solo_requests(ticket,proc,known=(first,))[0]
            self.assertNotEqual(first,second)
            self.assertEqual(first.read_text(),before)
            self.solo_respond(second);proc.communicate(timeout=DEADLINE)
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()
        self.assertEqual(proc.returncode,0)
        self.assertEqual(first.read_text(),before)
        self.assertEqual(len(self.solo_records(ticket)),2)


if __name__=='__main__':
    unittest.main()
