#!/usr/bin/env python3
"""Analyze an explicitly scoped native-log selection, without returning raw logs."""
import argparse,json,stat,os,sys,collections
from pathlib import Path
sys.dont_write_bytecode=True
from native_traces import parse,sha,SKILLS
from scan import SKILL
from report import render
MISSING={
'system-fidelity':'No matched rendered geometry/type/color assertions with source bindings were qualified outside the batch.',
'interaction-correctness':'Action/assertion code hints lack specified operation cases and matched expected/observed outcomes.',
'environment-resilience':'Required browser/viewport usability cases and clipping/reachability results were not qualified.',
'standalone-consumption':'No isolated base-ui-only setup/build attempt was identified outside reporting/study activity.',
'context-burden':'Logged single-skill read returns are measurable below; successful-quality gates and complete retrieval capture are not established.',
'distinctness':'No predeclared decision-axis human rubric or evaluated contrasts were identified.',
'fairness':'No explicit controlled-condition audit tied to an artifact/alternative set was qualified.',
'preview-operability':'Browser action source is present, but preview versus shell scope, required checks and their outcomes remain unqualified.',
'feedback-fidelity':'No complete export case with required identity/notes/context preservation was qualified from matched log records.',
'decision-usefulness':'No explicit supported-choice/usefulness response linked to a review revision was qualified; preference selection alone is insufficient.',
'shell-overhead':'No defensible active-effort attribution separates review apparatus from component authoring.',
 'task-completeness':'No brief-bound application outcomes with activation and matched observed results were qualified.',
'hypothesis-coverage':'No brief-bound requested-decision rubric with inspected alternative tradeoffs was qualified.',
'review-correctness':'Browser action source is present, but specified shell operations and state-isolation outcomes are not qualified.',
'feedback-portability':'No original/round-tripped export case with comment/target/choice/revision identity was qualified.',
'revision-fidelity':'No identified revision attempt with both requested-change and predecessor preservation outcomes was qualified.',
'delivery-integrity':'Logged delivery claims lack a complete correlated dependency/provenance/verification audit.'}

def analyze(index,session_root,out):
    records=json.loads(index.read_bytes());observations=[];sources=[];counts=collections.Counter();seen=set();total=0
    for record in records[:100]:
        p=Path(record['path']).absolute()
        if session_root not in p.parents or p.resolve()!=p or any('holdout' in x.lower() or x.lower() in ('secrets','credentials') for x in p.parts):counts['excludedSources']+=1;continue
        try:fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
        except OSError:counts['unavailableSources']+=1;continue
        with os.fdopen(fd,'rb') as f:
            a=os.fstat(f.fileno())
            if not stat.S_ISREG(a.st_mode) or a.st_size>32*1024*1024:counts['oversized']+=1;continue
            if total+a.st_size>512*1024*1024:counts['totalByteBudget']=1;break
            raw=f.read(32*1024*1024+1);z=os.fstat(f.fileno())
        if len(raw)>32*1024*1024 or (a.st_size,a.st_mtime_ns)!=(z.st_size,z.st_mtime_ns):counts['changedSources']+=1;continue
        total+=len(raw);h=sha(raw)
        if h in seen:counts['exactCopies']+=1;continue
        seen.add(h);o=parse(raw);observations.append(o);sources.append({'path':str(p),'sha256':h,'bytes':len(raw)});counts['sessionsAnalyzed']+=1
    all_turns=[{**t,'traceSHA256':o['traceSHA256']} for o in observations for t in o['turns']];cards=[];contracts=json.loads((SKILL/'references/kpis.json').read_bytes())
    for s in contracts['skills']:
        turns=[t for t in all_turns if s['id'] in t['skillsReferenced']];candidate=[t for t in turns if t['category']=='candidate-real-use' and not t['reportingHintCalls']]
        access=[t for t in turns if t['category'] in ('candidate-real-use','unclassified') and not t['reportingHintCalls']]
        reads=[{'traceSHA256':t['traceSHA256'],'turnIdentityHash':t['turnIdentityHash'],**e} for t in access for e in t['evidence'] if e['skillScope']==s['id']]
        summaries={'candidateUseTurns':len(candidate),'classification':'inferred, not independently confirmed','excludedOrUnclassifiedTurns':len(turns)-len(candidate),'sourceAccessTurnsWithMissingBrief':sum(t['category']=='unclassified' for t in access),'completeCandidateTurns':sum(t['startedAndCompleted'] for t in candidate),'singleSkillReadCalls':len(reads),'loggedSingleSkillReadReturnBytes':sum(e['loggedReturnBytes'] for e in reads),'browserActionSourceHints':sum(t['browserActionHintCalls'] for t in candidate),'assertionSourceHints':sum(t['assertionHintCalls'] for t in candidate),'measuredPerformanceKpis':0}
        metrics=[{'id':k['id'],'value':None,'status':'not-measured','evidenceState':'insufficient','reason':MISSING[k['id']],'missingEvidence':MISSING[k['id']]} for k in s['kpis']]
        if s['id']=='base-ui':next(m for m in metrics if m['id']=='context-burden')['observedProxy']={'label':'Logged single-skill read returns','value':summaries['loggedSingleSkillReadReturnBytes'],'count':len(reads),'unit':'bytes','qualityQualified':False}
        cards.append({**s,'candidateDocuments':sum(any(s['id'] in t['skillsReferenced'] for t in o['turns']) for o in observations),'traceObservations':[],'useAnalysis':summaries,'readEvidence':reads,'metrics':metrics})
    coverage={'uniqueCandidateDocuments':len(sources),'stopReason':'total-byte-budget' if counts['totalByteBudget'] else None,'counts':dict(counts),'limitations':['The supplied source selection comes from a bounded external search; selection coverage is recorded separately and is not exhaustive.','Native-session access was scoped by explicit user request for relevant real-use logs; unrelated messages are discarded.','User-turn category and source-code action classifications are inferences, not task correctness.','No trial, raw-log copying, instrumentation change or target change.']}
    report={'schemaVersion':1,'status':'real-use-trace-analysis','coverage':coverage,'skills':cards,'styling':None};render(report,out,SKILL.parent/'base-ui');(out/'report-card.json').write_text(json.dumps(report,indent=2)+'\n');(out/'evidence-index.json').write_text(json.dumps({'schemaVersion':1,'sources':sources,'coverage':coverage},indent=2)+'\n');(out/'native-observations.json').write_text(json.dumps(observations,indent=2)+'\n')
    return {'status':'real-use-trace-analysis','sessionsAnalyzed':len(sources),'dashboard':str(out/'index.html'),'measuredPerformanceKpis':0,'skills':{s['id']:s['useAnalysis'] for s in cards}}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--index',required=True);p.add_argument('--session-root',required=True);p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output).absolute();sr=Path(a.session_root).absolute()
    if out.exists() or out.resolve()!=out or sr==out or sr in out.parents or SKILL.parent==out or SKILL.parent in out.parents:p.error('Fresh output outside sessions/skills required')
    out.mkdir(parents=True,mode=0o700)
    try:result=analyze(Path(a.index),sr,out)
    except (OSError,ValueError,TypeError,KeyError,RecursionError):print(json.dumps({'status':'analysis-failed','rawLogsKeptLocal':True}));return 1
    print(json.dumps(result));return 0
if __name__=='__main__':sys.exit(main())
