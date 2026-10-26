#!/usr/bin/env python3
"""Bounded log-first discovery. Raw events never leave the local process."""
import argparse,json,os,stat,time,collections,sys
from pathlib import Path
sys.dont_write_bytecode=True
from traces import parse,sha,SKILLS
from scan import excluded,SKILL
from report import render

def collect(roots,out,seconds=20,max_entries=50000,max_files=100,max_bytes=8388608,depth=8):
    counts=collections.Counter();observations=[];index=[];seen={};start=time.monotonic();stop=None
    for root in roots:
        root=Path(root).expanduser().absolute()
        if excluded(root) or root.resolve()!=root or not root.is_dir():counts['excludedOrMissingRoots']+=1;continue
        queue=collections.deque([(root,0)])
        while queue and not stop:
            d,level=queue.popleft()
            if time.monotonic()-start>=seconds:stop='time-budget';break
            try:
                with os.scandir(d) as entries:
                    for e in entries:
                        if counts['entries']>=max_entries:stop='entry-budget';break
                        if counts['traceFiles']>=max_files:stop='trace-file-budget';break
                        if time.monotonic()-start>=seconds:stop='time-budget';break
                        counts['entries']+=1;p=Path(e.path)
                        if excluded(p) or p==out or out in p.parents or e.is_symlink():counts['excluded']+=1;continue
                        if e.is_dir(follow_symlinks=False):
                            if level<depth:queue.append((p,level+1))
                            else:counts['depthLimitedDirectories']+=1
                            continue
                        if p.suffix not in ('.jsonl','.ndjson') or not e.is_file(follow_symlinks=False):continue
                        counts['traceFiles']+=1
                        try:
                            fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
                            with os.fdopen(fd,'rb') as f:
                                a=os.fstat(f.fileno())
                                if not stat.S_ISREG(a.st_mode) or a.st_size>max_bytes:counts['oversizedOrNonregular']+=1;continue
                                raw=f.read(max_bytes+1);z=os.fstat(f.fileno())
                            if len(raw)>max_bytes or (a.st_size,a.st_mtime_ns)!=(z.st_size,z.st_mtime_ns):counts['changedOrOversized']+=1;continue
                            h=sha(raw)
                            if h in seen:seen[h]['paths'].append(str(p));counts['exactCopies']+=1;continue
                            o=parse(raw)
                            if not o['recordedCommands']:counts['unsupportedOrNoCommands']+=1;continue
                            row={'sha256':h,'paths':[str(p)],'bytes':len(raw),'adapter':o['adapterVersion']};seen[h]=row;index.append(row);observations.append(o)
                        except OSError:counts['readErrors']+=1
            except OSError:counts['directoryErrors']+=1
        if stop:break
    return observations,{'schemaVersion':1,'sources':index,'coverage':{'counts':dict(counts),'stopReason':stop,'uniqueCandidateDocuments':len(index),'limitations':['Only bounded JSONL/NDJSON Codex exec events supported.','Unrelated session/chat stores, credentials, holdouts and symlinks excluded.','No producer manifest or skill-emitted report required.','Soft traversal budgets and nonrepresentative source ordering remain.']}}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',action='append');p.add_argument('--output',required=True);p.add_argument('--seconds',type=float,default=20);p.add_argument('--max-entries',type=int,default=50000);p.add_argument('--max-files',type=int,default=100);p.add_argument('--max-bytes',type=int,default=8388608);p.add_argument('--depth',type=int,default=8);a=p.parse_args();
    if min(a.seconds,a.max_entries,a.max_files,a.max_bytes)<=0 or a.depth<0:p.error('Positive budgets and nonnegative depth required')
    out=Path(a.output).expanduser().absolute()
    if out.exists() or out.resolve()!=out or out==SKILL.parent or SKILL.parent in out.parents:p.error('Use a fresh output outside installed skills')
    out.mkdir(parents=True,mode=0o700)
    roots=a.root or [Path.home()/'.codex/skill-previews',Path.home()/'Projects']
    obs,index=collect(roots,out,seconds=a.seconds,max_entries=a.max_entries,max_files=a.max_files,max_bytes=a.max_bytes,depth=a.depth);(out/'trace-observations.json').write_text(json.dumps({'schemaVersion':1,'observations':obs,'measuredKpis':0},indent=2)+'\n');(out/'evidence-index.json').write_text(json.dumps(index,indent=2)+'\n')
    contracts=json.loads((SKILL/'references/kpis.json').read_text());cards=[]
    for s in contracts['skills']:
        traces=[o for o in obs if s['id'] in o['skillHints']]
        cards.append({**s,'candidateDocuments':len(traces),'traceObservations':[{'loggedOutputBytes':o['loggedCommandOutputUtf8Bytes'],'recordedCommands':o['recordedCommands'],'successfulExits':o['recordedSuccessfulExits'],'nonzeroExits':o['recordedNonzeroExits'],'conflicts':o['conflictingCommandIdentities'],'traceSHA256':o['traceSHA256']} for o in traces],'metrics':[{'id':k['id'],'value':None,'status':'not-measured','evidenceState':'insufficient','reason':'Logs supply observations; this performance criterion lacks qualified task/quality applicability.'} for k in s['kpis']]})
    report={'schemaVersion':1,'status':'log-first-observations','coverage':index['coverage'],'skills':cards,'styling':None};render(report,out,SKILL.parent/'base-ui');(out/'report-card.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'log-first-observations','dashboard':str(out/'index.html'),'qualifiedTraceFormats':len(obs),'measuredKpis':0,'stopReason':index['coverage']['stopReason']}))
if __name__=='__main__':main()
