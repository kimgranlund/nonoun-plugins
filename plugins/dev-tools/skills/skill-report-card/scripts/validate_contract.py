#!/usr/bin/env python3
"""Validate the bundled schema's supported vocabulary plus cross-reference invariants. Stdlib only."""
import json,re,sys,hashlib,math
from pathlib import Path
SCHEMA=Path(__file__).resolve().parents[1]/'references/performance-contract.schema.json'
SUPPORTED={'$schema','title','description','type','properties','required','additionalProperties','items','minItems','maxItems','minLength','pattern','const','enum','oneOf'}
def validate_schema(node):
    unknown=set(node)-SUPPORTED
    if unknown:raise ValueError('Unsupported schema keywords: '+','.join(sorted(unknown)))
    for sub in node.get('properties',{}).values():validate_schema(sub)
    if 'items' in node:validate_schema(node['items'])
    for sub in node.get('oneOf',[]):validate_schema(sub)
def check(value,node,where='$'):
    def fail(message):raise ValueError(where+': '+message)
    if 'oneOf' in node:
        matches=0
        for sub in node['oneOf']:
            try:check(value,sub,where);matches+=1
            except ValueError:pass
        if matches!=1:fail('expected exactly one permitted shape')
    if 'const' in node and (value!=node['const'] or type(value)!=type(node['const'])):fail('incorrect constant')
    if 'enum' in node and value not in node['enum']:fail('unsupported value')
    typ=node.get('type');types={'object':dict,'array':list,'string':str,'null':type(None)}
    if typ in types and not isinstance(value,types[typ]):fail('expected '+typ)
    if typ=='number' and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value)):fail('expected finite number')
    if isinstance(value,dict) and typ=='object':
        if set(node.get('required',[]))-set(value):fail('missing required fields')
        if node.get('additionalProperties') is False and set(value)-set(node.get('properties',{})):fail('unknown fields')
        for key,sub in node.get('properties',{}).items():
            if key in value:check(value[key],sub,where+'.'+key)
    if isinstance(value,list) and typ=='array':
        if not node.get('minItems',0)<=len(value)<=node.get('maxItems',float('inf')):fail('array length outside limits')
        for i,item in enumerate(value):check(item,node['items'],where+f'[{i}]')
    if isinstance(value,str):
        if len(value.strip())<node.get('minLength',0):fail('empty text')
        if 'pattern' in node and not re.fullmatch(node['pattern'],value):fail('invalid format')
def validate(value):
    schema=json.loads(SCHEMA.read_text());validate_schema(schema);check(value,schema)
    goals=[value['goals']['primary'],*value['goals']['secondary']];ids=[g['id'] for g in goals]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate goal IDs')
    kpis=value['kpis'];kids=[k['id'] for k in kpis]
    if len(kids)!=len(set(kids)):raise ValueError('Duplicate KPI IDs')
    for k in kpis:
        refs=k['goalIds']
        if len(refs)!=len(set(refs)) or set(refs)-set(ids):raise ValueError('Invalid/duplicate goal references: '+k['id'])
        if k['defaultTarget'] is not None and k['unit']=='proportion' and not 0<=k['defaultTarget']['value']<=1:raise ValueError('Proportion target must be 0..1')
    if not any(value['goals']['primary']['id'] in k['goalIds'] for k in kpis):raise ValueError('Primary goal has no KPI')
    return {'valid':True,'skillId':value['skillId'],'contractVersion':value['contractVersion'],'kpis':len(kpis),'limits':'Structural checks only; conceptual overlap, evidence adequacy and target validity require review.'}
if __name__=='__main__':
    try:
        if len(sys.argv)!=2:raise ValueError('Usage: validate_contract.py CONTRACT.json')
        raw=Path(sys.argv[1]).read_bytes();result=validate(json.loads(raw,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Non-finite JSON number'))));result['sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(result))
    except (ValueError,OSError) as e:print(str(e),file=sys.stderr);sys.exit(1)
