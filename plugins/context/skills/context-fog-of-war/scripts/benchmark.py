"""Run hash-pinned adjudicated traces; never execute recorded commands."""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

def sha(value):return hashlib.sha256(value).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def score(expected,actual):
    expected,actual=Counter(expected),Counter(actual)
    tp=sum((expected&actual).values());fp=sum((actual-expected).values());fn=sum((expected-actual).values())
    return dict(tp=tp,fp=fp,fn=fn,precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None)
def sig(x):return (x['detector'],x['anchorLine'])
def attr(x):return (x['path'],x['line'])
def summarize(cases):
    result={}
    for key in ('signalDetection','candidateProblemTriage','problemTriage','returnedAttribution','relationshipAttribution'):
        counts={k:sum(c[key][k] for c in cases) for k in ('tp','fp','fn')};tp,fp,fn=(counts[k] for k in ('tp','fp','fn'));result[key]=dict(counts,precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None)
    actions=[a for c in cases for a in c['actions'] if a['matchedProblem']]
    reviewed=[a for a in actions if a['rating']!='unreviewed'];addressed=sum(a['rating']=='addresses' for a in reviewed)
    problem_count=sum(c['problemTriage']['tp']+c['problemTriage']['fn'] for c in cases)
    result['actionRelevance']={'matchedProblemSuggestions':len(actions),'reviewed':len(reviewed),'addresses':addressed,'partial':sum(a['rating']=='partial' for a in reviewed),'unrelated':sum(a['rating']=='unrelated' for a in reviewed),'unreviewed':len(actions)-len(reviewed),'addressRateAmongReviewed':addressed/len(reviewed) if reviewed else None,'problemCoverageWithAddressingAction':addressed/problem_count if problem_count else None,'nonProblemSuggestions':sum(not a['matchedProblem'] for c in cases for a in c['actions']),'limitation':'Author-adjudicated relevance, not evidence the remedy works.'}
    result['triage']={'likelyBenign':sum(x['triage']['state']=='likely-benign' for c in cases for x in c['actualSignals']),'needsReview':sum(x['triage']['state']=='needs-review' for c in cases for x in c['actualSignals']),'nonProblemCorrectiveSuggestions':sum(not a['matchedProblem'] and a['correctiveSuggestion'] for c in cases for a in c['actions'])}
    ambiguous=[c for c in cases if c['ambiguous']];result['abstention']={'cases':len(ambiguous),'correct':sum(not c['actualSignals'] for c in ambiguous),'violations':sum(bool(c['actualSignals']) for c in ambiguous)}
    return result

def run(manifest_path,out):
    from fog import hydrate
    import claude
    from bundle import ingest
    from reconstruct import reconstruct
    from diagnostics import diagnose
    manifest_path=Path(manifest_path).resolve();root=manifest_path.parent;manifest=read(manifest_path);out=Path(out).resolve()
    if out==root or root in out.parents:raise ValueError('Benchmark output must be outside the frozen suite')
    out.mkdir(parents=True,exist_ok=True);reviews_path=root/'action-reviews.json';reviews=read(reviews_path) if reviews_path.exists() else {};cases=[]
    for relative,expected in manifest.get('repoHashes',{}).items():
        file=(root/'repo'/relative).resolve()
        if (root/'repo').resolve() not in file.parents or sha(file.read_bytes())!=expected:raise ValueError('Repository fixture hash mismatch')
    ids=set()
    for label in manifest['cases']:
        if label['id'] in ids:raise ValueError('Duplicate case ID')
        ids.add(label['id']);trace=(root/label['trace']).resolve()
        if root not in trace.parents or sha(trace.read_bytes())!=label['sha256']:raise ValueError('Trace path or hash mismatch: '+label['id'])
        if label['host']=='codex':data=hydrate(trace,root/'repo')
        elif label['host']=='claude':data=claude.hydrate(trace,root/'repo')
        elif label['host']=='bundle':data=reconstruct(ingest(trace.parent))
        else:raise ValueError('Unsupported host')
        diagnose(data);paths={s['id']:s['path'] for s in data['sources']};actual=[];actions=[];expected_problems=Counter(map(sig,label['problems']))
        for f in data['diagnostics']['findings']:
            anchor=max(e['traceLine'] for e in f['evidence']);item={'detector':f['detector'],'anchorLine':anchor,'evidence':f['evidence'],'triage':f['triage']};actual.append(item)
            digest=sha(f['guidance'].encode());key=f"{label['id']}/{f['detector']}/{anchor}";review=reviews.get(key)
            matched=expected_problems[sig(item)]>0
            if matched:expected_problems[sig(item)]-=1
            valid=review and review.get('actionSha256')==digest and review.get('traceSha256')==label['sha256'] and review.get('labelSha256')==sha(json.dumps(label,sort_keys=True).encode()) and review.get('rationale') and review.get('rating') in ('addresses','partial','unrelated','not-needed')
            actions.append(dict(key=key,text=f['guidance'],actionSha256=digest,traceSha256=label['sha256'],matchedProblem=matched,rating=review['rating'] if valid else 'unreviewed',rationale=review['rationale'] if valid else 'No current hash-matched action adjudication.',triage=f['triage']['state'],correctiveSuggestion=f['triage']['state']!='likely-benign'))
        # One exposure claim per source/result line; duplicated annotations are not independent returns.
        returns=sorted({(paths[x['sourceId']],e['evidence']['traceLine']) for e in data['events'] for x in e['exposures'] if x['state'] in ('read','partial')})
        actual_returns=[dict(path=p,line=line) for p,line in returns]
        lines={e['id']:e['evidence']['traceLine'] for e in data['events']}
        actual_links=sorted({(lines[l['from']],lines[l['to']]) for l in data['links'] if l.get('reason','').startswith(('Matched','Explicit target identity'))})
        triaged=[x for x in actual if x['triage']['state']!='likely-benign']
        c=dict(id=label['id'],host=label['host'],ambiguous=label['ambiguous'],rationale=label['rationale'],actualSignals=actual,actualProblemCandidates=triaged,actualReturns=actual_returns,actions=actions,
            signalDetection=score(map(sig,label['expectedSignals']),map(sig,actual)),candidateProblemTriage=score(map(sig,label['problems']),map(sig,actual)),problemTriage=score(map(sig,label['problems']),map(sig,triaged)),returnedAttribution=score(map(attr,label['returns']),returns),relationshipAttribution=score(((x['fromLine'],x['toLine']) for x in label['links']),actual_links),actualLinks=actual_links,
            missedSignals=list((Counter(map(sig,label['expectedSignals']))-Counter(map(sig,actual))).elements()),missedProblems=list((Counter(map(sig,label['problems']))-Counter(map(sig,triaged))).elements()),unexpectedSignals=list((Counter(map(sig,actual))-Counter(map(sig,label['expectedSignals']))).elements()),coverage=data['diagnostics']['coverage'])
        cases.append(c)
    result=dict(version=2,triagePolicy='Exclude only explicitly qualified likely-benign signals; needs-review signals remain problem candidates. candidateProblemTriage preserves the original all-signals metric.',manifestSha256=sha(manifest_path.read_bytes()),actionReviewsSha256=sha(reviews_path.read_bytes()) if reviews_path.exists() else None,limitations=manifest['limitations'],caseCount=len(cases),aggregate=summarize(cases),byHost={host:summarize([c for c in cases if c['host']==host]) for host in sorted({c['host'] for c in cases})},cases=cases)
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=[f"Adjudicated trace benchmark: {len(cases)} cases",'Author-adjudicated development suite; synthetic plus frozen real subset; not independent production validation.']
    for group,metrics in [('all',result['aggregate']),*result['byHost'].items()]:
        lines.append('\n'+group)
        for key in ('signalDetection','candidateProblemTriage','problemTriage','returnedAttribution','relationshipAttribution'):
            m=metrics[key];lines.append(f"  {key}: TP={m['tp']} FP={m['fp']} FN={m['fn']} precision={m['precision']} recall={m['recall']}")
        lines.append('  triage: '+json.dumps(metrics['triage']));lines.append('  actions: '+json.dumps(metrics['actionRelevance']));lines.append('  ambiguity: '+json.dumps(metrics['abstention']))
    for c in cases:
        if c['missedSignals'] or c['missedProblems'] or c['unexpectedSignals'] or c['returnedAttribution']['fp'] or c['returnedAttribution']['fn']:lines.append('\nReview '+c['id']+': missedSignals='+str(c['missedSignals'])+' missedProblems='+str(c['missedProblems'])+' unexpected='+str(c['unexpectedSignals'])+' attribution='+str(c['returnedAttribution']))
    (out/'summary.txt').write_text('\n'.join(lines)+'\n');return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--suite',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.suite,a.out);print((a.out/'summary.txt').read_text())
if __name__=='__main__':main()
