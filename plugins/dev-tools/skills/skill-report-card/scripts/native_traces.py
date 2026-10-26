"""Scoped native-session analysis. Never returns prompts, commands or tool output."""
import json,re,hashlib,statistics,shlex,ast
SKILLS=('base-ui','component-variants','wireframe-review')
def sha(b):return hashlib.sha256(b).hexdigest()
def command(text):
    try:v=json.loads(text)
    except (ValueError,TypeError):v=None
    if isinstance(v,dict) and isinstance(v.get('cmd'),str):return v['cmd']
    if isinstance(v,dict) and isinstance(v.get('code'),str):return command(v['code'])
    matches=re.findall(r'\bcmd\s*:\s*("(?:[^"\\]|\\.)*")',text)
    if len(matches)==1:
        try:return json.loads(matches[0])
        except ValueError:pass
    single=re.findall(r"\bcmd\s*:\s*('(?:[^'\\]|\\.)*')",text)
    if len(single)==1:
        try:return ast.literal_eval(single[0])
        except (ValueError,SyntaxError):pass
    return None

def parse(raw):
    turns=[];current=None;calls={};outputs={};conflicts=set();unpaired=0
    def fresh():return {'id':None,'started':False,'complete':False,'category':'unclassified','model':None,'effort':None,'skills':set(),'calls':[],'userResponse':False}
    for lineno,b in enumerate(raw.splitlines(),1):
        if len(b)>2097152:continue
        try:r=json.loads(b)
        except (ValueError,UnicodeError,RecursionError):continue
        p=r.get('payload',{}) if isinstance(r,dict) else {}
        if not isinstance(p,dict):continue
        typ=p.get('type')
        if typ=='task_started':
            previous=current;current=fresh();current['id']=sha(str(p.get('turn_id',lineno)).encode());current['started']=True
            if previous and not previous['calls']:current['category']=previous['category'];current['userResponse']=previous['userResponse'];current['model']=previous['model'];current['effort']=previous['effort']
            turns.append(current)
        if current is None:current=fresh();current['id']=sha(b'pre-boundary');turns.append(current)
        if r.get('type')=='turn_context':
            current['model']=p.get('model') if isinstance(p.get('model'),str) and re.fullmatch('[a-z0-9][a-z0-9._/-]{1,64}',p['model']) else None
            current['effort']=p.get('effort') if p.get('effort') in ('low','medium','high','xhigh','max','ultra') else None
        if typ=='user_message' or (typ=='message' and p.get('role')=='user'):
            text=p.get('message','') if typ=='user_message' else '\n'.join(x.get('text','') for x in p.get('content',[]) if isinstance(x,dict) and isinstance(x.get('text'),str));text=text if isinstance(text,str) else ''
            if '## My request:' in text:text=text.split('## My request:',1)[1]
            if text.startswith(('# AGENTS.md instructions','<external_codex_apps_open_page>','<environment_context>')):continue
            if current['calls'] or current['complete']:
                previous=current;current=fresh();current['id']=sha(('user-boundary-'+str(lineno)).encode());current['model']=previous['model'];current['effort']=previous['effort'];turns.append(current)
            lower=text.lower()
            if any(x in lower for x in ('skill-report-card','report card','split-consumption','w5','skill performance','real-use logs','use-traces','test batch')):current['category']='reporting-or-study'
            elif any(x in lower for x in ('update the skill','improve the skill','skill-release','skill release','fix the skill','maintained skill','skill corpus')):current['category']='skill-maintenance'
            else:current['category']='candidate-real-use'
            current['userResponse']=bool(re.search(r'\b(this helped|helped me|i prefer.+because|i chose.+because|combine.+because)\b',lower))
        if typ in ('function_call','custom_tool_call'):
            ident=p.get('call_id');text=p.get('input',p.get('arguments',''))
            if not isinstance(ident,str) or not isinstance(text,str):continue
            h=sha(ident.encode());skills=[s for s in SKILLS if re.search(r'/'+s+r'/',text)]
            c=command(text)
            try:parts=shlex.split(c) if c else []
            except ValueError:parts=[]
            is_pure_read=bool(1<len(parts)<=16 and parts[0]=='cat' and all(not x.startswith('-') and not any(y in x for y in ';&|<>$`') for x in parts[1:]))
            single_skill=next((s for s in SKILLS if is_pure_read and all('/'+s+'/' in x for x in parts[1:])),None)
            if c and any(x in c for x in ('skill-report-card','split-consumption','/evals/','/check-','/test_')):is_pure_read=False
            call={'id':h,'line':lineno,'skills':skills,'pureRead':is_pure_read,'pureSkillReadSkill':single_skill if is_pure_read else None,'browserActionHint':bool(re.search(r'\.(click|fill|check|press|selectOption)\(',text)),'assertionHint':bool(re.search(r'assert\.|expect\(',text)),'reportingHint':any(x in text for x in ('skill-report-card','split-consumption-confirmation')),'fingerprint':sha(text.encode())}
            if h in calls:
                if calls[h]['fingerprint']!=call['fingerprint']:conflicts.add(h)
                continue
            calls[h]=call;current['calls'].append(h);current['skills'].update(skills)
        if typ in ('function_call_output','custom_tool_call_output'):
            ident=p.get('call_id');output=p.get('output')
            if not isinstance(ident,str):unpaired+=1;continue
            h=sha(ident.encode());text=output if isinstance(output,str) else json.dumps(output,ensure_ascii=False)
            o={'bytes':len(text.encode()),'sha256':sha(text.encode()),'line':lineno}
            if h in outputs and outputs[h]['sha256']!=o['sha256']:conflicts.add(h)
            else:outputs[h]=o
        if typ=='task_complete':current['complete']=True
    result=[]
    for t in turns:
        linked=[calls[h] for h in t['calls'] if h not in conflicts];skills=sorted(t['skills'])
        if not skills:continue
        paired=[(c,outputs[c['id']]) for c in linked if c['id'] in outputs];reads=[(c,o) for c,o in paired if c['pureRead'] and c['skills']]
        # A completed turn and tool output are not declared task acceptance or a quality gate.
        result.append({'turnIdentityHash':t['id'],'category':t['category'],'classification':'inferred-from-user-turn-keywords','skillsReferenced':skills,'model':t['model'],'effort':t['effort'],'startedAndCompleted':t['started'] and t['complete'],'toolCalls':len(linked),'pairedToolResults':len(paired),'missingToolResults':len(linked)-len(paired),'loggedToolReturnUtf8Bytes':sum(o['bytes'] for c,o in paired),'pureSkillReadCalls':len(reads),'pureSkillReadReturnBytes':sum(o['bytes'] for c,o in reads),'pureReadMedianBytes':statistics.median([o['bytes'] for c,o in reads]) if reads else None,'browserActionHintCalls':sum(c['browserActionHint'] for c in linked),'assertionHintCalls':sum(c['assertionHint'] for c in linked),'reviewerUsefulnessLanguageHint':t['userResponse'],'reportingHintCalls':sum(c['reportingHint'] for c in linked),'qualityAcceptance':'not-established','performanceEligible':False,'evidence':[{'callLine':c['line'],'resultLine':o['line'],'resultSHA256':o['sha256'],'skillScope':c['pureSkillReadSkill'],'loggedReturnBytes':o['bytes']} for c,o in reads]})
    return {'schemaVersion':1,'adapterVersion':'codex-native-trace/1.0.0','traceSHA256':sha(raw),'turns':result,'conflictingCallIdentities':len(conflicts),'unpairedOutputs':unpaired,'limits':['Turn classification is an inference; source-maintenance keywords are incomplete.','Tool-return bytes are logged strings; serialization/capture completeness is not established.','Browser actions/assertion source hints do not demonstrate expected effects or task acceptance.','No criterion/artifact/quality proof was qualified by this syntax-level parser; free-text semantic evidence and screenshots are not evaluated.']}
