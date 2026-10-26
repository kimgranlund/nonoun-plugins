#!/usr/bin/env python3
"""Replay only fixed historical selections and retain W5 copy-only controls."""
import argparse,json,copy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
from split_study import REGISTRY,KEYS,bounded,sha,interpret,validate

def verify(batch,out):
    packet={};hashes={}
    for key in KEYS:
        record=REGISTRY['sources'][key];raw=bounded(batch/record['relativePath']);hashes[key]=sha(raw)
        if hashes[key]!=record['sha256']:raise ValueError('source-identity-mismatch')
        packet[key]=json.loads(raw)
    gp=batch/REGISTRY['sources']['generation']['relativePath'];artifact_hash=sha(bounded(gp.parent/'artifact.html'))
    positive=interpret(packet,hashes,artifact_hash);raw=(json.dumps(positive,indent=2)+'\n').encode();(out/'positive.json').write_bytes(raw);positive_hash=sha(raw)
    selections=[]
    def control(name,pointer,mutate):
        n=copy.deepcopy(positive);mutate(n);raw=(json.dumps(n,indent=2)+'\n').encode();path=out/(name+'.json');path.write_bytes(raw)
        try:validate(n)
        except ValueError:state='rejected'
        else:raise ValueError('negative-control-did-not-bite')
        selections.append({'id':name,'state':state,'positive':{'path':str(out/'positive.json'),'sha256':positive_hash,'pointer':pointer},'negative':{'path':str(path),'sha256':sha(raw),'pointer':pointer}})
    control('CARD-01','/cleanContextEligibility',lambda n:n.update(cleanContextEligibility='eligible'))
    control('CARD-02','/deliveryAcceptance',lambda n:n.update(deliveryAcceptance='complete'))
    control('CARD-03','/telemetry/unit',lambda n:n['telemetry'].update(unit='tokens',modelTokens=1387892,crossTaskEfficiencyRanking=[0,1,2]))
    control('CARD-04','/confirmedDefectCount',lambda n:n.update(confirmedDefectCount=5))
    control('CARD-05','/observations/0/evidence',lambda n:n['observations'][0]['evidence'][0].update(sourceId='preservation',sha256=hashes['preservation']))
    control('CARD-06','/fullSystemAcceptance',lambda n:n.update(fullSystemAcceptance=True))
    # Conflicting metadata must retain observed behavior and the conservative eligibility.
    mixed=copy.deepcopy(packet);mixed['protocol']['revisionContaminated']=False;mh={k:sha(json.dumps(v).encode()) for k,v in mixed.items()};r=interpret(mixed,mh,artifact_hash)
    if r['cleanContextEligibility']!='ineligible' or not r['contaminationConflict']:raise ValueError('conflict-was-promoted')
    (out/'metadata-conflict.json').write_text(json.dumps(r,indent=2)+'\n')
    # Original CLI entry remains bounded; normalized source selections contain no raw prose.
    cli=subprocess.run([sys.executable,str(Path(__file__).with_name('split_study.py')),'--batch',str(batch),'--output',str(out/'cli')],capture_output=True,timeout=20)
    (out/'cli.stdout').write_bytes(cli.stdout);(out/'cli.stderr').write_bytes(cli.stderr)
    if cli.returncode!=0 or len(cli.stdout)>4096:raise ValueError('entry-verification-failed')
    copied=out/'tampered-packet';copied.mkdir(mode=0o700)
    for key in KEYS:
        record=REGISTRY['sources'][key];target=copied/record['relativePath'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(bounded(batch/record['relativePath']))
    artifact=copied/REGISTRY['sources']['generation']['relativePath'];(artifact.parent/'artifact.html').write_bytes(bounded(gp.parent/'artifact.html'))
    marker='PRIVATE_W5_SOURCE_CONTROL_'+'z'*100000
    pp=copied/REGISTRY['sources']['protocol']['relativePath'];mutated=json.loads(pp.read_bytes());mutated.update(revisionContaminated=False,rawPrivate=marker);pp.write_text(json.dumps(mutated))
    rejected=subprocess.run([sys.executable,str(Path(__file__).with_name('split_study.py')),'--batch',str(copied),'--output',str(out/'rejected-cli')],capture_output=True,timeout=20)
    if rejected.returncode==0 or marker.encode() in rejected.stdout+rejected.stderr or len(rejected.stdout)>4096:raise ValueError('source-control-did-not-reject-privately')
    (out/'source-rejection.json').write_text(json.dumps({'state':'rejected','sourceSHA256':sha(pp.read_bytes()),'pointer':'/revisionContaminated','rawMarkerNotReturned':True})+'\n')
    for key in KEYS:
        if sha(bounded(batch/REGISTRY['sources'][key]['relativePath']))!=hashes[key]:raise ValueError('original-changed')
    matrix={'schemaVersion':1,'adapterVersion':positive['adapterVersion'],'sourceHashes':hashes,'positiveSHA256':positive_hash,'criteria':selections,'originalSelectionsUnchanged':True,'publication':'not-published','observations':len(positive['observations']),'performanceEligible':False,'measuredKpis':0}
    (out/'criterion-evidence-matrix.json').write_text(json.dumps(matrix,indent=2)+'\n');return {'status':'qualified-scoped-reported','controlsPassed':len(selections),'metadataConflictRetained':True,'changedSourceRejectedPrivately':True,'observations':len(positive['observations']),'cleanContextEligibility':positive['cleanContextEligibility'],'measuredKpis':0,'matrix':str(out/'criterion-evidence-matrix.json')}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--output',required=True);a=p.parse_args();batch=Path(a.batch).absolute();out=Path(a.output).absolute()
    if out.exists() or out.resolve()!=out or batch==out or batch in out.parents or Path(__file__).resolve().parents[2] in out.parents:p.error('Fresh output outside inputs/skills required')
    out.mkdir(parents=True,mode=0o700)
    try:r=verify(batch,out)
    except (OSError,ValueError,KeyError,TypeError,RecursionError,subprocess.SubprocessError):print(json.dumps({'status':'verification-failed','rawEvidenceKeptLocal':True}));return 1
    print(json.dumps(r));return 0
if __name__=='__main__':sys.exit(main())
