#!/usr/bin/env python3
"""W5: fixed historical source selections, reported dimensions, no KPI aggregation."""
import argparse,json,hashlib,os,stat,sys,copy
from pathlib import Path
sys.dont_write_bytecode=True
ADAPTER='split-consumption-study/1.0.0'
REGISTRY=json.loads((Path(__file__).resolve().parents[1]/'references/split-study-v1.json').read_text())
MAX_BYTES=2097152
KEYS=('protocol','metrics','revision','qualification','generation','preservation')
def sha(b):return hashlib.sha256(b).hexdigest()
def ptr(s):return s.replace('~','~0').replace('/','~1')
def bounded(p):
    if p.resolve()!=p or any(x.lower() in ('secrets','.claude','.ssh','node_modules') or 'holdout' in x.lower() for x in p.parts):raise ValueError('unsafe-selection')
    fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
    with os.fdopen(fd,'rb') as f:
        a=os.fstat(f.fileno())
        if not stat.S_ISREG(a.st_mode) or a.st_size>MAX_BYTES:raise ValueError('invalid-selection-file')
        b=f.read(MAX_BYTES+1);z=os.fstat(f.fileno())
    if len(b)>MAX_BYTES or (a.st_size,a.st_mtime_ns)!=(z.st_size,z.st_mtime_ns):raise ValueError('changed-selection')
    return b

def interpret(packet,hashes,artifact_hash):
    if set(packet)!=set(KEYS) or set(hashes)!=set(KEYS):raise ValueError('missing-source-selection')
    p,m,r,q,g,preserve=(packet[k] for k in KEYS)
    if not isinstance(p,dict) or type(p.get('schemaVersion')) is not int or p.get('schemaVersion')!=1 or type(p.get('revisionContaminated')) is not bool:raise ValueError('invalid-protocol')
    if not isinstance(m,list) or len(m)!=3 or any(not isinstance(x,dict) or type(x.get('readCommandReturnBytes')) is not int or x['readCommandReturnBytes']<0 or not isinstance(x.get('readMetricDefinition'),str) or not x['readMetricDefinition'] or not isinstance(x.get('evaluatorAccess'),list) for x in m):raise ValueError('invalid-byte-telemetry')
    if not isinstance(q,dict) or any(q.get(k) is not True for k in ('capFaultDetected','swappedErrorFaultDetectedByStrongPredicate','positiveStrongPredicatePasses','qualifierCopiesAreNotAuthorRepairs')):raise ValueError('unqualified-behavior-predicate')
    if not isinstance(g,dict) or g.get('mode')!='draft' or not isinstance(g.get('delivery'),dict) or g['delivery'].get('status')!='delivery-incomplete':raise ValueError('unsupported-draft-qualification')
    if not isinstance(g.get('artifactSHA256'),str) or g['artifactSHA256']!=artifact_hash:raise ValueError('artifact-identity-mismatch')
    unverified=g.get('findings',{}).get('unverified')
    if not isinstance(unverified,list) or any(not isinstance(x,dict) or x.get('severity')!='unverified' for x in unverified):raise ValueError('invalid-style-observations')
    if not isinstance(preserve,dict) or any(type(preserve.get(k)) is not bool for k in ('03-revisionFrozen','03-revisionPredecessor','03-revisionSeal')):raise ValueError('invalid-preservation-record')
    if not isinstance(r,list) or len(r)!=4:raise ValueError('missing-environment-cases')
    envs=[];obs=[]
    def add(dimension,outcome,evidence,environment=None):
        obs.append({'dimension':dimension,'outcome':outcome,'origin':'reported','environment':environment,'evidence':[{'sourceId':s,'sha256':hashes[s],'pointer':pointer} for s,pointer in evidence]})
    for i,row in enumerate(r):
        if not isinstance(row,dict) or row.get('width') not in (390,1280) or row.get('scheme') not in ('light','dark') or not isinstance(row.get('variants'),list) or len(row['variants'])!=2:raise ValueError('invalid-environment-case')
        envs.append((row['width'],row['scheme']));variant_ids=[]
        for j,v in enumerate(row['variants']):
            if not isinstance(v,dict) or v.get('variant') not in ('A','B') or not isinstance(v.get('checks'),dict) or len(v['checks'])!=5:raise ValueError('missing-behavior-criteria')
            variant_ids.append(v['variant'])
            for name,result in v['checks'].items():
                if not isinstance(name,str) or not isinstance(result,dict) or type(result.get('pass')) is not bool:raise ValueError('invalid-behavior-result')
                add('scoped-behavior','pass' if result['pass'] else 'fail',[('revision',f'/{i}/variants/{j}/checks/{ptr(name)}/pass'),('qualification','/positiveStrongPredicatePasses')],{'width':row['width'],'scheme':row['scheme'],'variant':v['variant'],'engine':'unqualified-in-structured-result'})
        if set(variant_ids)!={'A','B'}:raise ValueError('duplicate-variant')
    if set(envs)!={(390,'light'),(390,'dark'),(1280,'light'),(1280,'dark')} or len(set(envs))!=4:raise ValueError('duplicate-or-omitted-environment')
    accessed=bool(m[2]['evaluatorAccess']);contaminated=p['revisionContaminated'] or accessed
    add('clean-context-eligibility','ineligible' if contaminated else 'unverified',[('protocol','/revisionContaminated'),('metrics','/2/evaluatorAccess')])
    add('delivery','draft-incomplete',[('generation','/mode'),('generation','/delivery/status')])
    unknown=[i for i,x in enumerate(unverified) if x.get('rule')=='unknown-style-owner']
    for i in unknown:add('style-owner','unverified',[('generation',f'/findings/unverified/{i}')])
    for i,x in enumerate(m):add('byte-telemetry','reported',[('metrics',f'/{i}/readCommandReturnBytes'),('metrics',f'/{i}/readMetricDefinition')])
    for k in ('03-revisionFrozen','03-revisionPredecessor','03-revisionSeal'):add('preservation','pass' if preserve[k] else 'fail',[('preservation','/'+ptr(k))])
    normalized={'schemaVersion':1,'adapterVersion':ADAPTER,'batchId':REGISTRY['batchId'],'sourceHashes':hashes,'observations':obs,'behaviorScope':'selected-revision-checks-only','fullSystemAcceptance':False,'cleanContextEligibility':'ineligible' if contaminated else 'unverified','contaminationConflict':p['revisionContaminated']!=accessed,'deliveryMode':'draft','deliveryAcceptance':'incomplete','unknownStyleOwnerCount':len(unknown),'confirmedDefectCount':None,'telemetry':{'values':[x['readCommandReturnBytes'] for x in m],'unit':'bytes','classifier':'read-containing-command-returns','mixedCommands':True,'modelTokens':None,'crossTaskEfficiencyRanking':None},'preservationSubstitutesForBehavior':False,'artifactIdentity':'generation-subject-hash-matched','behaviorArtifactBinding':'unverified','sourceApplicability':'historical-only','attemptDenominator':None,'performanceEligible':False,'measuredKpis':0,'limitations':['Behavior results remain reported with width/scheme/variant provenance; engine/artifact execution binding is incomplete.','Recorded evaluator access excludes this revision from clean-context success.','Draft gates and preservation cannot substitute for delivery or behavior.','Unknown style owners need diagnosis; byte classifier is incomplete and not tokens.']}
    validate(normalized);return normalized

def validate(n):
    if n.get('schemaVersion')!=1 or n.get('adapterVersion')!=ADAPTER or n.get('fullSystemAcceptance') is not False or n.get('cleanContextEligibility') not in ('ineligible','unverified') or n.get('deliveryMode')!='draft' or n.get('deliveryAcceptance')!='incomplete' or n.get('confirmedDefectCount') is not None or n.get('preservationSubstitutesForBehavior') is not False or n.get('performanceEligible') is not False or n.get('measuredKpis')!=0 or n.get('attemptDenominator') is not None:raise ValueError('unsupported-interpretation-claim')
    t=n.get('telemetry',{})
    if t.get('unit')!='bytes' or t.get('classifier')!='read-containing-command-returns' or t.get('mixedCommands') is not True or t.get('modelTokens') is not None or t.get('crossTaskEfficiencyRanking') is not None:raise ValueError('unsupported-telemetry-claim')
    allowed_fields={'schemaVersion','adapterVersion','batchId','sourceHashes','observations','behaviorScope','fullSystemAcceptance','cleanContextEligibility','contaminationConflict','deliveryMode','deliveryAcceptance','unknownStyleOwnerCount','confirmedDefectCount','telemetry','preservationSubstitutesForBehavior','artifactIdentity','behaviorArtifactBinding','sourceApplicability','attemptDenominator','performanceEligible','measuredKpis','limitations'}
    if set(n)!=allowed_fields or set(n.get('sourceHashes',{}))!=set(KEYS):raise ValueError('invalid-normalized-schema')
    outcomes={'scoped-behavior':('pass','fail'),'clean-context-eligibility':('ineligible','unverified'),'delivery':('draft-incomplete',),'style-owner':('unverified',),'byte-telemetry':('reported',),'preservation':('pass','fail')}
    for o in n['observations']:
        if o.get('outcome') not in outcomes.get(o.get('dimension'),()):raise ValueError('unsupported-dimensional-outcome')
        if o['origin']!='reported' or o['dimension'] not in ('scoped-behavior','clean-context-eligibility','delivery','style-owner','byte-telemetry','preservation'):raise ValueError('unsupported-observation')
        if o['dimension']=='scoped-behavior' and (o['outcome'] not in ('pass','fail') or any(e.get('sourceId') not in ('revision','qualification') for e in o['evidence'])):raise ValueError('behavior-provenance-substitution')
        for e in o['evidence']:
            if e.get('sourceId') not in n['sourceHashes'] or e['sha256']!=n['sourceHashes'][e['sourceId']]:raise ValueError('selection-source-mismatch')
            if not isinstance(e['sha256'],str) or len(e['sha256'])!=64 or not e['pointer'].startswith('/'):raise ValueError('invalid-selection-provenance')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--output',required=True);a=p.parse_args();root=Path(a.batch).absolute();out=Path(a.output).absolute()
    if out.exists() or out.resolve()!=out or root==out or root in out.parents or Path(__file__).resolve().parents[2] in out.parents:p.error('Use a fresh output outside inputs and installed skills')
    out.mkdir(parents=True,mode=0o700)
    try:
        packet={};hashes={}
        for key in KEYS:
            record=REGISTRY['sources'][key];raw=bounded(root/record['relativePath']);hashes[key]=sha(raw)
            if hashes[key]!=record['sha256']:raise ValueError('source-identity-mismatch')
            packet[key]=json.loads(raw)
        gp=root/REGISTRY['sources']['generation']['relativePath'];artifact_hash=sha(bounded(gp.parent/'artifact.html'))
        result=interpret(packet,hashes,artifact_hash);(out/'observations.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'status':'qualified-scoped-reported','output':str(out/'observations.json'),'observations':len(result['observations']),'cleanContextEligibility':result['cleanContextEligibility'],'measuredKpis':0}))
    except (OSError,ValueError,TypeError,KeyError,RecursionError):print(json.dumps({'status':'rejected','rawEvidenceKeptLocal':True}));return 1
    return 0
if __name__=='__main__':sys.exit(main())
