"""Delivery identity, completion and real CLI/hydration boundary regressions."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from diagnostics import diagnose, validate_diagnostics
from claude import hydrate
from wrapped import scoped_read_requests
from test_delivery_oracle import report, page, returned, write, resequence, BODY, CONTENT_HASH


def checked(data):
    result = diagnose(resequence(data))
    validate_diagnostics(result)
    return result


def detectors(data):
    return {f['detector'] for f in checked(data)['diagnostics']['findings']}


class DeliveryDiagnostics(unittest.TestCase):
    def test_complete_file_receipt_is_not_a_returned_body(self):
        data = report()
        returned(data, 'receipt', 'node registry --read docs/api.md --out /tmp/body', {
            'kind': 'complete-file', 'source': 'docs/api.md', 'complete': True,
            'sha256': CONTENT_HASH, 'output': '/tmp/body', 'next': None})
        write(data)
        self.assertIn('required-source-before-write', detectors(data))

    def test_missing_first_page_cannot_be_repaired_by_terminal_page(self):
        data = report(); page(data, 'last', start=5); write(data)
        self.assertIn('required-source-before-write', detectors(data))

    def test_hash_claim_does_not_replace_exact_content(self):
        data = report(); page(data)
        item = data['events'][-1]
        payload = json.loads(json.loads(item['toolCalls'][0]['output'])['output'])
        payload['content'] = 'wrong' + BODY[5:]
        raw = json.dumps({'exit_code': 0, 'output': json.dumps(payload)})
        item['toolCalls'][0]['output'] = raw; item['evidence']['text'] = raw
        write(data)
        self.assertIn('required-source-before-write', detectors(data))

    def test_different_identity_pages_never_merge(self):
        data = report(); page(data, 'first', end=5); page(data, 'last', start=5, identity='different'); write(data)
        self.assertIn('unfinished-continuation', detectors(data))

    def test_unicode_codepoint_ranges_and_hashes(self):
        body = 'a😀e\u0301𝄞z'; data = report()
        digest = hashlib.sha256(body.encode()).hexdigest()
        data['deliveryContract']['requiredSources'][0]['contentHash'] = digest
        for start, end in [(0, 3), (3, len(body))]:
            returned(data, 'p'+str(start), 'node registry --read docs/api.md', {
                'kind': 'source-body-page', 'source': 'docs/api.md', 'sha256': 'bound-identity',
                'contentSha256': digest, 'offset': start, 'end': end, 'total': len(body),
                'offsetUnit': 'Unicode code points', 'content': body[start:end], 'complete': end == len(body),
                'next': None if end == len(body) else {'args': ['--read', 'docs/api.md', str(end), 'bound-identity']}})
        write(data)
        self.assertNotIn('required-source-before-write', detectors(data))
        self.assertNotIn('unfinished-continuation', detectors(data))

    def test_search_pages_recover_metadata_without_becoming_bodies(self):
        data = report()
        for start in (0, 1):
            returned(data, 's'+str(start), 'node registry --find api', {
                'kind':'search-page', 'source':'docs/api.md', 'sha256':'search-identity',
                'offset':start, 'end':start+1, 'total':2, 'matches':[{'id':str(start)}],
                'complete':start==1, 'next':None if start else {'args':['--find','api','1','search-identity']}})
        write(data)
        result = detectors(data)
        self.assertIn('required-source-before-write', result)
        self.assertNotIn('unfinished-continuation', result)

    def test_legacy_offset_is_unknown_executable_continuation(self):
        data = report(); page(data, 'first', end=5)
        item=data['events'][-1]; envelope=json.loads(item['toolCalls'][0]['output'])
        packet=json.loads(envelope['output']); packet['next']={'offset':5,'sha256':packet['sha256']}
        envelope['output']=json.dumps(packet); raw=json.dumps(envelope)
        item['toolCalls'][0]['output']=raw; item['evidence']['text']=raw;write(data)
        result=checked(data)
        self.assertNotIn('unfinished-continuation', {f['detector'] for f in result['diagnostics']['findings']})
        row=next(x for x in result['diagnostics']['coverage'] if x['detector']=='unfinished-continuation')
        self.assertTrue(any('next.args' in x['reason'] for x in row['explanation']['gaps']))

    def test_invalid_observation_citation_cannot_establish_absence(self):
        data=report();write(data)
        data['deliveryContract']['observationWindow']['evidence']['excerpt']='not in the trace'
        self.assertNotIn('required-source-before-write', detectors(data))

    def test_invalid_exclusion_citation_cannot_establish_policy(self):
        data=report();data['deliveryContract']['evidence']['excerpt']='not in the trace'
        returned(data,'excluded','cat history/solution.md','body',[{'sourceId':'history','state':'read'}]);write(data)
        self.assertNotIn('excluded-source-read',detectors(data))

    def test_cut_limited_native_return_is_not_tool_truncation(self):
        data=report();data['deliveryContract']['requiredSources'][0].pop('contentHash')
        returned(data,'cut','cut -c 1-4 docs/api.md','alph',[{'sourceId':'api','state':'partial'}]);write(data)
        found=detectors(data)
        self.assertIn('incomplete-source-delivery',found);self.assertNotIn('truncation',found)

    def test_packet_source_base_is_explicit(self):
        data=report();data['deliveryContract']['sourceBase']='kit'
        data['deliveryContract']['requiredSources'][0]['path']='kit/docs/api.md'
        page(data);write(data)
        self.assertNotIn('required-source-before-write',detectors(data))

    def test_contract_mode_is_visible(self):
        data=report();data['deliveryContract']['mode']='retrospective-policy';write(data)
        result=checked(data)
        self.assertEqual(result['diagnostics']['delivery']['contractMode'],'retrospective-policy')
        self.assertTrue(all(f['metrics']['contractMode']=='retrospective-policy' for f in result['diagnostics']['findings']))

    def test_native_compound_reads_need_returned_source_witness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'docs').mkdir()
            body='Full source body with more than thirty two characters.\nSecond documented instruction.\n'
            (root/'docs/guide.md').write_text(body)
            for output, expected in [(body,True),('No body was returned.',False)]:
                trace=root/'trace.jsonl'
                records=[{'type':'assistant','cwd':str(root),'message':{'content':[{'type':'tool_use','id':'x','name':'Bash','input':{'command':'cd docs && wc -l guide.md; cat guide.md'}}]}},
                    {'type':'user','cwd':str(root),'message':{'content':[{'type':'tool_result','tool_use_id':'x','is_error':False,'content':output}]},'toolUseResult':{'stdout':output}}]
                trace.write_text('\n'.join(json.dumps(r) for r in records))
                data=hydrate(trace,root,include_children=False)
                exposures=[x for e in data['events'] if e['kind']=='result' for x in e['exposures']]
                self.assertEqual(bool(exposures),expected)
                if expected:
                    self.assertEqual(next(s['path'] for s in data['sources'] if s['id']==exposures[0]['sourceId']),'docs/guide.md')
                    self.assertIn('unverified',exposures[0]['basis'])

    def test_dynamic_and_script_commands_are_not_executed_or_attributed(self):
        self.assertEqual(scoped_read_requests('cd "$UNKNOWN" && cat guide.md','/repo'),[])
        self.assertEqual(scoped_read_requests("python3 -c 'print(\"cat guide.md\")'",'/repo'),[])
        self.assertEqual(scoped_read_requests('cat <<EOF\ncat guide.md\nEOF','/repo'),[])
        self.assertEqual(scoped_read_requests('cd one; cat guide.md','/repo'),[])

    def test_task_packet_complete_body_reference_and_partial_controls(self):
        packet={'kind':'task-packet','schemaVersion':1,'pathBase':'',
                'selection':{'role':'consumer','renderer':'html','components':['component:example']},
                'complete':True,'taskReady':False,'sha256':'packet-selection-hash',
                'bodies':[{'kind':'body','source':'docs/api.md','sourceSha256':CONTENT_HASH,
                    'sha256':CONTENT_HASH,'projection':'complete-file','complete':True,'content':BODY}],
                'references':[{'kind':'reference','source':'docs/reference.md','delivery':'reference-only'}]}
        for variant in ('complete','partial','reference-only','tampered-body','selected-records'):
            with self.subTest(variant=variant):
                data=report();obj=copy.deepcopy(packet)
                if variant=='reference-only':obj['bodies']=[];obj['references'].append({'kind':'reference','source':'docs/api.md','delivery':'reference-only'})
                if variant=='tampered-body':obj['bodies'][0]['content']='not the hashed content'
                if variant=='selected-records':obj['bodies'][0]['projection']='selected-json-records'
                content=json.dumps(obj,ensure_ascii=False,indent=2);split=len(content)//2
                for start,end in [(0,split),(split,len(content))]:
                    if variant=='partial' and start:continue
                    returned(data,'packet-'+str(start),'node registry --packet consumer html component:example --page '+str(start),{
                        'kind':'task-packet-page','sha256':'bound-task-packet','offset':start,'end':end,'total':len(content),
                        'offsetUnit':'Unicode code points in serialized metadata','content':content[start:end],
                        'complete':end==len(content),'next':None if end==len(content) else {'args':['--packet','consumer','html','component:example','--page',str(end),'bound-task-packet']}})
                write(data);found=detectors(data)
                self.assertEqual('required-source-before-write' in found,variant!='complete')
                self.assertEqual('unfinished-continuation' in found,variant=='partial')

    def test_task_packet_direct_body_and_exclusion(self):
        data=report();data['deliveryContract']['requiredSources']=[]
        returned(data,'packet','node registry --packet consumer html component:example',{
            'kind':'task-packet','complete':True,'bodies':[{'kind':'body','source':'history/solution.md',
                'projection':'complete-file','complete':True,'content':BODY,'sha256':CONTENT_HASH}],
            'references':[{'source':'history/unread.md','delivery':'reference-only'}]})
        write(data);result=checked(data)
        found=[f for f in result['diagnostics']['findings'] if f['detector']=='excluded-source-read']
        self.assertEqual(len(found),1);self.assertEqual(found[0]['metrics']['path'],'history/solution.md')

    def test_cli_contract_option_and_schema_integration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);trace=root/'trace.jsonl'
            trace.write_text(json.dumps({'type':'user','message':{'content':'A bounded test task.'}})+'\n')
            data=hydrate(trace,root,include_children=False);source=root/'session.json';source.write_text(json.dumps(data))
            contract=root/'contract.json';contract.write_text(json.dumps({'mode':'authored-replay'}))
            output=root/'diagnosed.json'
            command=[sys.executable,'-B',str(ROOT/'scripts/diagnostics.py'),'--data',str(source),'--out',str(output),'--delivery-contract',str(contract)]
            result=subprocess.run(command,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            from fog import validate
            validate(json.loads(output.read_text()))
            result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/engineer.py'),'--root',str(root/'library'),'--json','diagnose','--data',str(source),'--delivery-contract',str(contract)],text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('authored-replay',result.stdout)


if __name__=='__main__':unittest.main()
