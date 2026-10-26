import unittest,tempfile,json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from wrapped import parse_calls,pair_outputs,expand_pairs,read_requests,corroborate
from projections import component_projections, prose_projections
from diagnostics import explicit_failure
class Routing(unittest.TestCase):
 def test_multi_cat(self):self.assertEqual(read_requests('cat one.md two.md; node x'),[('one.md',None,None),('two.md',None,None)])
 def test_no_scripts(self):self.assertEqual(read_requests('python3 <<\'PY\'\ncat secret.md\nPY'),[])
 def test_no_redirect(self):self.assertEqual(read_requests('cat one.md > other.md'),[])
 def test_indexed_batch(self):
  code='const results=await Promise.allSettled([tools.exec_command({cmd:"cat a"}),tools.exec_command({cmd:"cat b"})]);for(let i=0;i<results.length;i++)text({i,...results[i]});'
  calls=parse_calls(code);self.assertEqual(len(calls),2)
  out=[{'type':'input_text','text':json.dumps({'i':i,'status':'fulfilled','value':{'output':str(i),'exit_code':0}})} for i in range(2)]
  paired=pair_outputs(out,calls);self.assertEqual(len(expand_pairs(calls,paired)),2)
  out.reverse();self.assertIsNone(pair_outputs(out,calls))
 def test_merged_truncated_batch(self):
  # Codex merged three indexed outputs into one truncated text block: block count is not call count.
  code='const r = await Promise.allSettled([\ntools.exec_command({cmd:"cat a/SKILL.md b/SKILL.md",max_output_tokens:14000}),\ntools.exec_command({cmd:"cat docs/internals.md",max_output_tokens:12000}),\ntools.exec_command({cmd:"wc -l scripts/*.py",max_output_tokens:6000})\n]); for (let i=0;i<r.length;i++)text({i,...r[i]});\n'
  calls=parse_calls(code);self.assertEqual(len(calls),3);self.assertEqual([c['index'] for c in calls],[0,1,2])
  merged='Warning: truncated output (original token count: 19315)\nTotal output lines: 3\n\n'+'\n'.join(json.dumps({'i':i,'status':'fulfilled','value':{'exit_code':0,'output':'x'}}) for i in range(3))
  out=[{'type':'input_text','text':'Script completed\nWall time 0.1 seconds\nOutput:\n'},{'type':'input_text','text':merged}]
  self.assertIsNone(pair_outputs(out,calls))
  self.assertIsNone(parse_calls(code.replace('for (let i=0;i<r.length;i++)','for (let i=r.length-1;i>=0;i--)')))
 def test_dynamic_rejected(self):self.assertIsNone(parse_calls('const r=await Promise.all([tools.exec_command({cmd:secret})]);text(r);'))
 def test_reverse_loop_rejected(self):self.assertIsNone(parse_calls('const r=await Promise.all([tools.exec_command({cmd:"cat x"})]);for(let i=r.length-1;i>=0;i--)text({i,...r[i]});'))
 def test_source_witness(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'one.md';p.write_text('Long enough source content to disambiguate this single complete return.\n')
   self.assertEqual(corroborate(p,[Path(t).resolve()],p.read_text()),'read');self.assertIsNone(corroborate(p,[],p.read_text()));self.assertIsNone(corroborate(p,[Path(t).resolve()],'not the source'))
 def test_projection(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t).resolve();p=root/'contract.json';data={'families':[{'id':'fields','anatomy':'a meaningful returned contract'}],'version':1};p.write_text(json.dumps(data));packet={'schemaVersion':1,'records':[{'id':'fields','contract':data['families'][0]}],'sources':[{'path':'contract.json','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}]};cmd='node scripts/component-context.mjs --records fields --record-only'
   self.assertEqual(len(component_projections(cmd,t,json.dumps(packet),[root])),1)
   self.assertEqual(len(component_projections('python3 scripts/run.py component-context.mjs --records fields --record-only',t,json.dumps(packet),[root])),1)
   self.assertEqual(component_projections('python3 unrelated.py component-context.mjs fields',t,json.dumps(packet),[root]),[])
   packet['records'][0]['contract']['anatomy']='forged';self.assertEqual(component_projections(cmd,t,json.dumps(packet),[root]),[])
 def test_unattributed_hash(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'contract.json';p.write_text('{"id":"fields"}');packet={'schemaVersion':1,'contract':{'id':'fields'},'id':'fields','sources':[{'path':'contract.json','sha256':'bad'}]};self.assertEqual(component_projections('node scripts/component-context.mjs fields',t,json.dumps(packet),[Path(t).resolve()]),[])
 def test_prose_page(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t).resolve();p=root/'guide.md';p.write_text('Exact prose content\n');packet={'source':'guide.md','page':0,'pages':1,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'content':p.read_text()};cmd='python3 scripts/run.py read guide.md'
   self.assertEqual(len(prose_projections(cmd,t,json.dumps(packet),[root])),1)
   self.assertEqual(prose_projections(cmd,t,json.dumps(packet),[]),[])
   packet['content']='forged';self.assertEqual(prose_projections(cmd,t,json.dumps(packet),[root]),[])
 def test_failure_envelopes(self):self.assertTrue(explicit_failure({'exit_code':1,'output':'missing'}));self.assertFalse(explicit_failure({'exit_code':0,'output':'No such file or directory is an example'}))
if __name__=='__main__':unittest.main()
