"""Recover only explicitly emitted store snapshots. No hidden tool results inferred."""
import json,re
from wrapped import Parser,Unsupported,pair_outputs

def snapshot(code,output):
    # One precise producer idiom: a literal ID list, paths built per ID, then
    # store the map and emit that identical map. Do not read generated files.
    pattern=r"\s*const ids=(\[.*?\]);store\('ids',ids\);\s*const paths=\{\};for\(const id of ids\)\{const r=await tools.exec_command\(\{cmd:`[^`]*`,max_output_tokens:\d+\}\);paths\[id\]=JSON.parse\(r.output\).tiles.map\(t=>t.path\);\}store\('details',paths\);text\(paths\);\s*"
    match=re.fullmatch(pattern,code,re.S)
    if not match:return None
    templates=re.findall(r'`([^`]*)`',code)
    if any('${' in re.sub(r'\$\{id\}', '',text) for text in templates):return None
    try:
        p=Parser(match[1]);ids=p.value();p.space()
        if p.pos!=len(match[1]) or not isinstance(ids,list) or not ids or len(ids)>128 or len(set(ids))!=len(ids) or not all(isinstance(x,str) for x in ids):return None
        blocks=pair_outputs(output,[{'emit':'text'}])
        if not blocks or not isinstance(blocks[0],dict):return None
        paths=blocks[0]
        if set(paths)!=set(ids) or any(not isinstance(v,list) or len(v)>128 or not all(isinstance(x,str) and x.startswith('/') for x in v) for v in paths.values()):return None
        return {'ids':ids,'details':paths}
    except (Unsupported,ValueError,TypeError):return None

def prefix_outputs(output,calls):
    if isinstance(output,str):
        try:output=json.loads(output)
        except ValueError:return None
    if not isinstance(output,list):return None
    blocks=list(output)
    if blocks and re.fullmatch(r'Script completed\nWall time [^\n]+\nOutput:\n?',blocks[0].get('text','')):blocks=blocks[1:]
    else:return None
    if len(blocks)<len(calls):return None
    return pair_outputs(blocks[:len(calls)],calls)
