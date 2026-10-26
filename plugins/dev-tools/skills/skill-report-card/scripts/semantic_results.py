"""Aggregate bounded semantic reviews without reading their raw evidence."""
import json, hashlib, argparse, sys
from pathlib import Path
from report import render
SKILL=Path(__file__).resolve().parents[1]
ORIGINS={'explicit-human','reported','inferred','observed'}
OUTCOMES={'pass','fail','unverified','not-applicable'}

def aggregate(cases):
    groups={}
    for c in cases:
        if c['metricId'] in {'context-burden','shell-overhead'} and c.get('eligible',True) and c['outcome'] in {'pass','fail'}:raise ValueError('Telemetry KPI requires a unit-specific adapter')
        if c['outcome'] not in OUTCOMES or c['origin'] not in ORIGINS or c['confidence'] not in {'high','medium','low'}:raise ValueError('Invalid semantic case')
        if not c.get('provenance') or not isinstance(c['cohort'],dict):raise ValueError('Missing provenance/cohort')
        for p in c['provenance']:
            h=p.get('sha256','')
            if len(h)!=64 or any(x not in '0123456789abcdef' for x in h):raise ValueError('Missing evidence identity')
        cohort=json.dumps(c['cohort'],sort_keys=True)
        key=(c['skillId'],c['metricId'],cohort,bool(c.get('retrospectiveRubric',False)))
        identity=(c['attemptId'],c['criterionId'])
        groups.setdefault(key,{}).setdefault(identity,[]).append(c)
    results=[]
    for (skill,metric,cohort,retro),identities in groups.items():
        n=d=missing=na=conflicts=inferred=reported=0;confidences=set();origins=set()
        for rows in identities.values():
            signatures={(r['outcome'],r.get('eligible',True)) for r in rows}
            if len(signatures)>1:conflicts+=1;continue
            c=rows[0]
            if c['outcome']=='not-applicable':na+=1;continue
            if not c.get('eligible',True) or c['outcome']=='unverified':missing+=1;continue
            d+=1;n+=c['outcome']=='pass'
            inferred+=any(r['origin']=='inferred' for r in rows)
            reported+=all(r['origin']=='reported' for r in rows)
            confidences.update(r['confidence'] for r in rows);origins.update(r['origin'] for r in rows)
        results.append({'skillId':skill,'metricId':metric,'cohort':json.loads(cohort),'retrospectiveRubric':retro,'numerator':n,'denominator':d,'value':n/d if d else None,'missingCases':missing,'notApplicableCases':na,'conflictingCases':conflicts,'inferredCases':inferred,'reportedCases':reported,'confidence':sorted(confidences),'origins':sorted(origins),'assessmentConfidence':sorted({r['confidence'] for rows in identities.values() for r in rows}),'uniqueCases':len(identities)})
    return results

def validate_packet(value):
    if isinstance(value,dict):
        for key,v in value.items():
            if key.lower() in {'raw','rawlog','rawlogs','command','commands','prompt','prompts','stdout','stderr','excerpt','excerpts','sourcecode'}:raise ValueError('Raw evidence field prohibited')
            validate_packet(v)
    elif isinstance(value,list):
        if len(value)>1000:raise ValueError('Review bound exceeded')
        for v in value:validate_packet(v)
    elif isinstance(value,str) and len(value)>4000:raise ValueError('Review text bound exceeded')

def evidence_items(value):
    if isinstance(value,str):return [value]
    if isinstance(value,list) and all(isinstance(x,str) for x in value):return value
    raise ValueError('Evidence descriptions must be text or a text list')

def integrate(base,packets):
    cases=[]
    contracts={(s['id'],k['id']) for s in base['skills'] for k in s['kpis']}
    for packet in packets:
        validate_packet(packet)
        if packet.get('schemaVersion')!=1:raise ValueError('Unsupported semantic schema')
        for c in packet['cases']:
            if (c['skillId'],c['metricId']) not in contracts:raise ValueError('Unknown KPI')
            population=packet.get('population') or packet.get('coverage',{}).get('population')
            if population and c['cohort'].get('population',population)!=population:raise ValueError('Case population conflicts with reviewer population')
            cases.append({**c,'cohort':{**c['cohort'],**({'population':population} if population else {})}})
    populations={c['cohort'].get('population','real-use') for c in cases}
    populations.update(p.get('population') or p.get('coverage',{}).get('population') for p in packets if p.get('population') or p.get('coverage',{}).get('population'))
    if len(populations)>1:raise ValueError('Render test and real-use populations separately')
    results=aggregate(cases);measured=0
    for s in base['skills']:
        skill_packets=[p for p in packets if p['skillId']==s['id']]
        populations=[p.get('population') or p.get('coverage',{}).get('population') for p in skill_packets]
        s['semanticReview']={
            'findings':[f for p in skill_packets for f in p.get('findings',[])],
            'coverage':[p.get('coverage',{}) for p in skill_packets],
            'population':next((v for v in populations if v),'real-use'),
            'classificationConfidence':sorted({c['confidence'] for p in skill_packets for c in p.get('classificationCases',[])+p.get('excludedStreams',[]) if c.get('confidence')})}

        # Syntax-only observations remain separate, with no broken trace-file link.
        s.pop('traceObservations',None)
        for m in s['metrics']:
            m.update(value=None,status='not-measured',evidenceState='insufficient')
            rows=[r for r in results if r['skillId']==s['id'] and r['metricId']==m['id']]
            qualified=[r for r in rows if r['denominator'] and not r['retrospectiveRubric']]
            m['semanticCohorts']=rows
            m['supportedResults']=qualified
            m['exploratoryResults']=[r for r in rows if r['denominator'] and r['retrospectiveRubric']]
            gaps=[x for p in packets if p['skillId']==s['id'] for g in p.get('metricCoverage',[]) if g['metricId']==m['id'] for x in evidence_items(g.get('missingEvidence',[]))]
            if gaps:m['reason']=' '.join(gaps)
            elif not rows:m['reason']='No eligible measurement case qualified in the reviewed sample. '+m.get('missingEvidence',m.get('reason',''))
            if qualified:
                measured+=1;m.update(value='; '.join(f"{r['numerator']}/{r['denominator']} ({r['value']:.0%})" for r in qualified),status='no-target',evidenceState='historical',reason='Separate cohort results from semantic review; inference and confidence shown below. No target judgment.')
            elif any(r['denominator'] for r in rows):
                m['reason']='Exploratory retrospective results available below; contracted KPI remains unmeasured.'
            elif rows:m['reason']=' '.join(dict.fromkeys(x for c in cases if c['skillId']==s['id'] and c['metricId']==m['id'] for x in evidence_items(c.get('missingEvidence',[])))) or 'No eligible measurement denominator established by semantic review.'
            coverage_rows=[g for p in skill_packets for g in p.get('metricCoverage',[]) if g['metricId']==m['id']]
            if not qualified:
                notes=[g.get('reason') for g in coverage_rows if g.get('reason')]
                if notes:m['reason']=' '.join(notes)
                if coverage_rows and all(g.get('state')=='not-applicable' for g in coverage_rows) and not any(r['missingCases'] or r['conflictingCases'] for r in rows):m.update(status='not-applicable',evidenceState='historical')
    base['status']='semantic-cohort-review';base['population']= 'controlled-test' if any(c['cohort'].get('population')=='controlled-test' for c in cases) or any(p.get('population')=='controlled-test' or p.get('coverage',{}).get('population')=='controlled-test' for p in packets) else 'real-use';base['coverage']['measuredPerformanceKpis']=measured
    base['coverage']['limitations']+=['Semantic review is observational and selected, not exhaustive or a causal skill-effect estimate.','Unknown skill versions and environments remain unknown; incompatible task cohorts are never pooled.','Raw logs and artifacts stay outside this dashboard; semantic case provenance is local metadata.']
    return base,{'schemaVersion':1,'cases':cases,'cohorts':results,'reviews':packets}

def main():
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--review',action='append',required=True);p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output).absolute()
    if out.exists() or SKILL.parent in out.parents: p.error('Fresh output outside skill root required')
    try:
        report,evidence=integrate(json.loads(Path(a.base).read_text()),[json.loads(Path(x).read_text()) for x in a.review])
        out.mkdir(mode=0o700,parents=True);render(report,out,SKILL.parent/'base-ui')
        (out/'report-card.json').write_text(json.dumps(report,indent=2)+'\n');(out/'semantic-observations.json').write_text(json.dumps(evidence,indent=2)+'\n')
        (out/'evidence-index.json').write_text(json.dumps({'schemaVersion':1,'reviewFiles':[{'path':x,'sha256':hashlib.sha256(Path(x).read_bytes()).hexdigest()} for x in a.review],'coverage':report['coverage']},indent=2)+'\n')
        print(json.dumps({'dashboard':str(out/'index.html'),'measuredKpis':report['coverage']['measuredPerformanceKpis'],'cases':len(evidence['cases'])}))
    except (OSError,ValueError,KeyError,TypeError):print(json.dumps({'status':'semantic-review-rejected','rawEvidenceKeptLocal':True}));return 1
    return 0
if __name__=='__main__':sys.exit(main())
