#!/usr/bin/env python3
"""Bounded local JSON-candidate discovery. Never executes discovered content."""
import argparse, collections, hashlib, json, os, stat, sys, time
from pathlib import Path
from datetime import datetime, timezone
sys.dont_write_bytecode = True
from report import render
from adapters import qualify, PRODUCER
SKILL = Path(__file__).resolve().parents[1]
DENY = {'.git','node_modules','.ssh','.aws','.azure','.gnupg','.kube','.env','.trash','library','sessions','conversations','chats','credentials','secrets','.claude','__pycache__','.venv','venv'}
NAMES = {'generation.json','inventory.json','feedback.json','report.json','results.json','result.json','verification.json','acceptance.json','protocol.json','publication.json','kit.json'}
def excluded(path):
    return any(p.lower() in DENY or 'sealed' in p.lower() or 'holdout' in p.lower() or p.lower().startswith('skill-report-card-') for p in Path(path).parts)
def candidate_name(name):
    return name in NAMES or name.endswith(('-report.json','-results.json','-check.json'))
def default_roots():
    h = Path.home()
    return [h/'.codex/skill-previews',h/'.codex/skills',h/'Projects',h/'Documents',h/'Desktop',h/'Downloads',Path('/private/tmp'),h]
def scan(roots, output, selected, *, seconds=30, max_entries=100000, max_candidates=3000, max_bytes=2097152, depth=18):
    start=time.monotonic(); counts=collections.Counter(); rows=[]; seen_dirs=set(); by_hash={}; root_results=[]; stop=None
    def limited():
        if time.monotonic()-start >= seconds: return 'time-budget'
        if counts['entries'] >= max_entries: return 'entry-budget'
        if counts['candidateFiles'] >= max_candidates: return 'candidate-budget'
        return None
    for root in roots:
        rp=Path(root).expanduser().absolute(); rr={'path':str(rp),'status':'visited','errors':0};root_results.append(rr)
        if stop: rr['status']='not-visited-budget';continue
        if excluded(rp) or rp.is_symlink() or rp.resolve()!=rp or rp==output or output in rp.parents:
            rr['status']='excluded';continue
        if not rp.exists():rr['status']='missing';continue
        if not rp.is_dir():rr['status']='not-directory';continue
        queue=collections.deque([(rp,0)])
        while queue:
            stop=limited()
            if stop:rr['status']='partial-'+stop;break
            directory,level=queue.popleft()
            if directory in seen_dirs:continue
            seen_dirs.add(directory)
            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        stop=limited()
                        if stop:rr['status']='partial-'+stop;break
                        counts['entries']+=1;p=Path(entry.path)
                        if p==output or output in p.parents or excluded(p):counts['excluded']+=1;continue
                        try:
                            if entry.is_symlink():counts['symlinksSkipped']+=1;continue
                            if entry.is_dir(follow_symlinks=False):
                                if level<depth:queue.append((p,level+1))
                                else:counts['depthLimitedDirectories']+=1
                                continue
                            if not entry.is_file(follow_symlinks=False) or not candidate_name(entry.name):continue
                            counts['candidateFiles']+=1
                            flags=os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0)
                            fd=os.open(p,flags)
                            with os.fdopen(fd,'rb') as f:
                                before=os.fstat(f.fileno())
                                if not stat.S_ISREG(before.st_mode):counts['nonRegularSkipped']+=1;continue
                                if before.st_size>max_bytes:counts['oversized']+=1;continue
                                raw=f.read(max_bytes+1);after=os.fstat(f.fileno())
                            if len(raw)>max_bytes:counts['oversized']+=1;continue
                            if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):counts['changedDuringRead']+=1;continue
                            counts['bytesRead']+=len(raw)
                            try:data=json.loads(raw)
                            except (ValueError,UnicodeError,RecursionError):counts['malformed']+=1;continue
                            if not isinstance(data,dict):counts['unsupportedShape']+=1;continue
                            explicit=set()
                            for key in ['skill','skillId']:
                                if data.get(key) in selected:explicit.add(data[key])
                            for key in ['kit','identity']:
                                value=data.get(key)
                                if isinstance(value,dict) and value.get('packageId')=='local.base-ui' and 'base-ui' in selected:explicit.add('base-ui')
                            if data.get('packageId')=='local.base-ui' and 'base-ui' in selected:explicit.add('base-ui')
                            if data.get('pipelineSHA256') == PRODUCER and 'wireframe-review' in selected:explicit.add('wireframe-review')
                            hints={s for s in selected if s in p.parts}
                            related=explicit|hints
                            if not related:counts['unattributed']+=1;continue
                            digest=hashlib.sha256(raw).hexdigest()
                            if digest in by_hash:
                                row=by_hash[digest];row['paths'].append(str(p));row['skillHints']=sorted(set(row['skillHints'])|related);counts['exactDuplicates']+=1;continue
                            row={'sha256':digest,'bytes':len(raw),'paths':[str(p)],'skillHints':sorted(related),'attribution':'explicit-field' if explicit else 'path-hint-only','fileKind':'source-identity' if entry.name=='kit.json' else 'candidate-json','qualification':'unqualified','adapter':None}
                            if 'wireframe-review' in related:
                                def read_companion(name):
                                    # Fixed local names; source-provided paths are never followed.
                                    if name not in {'artifact.html','manifest.json','source.manifest.json','verification.json','runtime.json','lint.json','lint-policy.json','acceptance.json','acceptance-report.json'}:return None
                                    q=p.parent/name
                                    if limited() or excluded(q) or q.resolve()!=q:return None
                                    try:
                                        fd=os.open(q,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
                                        with os.fdopen(fd,'rb') as f:
                                            a=os.fstat(f.fileno())
                                            if not stat.S_ISREG(a.st_mode) or a.st_size>max_bytes:return None
                                            b=f.read(max_bytes+1);z=os.fstat(f.fileno())
                                        if len(b)>max_bytes or (a.st_size,a.st_mtime_ns)!=(z.st_size,z.st_mtime_ns):return None
                                        counts['adapterBytesRead']+=len(b);counts['adapterCompanionReads']+=1
                                        return b
                                    except OSError:
                                        counts['adapterReadErrors']+=1;return None
                                result=qualify(data,digest,read_companion)
                                row['adapter']=result['adapter'];row['qualification']=result['state'];row['adapterResult']=result
                            rows.append(row);by_hash[digest]=row
                        except (OSError,TypeError):counts['readErrors']+=1;rr['errors']+=1
            except OSError:counts['directoryErrors']+=1;rr['errors']+=1
        if rr['errors'] and rr['status']=='visited':rr['status']='visited-with-errors'
    return {'schemaVersion':1,'collectorVersion':'0.2.0','collectedAt':datetime.now(timezone.utc).isoformat(),'roots':root_results,'bounds':dict(seconds=seconds,maxEntries=max_entries,maxCandidates=max_candidates,maxBytesPerFile=max_bytes,depth=depth),'coverage':{'stopReason':stop,'elapsedSeconds':round(time.monotonic()-start,3),'counts':dict(counts),'uniqueCandidateDocuments':len(rows),'completeSystemCoverage':False,'limitations':['Known JSON filenames only; HTML-only samples are not indexed.','Exact bytes deduplicated; reported observations do not establish author attempts or KPI eligibility.','Filesystem order and budgets can bias the observed sample.','Protected directories and symlinks excluded; no unrelated chat stores read.','Same-user live filesystem races are not a hardened security boundary.']},'candidates':rows}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--root',action='append');p.add_argument('--skill',action='append',choices=['base-ui','component-variants','wireframe-review']);p.add_argument('--seconds',type=float,default=30);p.add_argument('--max-entries',type=int,default=100000);p.add_argument('--max-candidates',type=int,default=3000);p.add_argument('--max-bytes',type=int,default=2097152);p.add_argument('--depth',type=int,default=18)
    a=p.parse_args()
    if min(a.seconds,a.max_entries,a.max_candidates,a.max_bytes)<=0 or a.depth<0:p.error('Budgets must be positive; depth must be nonnegative')
    out=Path(a.output).expanduser().absolute()
    if out.exists():p.error('Output already exists; choose a fresh directory')
    if out==SKILL.parent or SKILL.parent in out.parents:p.error('Keep run outputs outside installed skills')
    out.mkdir(parents=True,mode=0o700)
    chosen=a.skill or ['base-ui','component-variants','wireframe-review']
    evidence=scan(a.root or default_roots(),out,chosen,seconds=a.seconds,max_entries=a.max_entries,max_candidates=a.max_candidates,max_bytes=a.max_bytes,depth=a.depth)
    evidence['coverage']['adapterStates']=dict(collections.Counter(row.get('adapterResult',{}).get('state','unqualified') for row in evidence['candidates']))
    observations=[o for row in evidence['candidates'] for o in row.get('adapterResult',{}).get('observations',[])]
    (out/'observations.json').write_text(json.dumps({'schemaVersion':1,'status':'reported-only','observations':observations,'attemptDeduplication':'unavailable-without-author-identity','performanceEligible':False},indent=2)+'\n')
    (out/'evidence-index.json').write_text(json.dumps(evidence,indent=2)+'\n')
    contracts=json.loads((SKILL/'references/kpis.json').read_text())
    cards=[]
    for s in contracts['skills']:
        if s['id'] not in chosen:continue
        cards.append({**s,'candidateDocuments':sum(s['id'] in row['skillHints'] for row in evidence['candidates']),'metrics':[{'id':k['id'],'value':None,'status':'not-measured','evidenceState':'insufficient','reason':'Reported metadata adapter does not establish an eligible KPI denominator.'} for k in s['kpis']]})
    report={'schemaVersion':1,'status':'reported-observations-only','generatedAt':evidence['collectedAt'],'coverage':evidence['coverage'],'skills':cards,'styling':None}
    render(report,out,SKILL.parent/'base-ui')
    (out/'report-card.json').write_text(json.dumps(report,indent=2)+'\n')
    # Only bounded metadata is returned to the calling conversation, never evidence contents.
    print(json.dumps({'status':'reported-observations-only','dashboard':str(out/'index.html'),'index':str(out/'evidence-index.json'),'uniqueCandidateDocuments':len(evidence['candidates']),'measuredKpis':0,'stopReason':evidence['coverage']['stopReason']}))
if __name__=='__main__':main()
