#!/usr/bin/env python3
"""Attach cited workflows, or import a base-ui peer-review evidence directory."""
import argparse,json
from pathlib import Path
from fog import validate

def read(path): return json.loads(Path(path).read_text())
def attach(data, workflows):
    data['workflows']=workflows
    validate(data)
    return data

def peer(root, app, data):
    outcome=read(root/'outcome-map.json')[app]['selected']
    inspection=read(root/'inspection-adjudication.json')[app]
    decisions={d['id']:d for d in data.get('decisions',[])}
    refs=decisions.get('review',{}).get('evidence',[])
    def trace_refs(needle):
        return [dict(r,label='Recorded trace excerpt') for r in refs if needle in r['excerpt']]
    def artifact(name,pointer,value):
        return {'label':name,'artifact':str(root/name),'pointer':pointer,'excerpt':json.dumps(value,ensure_ascii=False,indent=2)}
    g=trace_refs('Execute a review session')
    a=[r for r in refs if any(k in r['excerpt'] for k in ['review-session.mjs capture','review-session.mjs detail','review-session.mjs record','review-delivery.mjs finish'])]
    a=[dict(r,label='Recorded command (execution alone does not prove completion)') for r in a]
    stages=[
      dict(kind='guidance',state='complete' if g else 'unknown',summary='Review guidance returned in the trace.' if g else 'No verified guidance citation.',evidence=g),
      dict(kind='action',state='complete' if a else 'unknown',summary='Review commands recorded; inspect citations for capture, detail, judgment and finish activity. This does not establish successful review.',evidence=a),
      dict(kind='evidence',state='complete' if inspection['complete'] else 'incomplete',summary=f"{inspection['observedFinalSamples']} of {inspection['requiredSamples']} required final visual samples inspected.",evidence=[artifact('inspection-adjudication.json','/'+app,inspection)]),
      dict(kind='outcome',state='unknown' if not outcome.get('matchesFinalArtifact') else 'incomplete' if not outcome['complete'] else 'complete' if outcome['accepted'] else 'failed',summary=f"Review: {outcome['status']}. Acceptance: {'accepted' if outcome['accepted'] else 'not accepted'}. Receipt matches final artifact: {outcome.get('matchesFinalArtifact')}.",evidence=[artifact('outcome-map.json','/'+app+'/selected',outcome)])]
    return [dict(id='review-completion',title=app+' · review delivery',stages=stages,nextStep='Inspect remaining final-artifact samples, record judgments, resolve product failures, then generate a new receipt.' if not inspection['complete'] else 'Resolve recorded product failures and rerun affected scenarios; preserve the completed review as historical evidence.',uncertainty='Image access establishes inspection coverage, not understanding. Commands establish activity, not success. Why execution stopped is unknown; timing alone does not establish a cause.')]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--manifest',type=Path);g.add_argument('--peer-review',type=Path);p.add_argument('--app')
    a=p.parse_args();data=read(a.data)
    if a.peer_review:
        if not a.app:p.error('--peer-review requires --app')
        workflows=peer(a.peer_review.resolve(),a.app,data)
    else:workflows=read(a.manifest)
    # Verify structured external citations before embedding their snapshots.
    for w in workflows:
        for s in w['stages']:
            for ref in s['evidence']:
                if 'artifact' not in ref:continue
                value=read(ref['artifact'])
                for part in ref['pointer'].lstrip('/').split('/'):
                    key=part.replace('~1','/').replace('~0','~');value=value[int(key)] if isinstance(value,list) else value[key]
                if json.loads(ref['excerpt']) != value:raise ValueError('Artifact citation does not match: '+ref['artifact'])
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(attach(data,workflows),ensure_ascii=False,indent=2)+'\n');print(a.out)
if __name__=='__main__':main()
