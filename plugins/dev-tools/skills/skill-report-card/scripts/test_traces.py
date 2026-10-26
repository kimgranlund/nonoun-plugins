#!/usr/bin/env python3
import copy,json,tempfile,sys,unittest,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
from traces import parse
from scan_traces import collect,SKILL

def raw(rows):return ('\n'.join(json.dumps(x) for x in rows)+'\n').encode()
def fixture():return [{'type':'thread.started','thread_id':'private-thread'},{'type':'item.started','item':{'id':'x','type':'command_execution'}},{'type':'item.completed','item':{'id':'x','type':'command_execution','command':'cat /skills/base-ui/SKILL.md; echo private','aggregated_output':'éPRIVATE_MARKER','exit_code':0,'status':'completed'}},{'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':20,'output_tokens':30}}]
class TraceTests(unittest.TestCase):
    def test_log_only_positive(self):
        n=parse(raw(fixture()));self.assertEqual(n['recordedCommands'],1);self.assertEqual(n['loggedCommandOutputUtf8Bytes'],len('éPRIVATE_MARKER'.encode()));self.assertEqual(n['skillHints'],['base-ui']);self.assertEqual(n['reportedUsageEvents'][0]['input_tokens'],100);self.assertFalse(n['performanceEligible']);self.assertNotIn('PRIVATE_MARKER',json.dumps(n));self.assertNotIn('private-thread',json.dumps(n))
    def test_failures_are_not_task_success(self):
        r=fixture();r[2]['item']['exit_code']=1;n=parse(raw(r));self.assertEqual(n['recordedNonzeroExits'],1);self.assertEqual(n['recordedSuccessfulExits'],0);self.assertIsNone(n['attemptDenominator'])
    def test_duplicate_and_conflict(self):
        r=fixture();r.append(copy.deepcopy(r[2]));n=parse(raw(r));self.assertEqual(n['recordedCommands'],1);self.assertEqual(n['coverage']['counts']['duplicateCommandRecords'],1)
        r[-1]['item']['exit_code']=1;n=parse(raw(r));self.assertEqual(n['conflictingCommandIdentities'],1);self.assertEqual(n['loggedCommandOutputUtf8Bytes'],0);self.assertEqual(n['recordedSuccessfulExits'],0)
    def test_incomplete_and_mixed_threads(self):
        n=parse(raw(fixture()[:2]));self.assertEqual(n['unresolvedStartedCommands'],1);self.assertFalse(n['coverage']['completeCaptureEstablished'])
        r=fixture()+[{'type':'thread.started','thread_id':'different'}];self.assertEqual(parse(raw(r))['coverage']['stopReason'],'mixed-thread-identities')
    def test_no_substring_attribution(self):
        r=fixture();r[2]['item']['command']='echo base-ui-like';self.assertEqual(parse(raw(r))['skillHints'],[])
    def test_bounds_and_malformed(self):
        self.assertEqual(parse(raw(fixture()),max_records=1)['coverage']['stopReason'],'record-budget');n=parse(b'broken\n'+raw(fixture()),max_line_bytes=100);self.assertEqual(n['coverage']['counts']['malformedRecords'],1);self.assertGreater(n['coverage']['counts']['oversizedRecords'],0)
    def test_cli_privacy_and_discovery_without_manifest(self):
        with tempfile.TemporaryDirectory(prefix='trace-fixture-',dir='/private/tmp') as folder:
            root=Path(folder);p=root/'author.jsonl';p.write_bytes(raw(fixture()));before=p.read_bytes();out=root/'output'
            cli=subprocess.run([sys.executable,str(SKILL/'scripts/scan_traces.py'),'--root',str(root),'--output',str(out)],capture_output=True,text=True);self.assertEqual(cli.returncode,0,cli.stderr);self.assertLess(len(cli.stdout.encode()),4096);self.assertNotIn('PRIVATE_MARKER',cli.stdout+cli.stderr)
            for n in ('index.html','report-card.json','trace-observations.json'):self.assertNotIn('PRIVATE_MARKER',(out/n).read_text())
            self.assertIn('Observed in logs',(out/'index.html').read_text());self.assertEqual(p.read_bytes(),before);self.assertEqual(json.loads(cli.stdout)['qualifiedTraceFormats'],1)
    def test_exclusions_copies_and_budget(self):
        with tempfile.TemporaryDirectory(prefix='trace-fixture-',dir='/private/tmp') as folder:
            root=Path(folder);(root/'a.jsonl').write_bytes(raw(fixture()));(root/'b.ndjson').write_bytes(raw(fixture()));secret=root/'sessions';secret.mkdir();(secret/'private.jsonl').write_bytes(raw(fixture()));(root/'link.jsonl').symlink_to(secret/'private.jsonl')
            obs,index=collect([root],root/'output');self.assertEqual(len(obs),1);self.assertEqual(index['coverage']['counts']['exactCopies'],1);self.assertGreater(index['coverage']['counts']['excluded'],0)
            obs,index=collect([root],root/'output',max_entries=1);self.assertEqual(index['coverage']['stopReason'],'entry-budget')
if __name__=='__main__':unittest.main(verbosity=2)
