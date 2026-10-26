#!/usr/bin/env python3
"""CLI-first diagnosis, immutable experiments and conservative comparisons."""
import argparse
import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from library import default_root
from fog import validate
from diagnostics import diagnose as detect

VERSION = '6'

def read(path): return json.loads(Path(path).read_text())
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
def save(root, kind, value):
    value = dict(value, schemaVersion=1, analyzerVersion=VERSION)
    value.pop('id',None)
    identity = kind+'-'+digest(value)[:24]
    folder = Path(root)/'engineering'/kind
    folder.mkdir(parents=True, exist_ok=True)
    path = folder/(identity+'.json')
    record = dict(value, id=identity)
    # Publish complete bytes atomically without overwriting an existing record.
    fd, temp = tempfile.mkstemp(dir=folder, prefix='.pending-')
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(record,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
        try: os.link(temp,path)
        except FileExistsError:
            if read(path) != record: raise ValueError('Immutable record conflict')
    finally: os.unlink(temp)
    return record, path

def load(root, identity, kind):
    if not identity.startswith(kind+'-') or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in identity):
        raise ValueError('Invalid record ID')
    record=read(Path(root)/'engineering'/kind/(identity+'.json'))
    value={k:v for k,v in record.items() if k!='id'}
    if record.get('id')!=identity or kind+'-'+digest(value)[:24]!=identity:
        raise ValueError('Record integrity check failed')
    return record

def verify_refs(data, refs):
    events = {e['id']:e for e in data['events']}
    for ref in refs:
        if not ref.get('excerpt'): raise ValueError('Empty evidence')
        if 'eventId' in ref:
            if ref['eventId'] not in events or ref['excerpt'] not in events[ref['eventId']]['evidence']['text']:
                raise ValueError('Evidence excerpt does not match event')
        elif 'artifact' in ref:
            value = read(ref['artifact'])
            for part in ref.get('pointer','').split('/')[1:]:
                key = part.replace('~1','/').replace('~0','~')
                value = value[int(key)] if isinstance(value,list) else value[key]
            if json.loads(ref['excerpt']) != value: raise ValueError('Artifact evidence changed')
        else: raise ValueError('Evidence requires event or artifact')

def diagnosis(data, context):
    validate(data)
    data = detect(data)
    paths = {s['id']:s['path'] for s in data['sources']}
    findings = {}
    for f in data['diagnostics']['findings']:
        # Aggregate detector/source families: event renumbering cannot change identity.
        scope = sorted(paths[s] for s in f.get('sourceIds',[])) or ['session']
        key = 'F-'+digest([context.get('task'), f['detector'], scope])[:16]
        if key not in findings:
            findings[key] = dict(id=key, detector=f['detector'], scope=scope, observation=f['observation'],
                interpretation=f['hypothesis'], uncertainty=f['alternatives'], action=f['guidance'],
                verification=f['verification'], evidence=[], occurrences=0, triage=[])
        findings[key]['triage'].append(f['triage'])
        findings[key]['evidence'].extend(f['evidence']); findings[key]['occurrences'] += 1
    workflow_states = {}
    for w in data.get('workflows',[]):
        for stage in w['stages']:
            scope = w['id']+'/'+stage['kind']; workflow_states[scope] = stage['state']
            verify_refs(data, stage['evidence'])
            if stage['state'] == 'complete': continue
            key = 'F-'+digest([context.get('task'), 'workflow', scope])[:16]
            findings[key] = dict(id=key, detector='workflow', scope=[scope], observation=stage['summary'],
                interpretation='Workflow requirement is not established as complete.', uncertainty=[w.get('uncertainty','')],
                action=w['nextStep'], verification='Record completion evidence and assess acceptance separately.',
                evidence=stage['evidence'], occurrences=1, state=stage['state'])
    for f in findings.values(): verify_refs(data, f['evidence'])
    return dict(kind='diagnosis', createdAt=datetime.now(timezone.utc).isoformat(), context=context,
        inputHash=digest(data), adapter={'host':data['session'].get('host','codex'),'version':data['session'].get('adapterVersion','legacy'),'coverage':data['coverage']['warnings'],'mappingHash':data.get('bundle',{}).get('mappingHash')}, children=[{'agentId':c['agentId'],'parentEventId':c['parentEventId'],'diagnosis':diagnosis(c['report'],dict(context,task=str(context.get('task',''))+'/child:'+c['agentId']))} for c in data.get('childSessions',[]) if c['status']=='hydrated'], session=data['session'], findings=list(findings.values()),
        coverage=data['diagnostics']['coverage'], workflows=workflow_states,
        limits=data['diagnostics']['limits'], snapshot=data)

def assessment(path):
    if not path: return {}
    value = read(path)
    for key in ('mechanism','behavior','outcome'):
        entry=value.get(key)
        if entry is None: continue
        if entry.get('state') not in ('pass','fail','unknown'): raise ValueError('Invalid assessment state')
        if entry['state'] != 'unknown' and not entry.get('evidence'): raise ValueError('Assessment needs evidence')
        for ref in entry.get('evidence',[]):
            if 'artifact' not in ref: raise ValueError('Assessment requires artifact citations')
            verify_refs({'events':[]}, [ref])
    for name, amount in value.get('cost',{}).items():
        if not isinstance(amount,(int,float)) or isinstance(amount,bool) or not math.isfinite(amount) or amount<0: raise ValueError('Invalid measured cost')
        refs=value.get('costEvidence',{}).get(name,[])
        if not refs: raise ValueError('Measured cost requires evidence')
        verify_refs({'events':[]},refs)
    return value

def compare(before, after, experiment=None, mode="auto", experiment_type=None, experiment_contract=None, reassessments=None):
    reasons=[]
    for key in ('task','testSuite','runtime','budget','environment'):
        a,b=before['context'].get(key),after['context'].get(key)
        if a is None or b is None: reasons.append(key+': missing')
        elif a!=b: reasons.append(key+': changed')
    if before.get('adapter')!=after.get('adapter'): reasons.append('host, adapter version or extraction coverage changed')
    if before['analyzerVersion']!=after['analyzerVersion']: reasons.append('analyzer changed')
    revision_changed=before['context'].get('revision')!=after['context'].get('revision')
    if not before['context'].get('revision') or not after['context'].get('revision'): reasons.append('revision: missing')
    if revision_changed and not experiment: reasons.append('revision changed without registered experiment')
    if experiment:
        if experiment['baseline']!=before['id']: raise ValueError('Experiment baseline mismatch')
        if after.get('experiment')!=experiment['id']: reasons.append('run not linked to experiment')
        if not after.get('actualChange'): reasons.append('actual intervention missing')
    a={f['id']:f for f in before['findings']};b={f['id']:f for f in after['findings']}
    coverage={c['detector']:c['assessed'] for c in after['coverage']}
    transitions=[]
    for key in sorted(a.keys()|b.keys()):
        old,new=a.get(key),b.get(key);f=new or old
        if reasons: state='not assessable'
        elif old and new:
            state='not assessable' if new.get('state')=='unknown' else 'persists'
        elif new: state='new'
        elif f['detector']=='workflow':
            state='resolved' if after['workflows'].get(f['scope'][0])=='complete' else 'not assessable'
        else: state='signal no longer observed' if coverage.get(f['detector'],0)>0 else 'not assessable'
        transitions.append(dict(finding=key,state=state,detector=f['detector']))
    observations={k:after.get('assessment',{}).get(k,{'state':'unknown'}) for k in ('mechanism','behavior','outcome')}
    prior=before.get('assessment',{}).get('outcome',{}).get('state','unknown')
    current=observations['outcome']['state']
    improvement=not reasons and prior=='fail' and all(v['state']=='pass' for v in observations.values())
    regression=not reasons and prior=='pass' and current=='fail'
    verdict='Improvement observed in this controlled comparison.' if improvement else 'Outcome regressed.' if regression else 'Outcome improvement not established.'
    result = dict(kind='comparison',baseline=before['id'],run=after['id'],experiment=experiment['id'] if experiment else None,
        comparable=not reasons, limitations=reasons+['One comparison does not establish general reliability or causal attribution.'],
        transitions=transitions,observations=observations,verdict=verdict,
        nextAction='Keep the change provisionally; repeat on independent tasks.' if improvement else 'Inspect evidence; revise the experiment or collect missing measurements.',
        costDelta={k: v-before.get('assessment',{}).get('cost',{}).get(k,0) for k,v in after.get('assessment',{}).get('cost',{}).items() if k in before.get('assessment',{}).get('cost',{})})

    from comparison_layers import layers
    return layers(before,after,result,experiment,mode,experiment_type,experiment_contract,reassessments)

def summary(record):
    if record['kind']=='comparison':
        return '\n'.join([record['verdict'], 'Mode: '+record.get('comparisonMode','legacy'),
            'Evidence: '+str(len(record.get('evidenceChanges',{}).get('addedReturnedPaths',[])))+' added returned paths; '+str(len(record.get('evidenceChanges',{}).get('removedReturnedPaths',[])))+' removed. Counts are not outcome improvements.',
            *['Diagnosis '+t['finding']+': '+t['status'] for t in record.get('diagnosisChanges',[])],
            'Outcome scope: '+record.get('outcomeChanges',{}).get('scope','legacy'),
            'Context-engineering improvement: '+str(record.get('outcomeChanges',{}).get('contextEngineeringImprovement',False)),
            'Comparable: '+str(record['comparable']),
            *[k+': '+v['state'] for k,v in record['observations'].items()],
            *[t['finding']+': '+t['state'] for t in record['transitions']],
            'Next: '+record['nextAction'], 'Limits: '+'; '.join(record['limitations'])])
    if record['kind']=='experiment': return 'Proposed experiment: '+record['hypothesis']+'\nChange: '+record['intervention']+'\nVerify: '+record['criterion']
    lines=[f"Diagnosis: {len(record['findings'])} evidence-backed signals; not a defect count."]
    def benign(f):return bool(f.get('triage')) and all(t['state']=='likely-benign' for t in f['triage'])
    lines.append(str(sum(benign(f) for f in record['findings']))+' likely-benign groups retained for inspection; other signals still require review.')
    for f in sorted(record['findings'],key=lambda f:(benign(f),f['detector']!='workflow'))[:5]:
        lines.extend(['',f['id']+' · '+f['observation'],('Action: No corrective change proposed from this signal alone.' if benign(f) else 'Conditional action: '+f['action']),'Verify: '+f['verification'],
            'Uncertainty: '+'; '.join(f['uncertainty'])])
        for t in f.get('triage',[]):
            lines.append('Triage: '+t['state']+' — '+t['reason']+' Need: '+t['nextEvidence'])
        for e in f['evidence'][:2]: lines.append('Evidence: '+e.get('eventId',e.get('artifact',''))+' '+e.get('pointer','')+' — '+e['excerpt'][:180].replace('\n',' '))
    lines.append('\nDetector coverage (eligibility, not correctness):')
    for c in record['coverage']:
        x=c.get('explanation')
        if not x:
            lines.append(c['detector']+': legacy scan count '+str(c['assessed'])+'; rerun diagnosis for eligibility details.');continue
        lines.append(c['detector']+': '+x['status']+'; '+str(x['eligible'])+' '+x['unit']+'; '+str(c['findings'])+' signal(s).')
        if x['excluded']:lines.append('  Excluded: '+', '.join(k+' ('+str(v)+')' for k,v in x['excluded'].items()))
        for request in x['nextEvidence']:lines.append('  Need: '+request)
        if x['noCandidateExplanation']:lines.append('  '+x['noCandidateExplanation'])
        lines.append('  Limit: '+x['blindSpots'][0])
    if any(c.get('explanation',{}).get('opaqueEvidenceRequest') for c in record['coverage']):
        lines.append('Opaque wrappers: emit ordered tool names, arguments, status and results for the affected calls; stored path snapshots only when needed. See cited coverage warnings in the run record.')
    if record.get('children'): lines.append('Separate child diagnoses: '+', '.join(c['agentId']+' ('+str(len(c['diagnosis']['findings']))+' signals)' for c in record['children']))
    lines.append('No findings does not establish correctness. Full citations and input snapshot are in the run record.')
    return '\n'.join(lines)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=default_root());p.add_argument('--json',action='store_true')
    sub=p.add_subparsers(dest='command',required=True)
    d=sub.add_parser('diagnose');d.add_argument('--data',required=True);d.add_argument('--context');d.add_argument('--assessment');d.add_argument('--experiment');d.add_argument('--actual-change')
    i=sub.add_parser('ingest');i.add_argument('folder',type=Path);i.add_argument('--mapping',type=Path);i.add_argument('--repo',type=Path);i.add_argument('--out',type=Path,required=True);i.add_argument('--context');i.add_argument('--assessment');i.add_argument('--experiment');i.add_argument('--actual-change')
    e=sub.add_parser('experiment');e.add_argument('--baseline',required=True);e.add_argument('--finding',required=True);e.add_argument('--hypothesis');e.add_argument('--intervention');e.add_argument('--criterion');e.add_argument('--type',choices=['context-engineering','product-repair','instrumentation','unspecified'],default='unspecified');e.add_argument('--contract',help='JSON contextIntervention, expectedBehavior, acceptanceCheck')
    c=sub.add_parser('compare');c.add_argument('--baseline',required=True);c.add_argument('--run',required=True);c.add_argument('--experiment');c.add_argument('--mode',choices=['auto','extraction','execution'],default='auto');c.add_argument('--experiment-type',choices=['context-engineering','product-repair','instrumentation']);c.add_argument('--contract');c.add_argument('--reassessment',help='JSON array of cited finding reassessments')
    b=sub.add_parser('benchmark');b.add_argument('--suite',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    h=sub.add_parser('history');h.add_argument('--finding')
    a=p.parse_args()
    try:
        if a.command=='benchmark':
            from benchmark import run as run_benchmark
            value=run_benchmark(a.suite,a.out);value.update(kind='benchmark',createdAt=datetime.now(timezone.utc).isoformat())
            record,path=save(a.root,'benchmark',value)
            print(json.dumps(dict(record=record,path=str(path)),indent=2) if a.json else (a.out/'summary.txt').read_text()+'\nRecord: '+str(path));return
        if a.command in ('diagnose','ingest'):
            if a.command=='ingest':
                from bundle import ingest
                from reconstruct import reconstruct
                if a.out.resolve()==a.folder.resolve():raise ValueError('Output must be separate from the bundle root')
                a.out.mkdir(parents=True,exist_ok=True)
                bundle=ingest(a.folder,read(a.mapping) if a.mapping else None,exclude=a.out)
                (a.out/'inventory.json').write_text(json.dumps(bundle['inventory'],indent=2)+'\n')
                (a.out/'interpretation.json').write_text(json.dumps({'mapping':bundle['manifest'],'mappingHash':bundle['mappingHash'],'issues':bundle['issues'],'mappedRecords':len(bundle['records'])},indent=2)+'\n')
                if not bundle['records']:raise ValueError('No mapped records; inspect inventory.json and supply a reusable --mapping manifest')
                data=reconstruct(bundle,a.repo.resolve() if a.repo else None)
                (a.out/'session.json').write_text(json.dumps(data,indent=2)+'\n')
            else:data=read(a.data)
            value=diagnosis(data,read(a.context) if a.context else {})
            value['assessment']=assessment(a.assessment)
            if a.experiment:
                exp=load(a.root,a.experiment,'experiment');value.update(experiment=exp['id'],parent=exp['baseline'],actualChange=a.actual_change)
            record,path=save(a.root,'run',value)
            if a.command=='ingest':(a.out/'diagnosis.txt').write_text(summary(record)+'\nRecord: '+str(path)+'\n')
        elif a.command=='experiment':
            run=load(a.root,a.baseline,'run');f=next((f for f in run['findings'] if f['id']==a.finding),None)
            if not f: raise ValueError('Finding not in baseline')
            value=dict(kind='experiment',baseline=run['id'],finding=f['id'],hypothesis=a.hypothesis or f['interpretation'],
                intervention=a.intervention or f['action'],criterion=a.criterion or f['verification'],status='proposed')
            from comparison_layers import contract
            value.update(experimentType=a.type,contract=contract(read(a.contract) if a.contract else None,a.type))
            record,path=save(a.root,'experiment',value)
        elif a.command=='compare':
            before=load(a.root,a.baseline,'run');after=load(a.root,a.run,'run')
            exp=load(a.root,a.experiment,'experiment') if a.experiment else None
            record,path=save(a.root,'comparison',compare(before,after,exp,a.mode,a.experiment_type,read(a.contract) if a.contract else None,read(a.reassessment) if a.reassessment else None))
        else:
            records=[read(f) for f in sorted((a.root/'engineering'/'run').glob('*.json'))]
            records.sort(key=lambda r:r['createdAt'])
            rows=[dict(id=r['id'],createdAt=r['createdAt'],findings=[f['id'] for f in r['findings']]) for r in records if not a.finding or any(f['id']==a.finding for f in r['findings'])]
            comparisons=[read(f) for f in sorted((a.root/'engineering'/'comparison').glob('*.json'))]
            comparisons=[c for c in comparisons if not a.finding or any(t['finding']==a.finding for t in c['transitions'])]
            print(json.dumps(dict(runs=rows,comparisons=comparisons),indent=2));return
        print(json.dumps(dict(record=record,path=str(path)),indent=2) if a.json else summary(record)+'\n\nRecord: '+str(path))
    except (ValueError,KeyError,OSError,TypeError) as exc: p.error(str(exc))
if __name__=='__main__': main()
