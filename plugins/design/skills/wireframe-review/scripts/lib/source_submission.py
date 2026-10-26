"""Source-only evaluator admission. Declared controllers are part of sealed input."""
import hashlib,json,shutil
from pathlib import Path

def child(base,value):
    if not isinstance(value,str) or not value: raise ValueError('Nonempty relative source path required')
    target=(base/value).resolve()
    if Path(value).is_absolute() or not target.is_relative_to(base.resolve()) or target==base.resolve(): raise ValueError('Source path escapes assigned directory')
    return target

def validate_packet(lane,packet):
    if not isinstance(packet,dict) or not isinstance(packet.get('sources'),list) or not packet['sources']: raise ValueError('Nonempty sources required')
    for item in packet['sources']:
        source=child(lane,item['path'])
        if not source.is_dir(): raise ValueError('Missing source directory')
        if item.get('controller') is not None:
            controller=child(source,item['controller'])
            if not controller.is_file(): raise ValueError('Missing declared controller')
    return packet

def submission(lane,expected,final=None):
    # Explicit packets own metadata, including arbitrary relative controller names.
    for file in [lane/'submission.json']+[child(lane,x['path'])/'submission.json' for x in expected['sources']]:
        if file.exists():
            try: packet=json.loads(file.read_text())
            except json.JSONDecodeError: continue # writer has not finished its signal
            return validate_packet(lane,packet)
    if final is None: return None
    if not all(x['path'] in final for x in expected['sources']): return None
    packet=json.loads(json.dumps(expected))
    for item in packet['sources']:
        source=child(lane,item['path'])
        if item.get('controller') is not None: continue # evaluator's explicit envelope
        declared=[f for f in source.rglob('*.js') if str(f) in final or item['path']+'/'+str(f.relative_to(source)) in final]
        if len(declared)>1: raise ValueError('Multiple final controller paths; use an explicit submission packet')
        if declared: item['controller']=str(declared[0].relative_to(source))
    return validate_packet(lane,packet)

def seal(lane,packet,destination):
    validate_packet(lane,packet);destination.mkdir(exist_ok=False);sources=[]
    for index,item in enumerate(packet['sources']):
        target=destination/str(index);shutil.copytree(child(lane,item['path']),target)
        sources.append(dict(item,sealedPath=str(target)))
    (destination/'submission.json').write_text(json.dumps(dict(packet,sources=sources),indent=2))
    hashes={str(f.relative_to(destination)):hashlib.sha256(f.read_bytes()).hexdigest() for f in destination.rglob('*') if f.is_file()}
    (destination/'hashes.json').write_text(json.dumps(hashes,indent=2))
    return str(destination)
