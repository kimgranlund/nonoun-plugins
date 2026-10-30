"""Locate truncation markers in returned envelopes, never call arguments."""
import json,re
MARKER=re.compile(r'(?:Warning: truncated output|Output truncated|output has been truncated|\[output truncated|\[\d+ characters truncated\])',re.I)
# Require the returned preview envelope, not a path mention or generic size warning.
# The lookahead keeps the marker itself an exact short excerpt of the return.
PERSISTED_PREVIEW=re.compile(
    r'\A\s*<persisted-output>(?=\s*\r?\n'
    r'Output too large \(\d+(?:\.\d+)?\s*(?:B|KB|MB|GB)\)\. '
    r'Full output saved to: [^\r\n]+\r?\n\s*'
    r'Preview \(first \d+(?:\.\d+)?\s*(?:B|KB|MB|GB)\):)', re.I)
def sites(event):
    try:raw=json.loads(event['evidence']['text'].split('\n\nDecoded tool/output attribution',1)[0])
    except ValueError:raw=event['evidence']['text']
    output=raw.get('output',raw) if isinstance(raw,dict) else raw
    location='/output'
    claude_block=isinstance(raw,dict) and 'block' in raw
    if claude_block:
        block=raw['block']
        if not isinstance(block,dict) or block.get('type')!='tool_result':return []
        output=block.get('content','');location='/block/content'
    wrapped=isinstance(output,list) and not claude_block;found=[]
    def walk(value,path,nested=False):
        if isinstance(value,str):
            try:decoded=json.loads(value)
            except ValueError:decoded=None
            if isinstance(decoded,(dict,list)):walk(decoded,path+'/decoded',nested);return
            match=MARKER.search(value) or PERSISTED_PREVIEW.match(value)
            if match:
                token=re.search(r'original token count:\s*(\d+)',value[match.start():match.start()+150])
                found.append(dict(layer='nested-command' if nested else 'outer-aggregation' if wrapped else 'command-or-unknown',location=path,marker=match.group(),originalTokens=int(token[1]) if token else None))
        elif isinstance(value,list):
            for i,item in enumerate(value):walk(item,path+'/'+str(i),nested)
        elif isinstance(value,dict):
            if 'output' in value:walk(value['output'],path+'/output',wrapped)
            elif 'text' in value:walk(value['text'],path+'/text',nested)
            elif 'content' in value:walk(value['content'],path+'/content',nested)
    walk(output,location)
    return found
