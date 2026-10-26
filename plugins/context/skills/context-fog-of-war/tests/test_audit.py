import unittest,tempfile,json,os,sys,io,contextlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import audit
FIXTURE=Path(__file__).resolve().parent/'fixtures'/'contract-audit'
CATALOG={'components':{'Tile':{},'PriceTile':{},'InfoTile':{},'Summary':{'type':'object','properties':{'title':{'type':'string'},'rows':{'type':'array'}},'required':['title','rows'],'additionalProperties':False}}}
def surface(i,kind,paths,load='full',**kw):return dict(id=i,kind=kind,paths=paths,load=load,**kw)
def run(files,mapping):
 with tempfile.TemporaryDirectory() as t:
  for rel,body in files.items():
   p=Path(t)/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body if isinstance(body,str) else json.dumps(body))
  base={'version':1,'entities':{'fromJson':[{'path':'catalog.json','pointer':'/components'}]}}
  base['surfaces']=[surface('catalog','catalog',['catalog.json'],authority=True)]+mapping.pop('surfaces',[])
  base.update(mapping);report=audit.scan(t,base)
  return report
def hits(report,detector):return [f for f in report['findings'] if f['detector']==detector]
class Audit(unittest.TestCase):
 def test_conflict(self):
  rules={'catalog.json':CATALOG,'guide.json':{'InfoTile':{'notFor':[{'why':'an item with a price to order'}]}}}
  m=lambda:{'surfaces':[surface('guide','catalog',['guide.json']),surface('skill','skill',['skill.md'])],'topics':['order']}
  bad=run(dict(rules,**{'skill.md':'A priced item to order is one InfoTile each.\n'}),m())
  good=run(dict(rules,**{'skill.md':'A priced item to order is one PriceTile each.\n'}),m())
  self.assertEqual(len(hits(bad,'cross-surface-conflict')),1);self.assertEqual(hits(bad,'cross-surface-conflict')[0]['entities'],['InfoTile'])
  self.assertEqual(hits(good,'cross-surface-conflict'),[])
  m2=m();m2['surfaces'][0]['scope']='a';m2['surfaces'][1]['scope']=['b']
  self.assertEqual(hits(run(dict(rules,**{'skill.md':'A priced item to order is one InfoTile each.\n'}),m2),'cross-surface-conflict'),[])
 def test_undefined_reference(self):
  m=lambda:{'surfaces':[surface('skill','skill',['skill.md'])]}
  bad=run({'catalog.json':CATALOG,'skill.md':'Always use a GalleryTile for photos.\n'},m())
  good=run({'catalog.json':CATALOG,'skill.md':'Always use a PriceTile for prices.\n'},m())
  self.assertEqual([f['entities'] for f in hits(bad,'undefined-reference')],[['GalleryTile']]);self.assertEqual(hits(good,'undefined-reference'),[])
 def test_schema_mismatch(self):
  m=lambda:{'schemas':[{'schema':'catalog.json#/components/Summary','instances':[{'paths':['examples/*.json'],'pointer':'/nodes/*'},{'paths':['repair.md'],'snippets':'fenced'}]}]}
  valid={'title':'Done','rows':[]}
  bad=run({'catalog.json':CATALOG,'examples/a.json':{'nodes':[valid,{'title':'Done'}]},'repair.md':'Send:\n```json\n{"title":"Done","rows":[],"reference":"x"}\n```\n'},m())
  good=run({'catalog.json':CATALOG,'examples/a.json':{'nodes':[valid]},'repair.md':'Send:\n```json\n{"title":"Done","rows":[]}\n```\n'},m())
  got=hits(bad,'schema-mismatch');self.assertEqual(sorted(f['evidence'][0]['path'] for f in got),['examples/a.json','repair.md'])
  self.assertEqual(hits(good,'schema-mismatch'),[])
  self.assertEqual(audit.validate({'a':1},{'propertyNames':{'pattern':'^b'}},{},'',set()),[])
 def test_stale_generated(self):
  m=lambda:{'surfaces':[surface('prompt','prompt',['prompt.md'])],'generated':[{'output':'out.gen.js','sources':['prompt.md'],'embedded':True,'mtime':False}]}
  src='Answer in one short sentence before any surface.\nEvery surface carries "one" primary action.\n'
  bad=run({'catalog.json':CATALOG,'prompt.md':src,'out.gen.js':'export const P='+json.dumps(src.replace('"one" primary','"two" primary'))+'\n'},m())
  good=run({'catalog.json':CATALOG,'prompt.md':src,'out.gen.js':'export const P='+json.dumps(src)+'\n'},m())
  self.assertEqual([f['evidence'][0]['line'] for f in hits(bad,'stale-generated')],[2]);self.assertEqual(hits(good,'stale-generated'),[])
 def test_stale_generated_mtime(self):
  with tempfile.TemporaryDirectory() as t:
   Path(t,'catalog.json').write_text(json.dumps(CATALOG));Path(t,'src.md').write_text('x\n');Path(t,'out.gen.js').write_text('x\n')
   os.utime(Path(t,'out.gen.js'),(1000,1000));m={'version':1,'surfaces':[],'generated':[{'output':'out.gen.js','sources':['src.md']}]}
   self.assertEqual(hits(audit.scan(t,m),'stale-generated')[0]['confidence'],'low')
   os.utime(Path(t,'src.md'),(500,500));self.assertEqual(hits(audit.scan(t,m),'stale-generated'),[])
 def test_index_only_rule(self):
  skill='---\ndescription: priced items to order\n---\nA priced item to order is one PriceTile each, never a hand-built Tile.\n'
  m=lambda:{'surfaces':[surface('skill','skill',['skill.md'],'index-only',index={'frontmatter':'description'}),surface('grammar','prompt',['grammar.md'])]}
  bad=run({'catalog.json':CATALOG,'skill.md':skill,'grammar.md':'Answer briefly.\n'},m())
  good=run({'catalog.json':CATALOG,'skill.md':skill,'grammar.md':'A priced item to order is one PriceTile, never a hand-built Tile.\n'},m())
  self.assertEqual([f['metrics']['rules'] for f in hits(bad,'index-only-rule')],[1]);self.assertEqual(hits(good,'index-only-rule'),[])
  none=run({'catalog.json':CATALOG,'skill.md':skill},{'surfaces':[surface('skill','skill',['skill.md'],'unknown')]})
  self.assertEqual([c['state'] for c in none['coverage'] if c['detector']=='index-only-rule'],['abstained'])
 def test_modality_leak(self):
  m=lambda:{'surfaces':[surface('persona','persona',['persona.md'],modalityFree=True)]}
  bad=run({'catalog.json':CATALOG,'persona.md':'You host a cafe.\nShow specials as PriceTile entries.\n'},m())
  good=run({'catalog.json':CATALOG,'persona.md':'You host a cafe.\nOffer the daily specials with their prices.\n'},m())
  self.assertEqual([f['evidence'][0]['line'] for f in hits(bad,'modality-leak')],[2]);self.assertEqual(hits(good,'modality-leak'),[])
  code="const p = {\n  persona:\n    'You host a cafe.',\n  skills: 'Use a PriceTile.',\n}\n"
  scoped=run({'catalog.json':CATALOG,'p.ts':code},{'surfaces':[surface('persona','persona',['p.ts'],modalityFree=True,regions=[{'start':'^\\s+persona:','end':'^\\s+[a-z]+:'}])]})
  self.assertEqual(hits(scoped,'modality-leak'),[])
 def test_generic_oracle(self):
  m=lambda:{'surfaces':[surface('evals','oracle',['evals.json'],'none')]}
  bad=run({'catalog.json':CATALOG,'evals.json':{'expect':'Tile'}},m())
  good=run({'catalog.json':CATALOG,'evals.json':{'expect':'PriceTile'}},m())
  self.assertEqual([f['entities'] for f in hits(bad,'generic-oracle')],[['Tile']]);self.assertEqual(hits(good,'generic-oracle'),[])
 def test_discovery_abstains(self):
  r2=audit.scan(FIXTURE,None)
  self.assertIn('skill',[s['kind'] for s in r2['inventory']]);self.assertTrue(all(s['load']=='unknown' for s in r2['inventory']))
  self.assertEqual({c['detector']:c['state'] for c in r2['coverage']}['index-only-rule'],'abstained')
 def test_link(self):
  m=json.loads((FIXTURE/'mapping.json').read_text());r=audit.scan(FIXTURE,m)
  got=audit.link(r,'The model drew an InfoTile for priced menu items to order and the oracle failed')
  self.assertEqual(got['query']['entities'],['InfoTile']);paths=[x['path'] for x in got['surfaces']]
  self.assertIn('skills/menu.md',paths);self.assertIn('catalog/selection.json',paths)
  self.assertIn('phrase',next(x for x in got['surfaces'] if x['path']=='skills/menu.md')['matched'])
  self.assertTrue(got['auditFindings'])
  self.assertEqual(audit.link(r,'nothing related here at all')['surfaces'],[])
  with tempfile.TemporaryDirectory() as t:
   rp,dp=Path(t)/'r.json',Path(t)/'s.json';rp.write_text(json.dumps(r))
   dp.write_text(json.dumps({'findings':[{'id':'f1','title':'Drew a GalleryTile','evidence':[{'excerpt':'reach for a GalleryTile when the guest asks'}]}],'diagnostics':{'findings':[{'id':'diag-1','title':'unrelated'}]}}))
   out=io.StringIO()
   with contextlib.redirect_stdout(out):self.assertEqual(audit.main(['link','--report',str(rp),'--finding','f1','--data',str(dp),'--json']),0)
   got=json.loads(out.getvalue());self.assertIn('skills/menu.md',[x['path'] for x in got['surfaces']])
   with self.assertRaises(ValueError):audit.main(['link','--report',str(rp),'--finding','missing','--data',str(dp)])
 def test_include_exclude_list(self):
  code="// Use a PriceTile for prices.\nconst x = 'Use a GalleryTile';\n// Use a InfoTile for notes.\n"
  for inc in ('^//',['^//','^#']):
   r=run({'catalog.json':CATALOG,'p.ts':code},{'surfaces':[surface('p','prompt',['p.ts'],include=inc,exclude=['InfoTile'])]})
   self.assertEqual(hits(r,'undefined-reference'),[])
   self.assertEqual(sorted(n for n,at in r['index']['entities'].items() if at[0][0]=='p.ts'),['PriceTile'])
 def test_link_scoped_to_statements(self):
  code="const modules = load('the agent prompts folder here');\nconst p = {\n  persona:\n    'Read the agent prompts folder here first.',\n}\n"
  with tempfile.TemporaryDirectory() as t:
   Path(t,'catalog.json').write_text(json.dumps(CATALOG));Path(t,'p.ts').write_text(code)
   m={'version':1,'entities':{'fromJson':[{'path':'catalog.json','pointer':'/components'}]},'surfaces':[surface('p','prompt',['p.ts'],regions=[{'start':'^\\s+persona:','end':'^}'}])]}
   got=audit.link(audit.scan(t,m),'the model ignored the agent prompts folder here')
   self.assertEqual([(x['path'],x['lines']) for x in got['surfaces']],[('p.ts',[4])])
 def test_link_reads_frontmatter(self):
  skill='---\nname: menu\ndescription: Use when the guest wants to order from the menu.\n---\nBody line.\n'
  for index in ({},{'index':{'frontmatter':'description'}}):
   with tempfile.TemporaryDirectory() as t:
    Path(t,'catalog.json').write_text(json.dumps(CATALOG));Path(t,'SKILL.md').write_text(skill)
    m={'version':1,'entities':{'fromJson':[{'path':'catalog.json','pointer':'/components'}]},'surfaces':[surface('s','skill',['SKILL.md'],**index)]}
    got=audit.link(audit.scan(t,m),'the guest wants to order from the menu but got nothing')
    self.assertEqual([(x['path'],x['lines']) for x in got['surfaces']],[('SKILL.md',[3])])
 def test_text_summary_limits(self):
  self.assertIn('limit: Conflict precision',audit.summary(run({'catalog.json':CATALOG},{})))
 def test_modality_evidence_cap(self):
  leak=lambda k:hits(run({'catalog.json':CATALOG,'persona.md':'You host a cafe.\n'+''.join('Show item %d as a PriceTile.\n'%i for i in range(k))},{'surfaces':[surface('persona','persona',['persona.md'],modalityFree=True)]}),'modality-leak')[0]
  f=leak(7);self.assertEqual([e['line'] for e in f['evidence']],list(range(2,9)));self.assertEqual(f['metrics']['statements'],7);self.assertNotIn('first',f['observation'])
  f=leak(60);self.assertEqual(len(f['evidence']),50);self.assertEqual((f['metrics']['statements'],f['metrics']['evidenceShown']),(60,50));self.assertIn('first 50 of 60',f['observation'])
 def test_mapping_surface_warning(self):
  warn=lambda r:[i for i in r['issues'] if 'declares no' in i]
  skill=lambda:surface('s','skill',['s.md'])
  self.assertEqual(len(warn(run({'catalog.json':CATALOG,'s.md':'x\n'},{'surfaces':[skill()]}))),2)
  both={'surfaces':[skill(),surface('r','check',['r.md']),surface('t','tool',['t.json'])]}
  self.assertEqual(warn(run({'catalog.json':CATALOG,'s.md':'x\n','r.md':'x\n','t.json':{}},both)),[])
  unmatched={'surfaces':[skill(),surface('r','check',['missing/*.md']),surface('t','tool',['t.json'])]}
  self.assertEqual(len(warn(run({'catalog.json':CATALOG,'s.md':'x\n','t.json':{}},unmatched))),1)
  declared={'surfaces':[skill()],'noSurface':{'repair':'the producer has no validator','tool':'no tools are sent'}}
  self.assertEqual(warn(run({'catalog.json':CATALOG,'s.md':'x\n'},declared)),[])
  self.assertEqual(warn(run({'catalog.json':CATALOG,'examples/a.json':{}},{'surfaces':[surface('ex','exemplar',['examples/*.json'])]})),[])
  self.assertEqual(warn(audit.scan(FIXTURE,None)),[])
  self.assertEqual(warn(audit.scan(FIXTURE,json.loads((FIXTURE/'mapping.json').read_text()))),[])
 def test_fixture_cli(self):
  with tempfile.TemporaryDirectory() as t:
   out=Path(t)/'r.json'
   with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(audit.main(['scan','--root',str(FIXTURE),'--mapping',str(FIXTURE/'mapping.json'),'--out',str(out)]),0)
   r=json.loads(out.read_text());self.assertEqual({f['detector'] for f in r['findings']},set(audit.DETECTORS))
   self.assertTrue(all(f['status']=='candidate' and f['evidence'] and f['evidence'][0]['line'] for f in r['findings']))
   with self.assertRaises(SystemExit),contextlib.redirect_stderr(io.StringIO()):audit.main(['scan','--root',str(FIXTURE),'--out',str(FIXTURE/'r.json')])
if __name__=='__main__':unittest.main()
