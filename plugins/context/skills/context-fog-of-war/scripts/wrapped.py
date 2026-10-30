"""Static, deliberately small JavaScript wrapper grammar. Never executes source."""
import json
import re
import shlex
from pathlib import Path


class Unsupported(ValueError): pass


class Parser:
    def __init__(self, text, env=None): self.text=text; self.pos=0; self.env=env or {}
    def space(self):
        while True:
            m=re.match(r'(?:\s+|//[^\n]*(?:\n|$)|/\*[\s\S]*?\*/)',self.text[self.pos:])
            if not m: break
            self.pos+=len(m[0])
    def take(self, token):
        self.space()
        if not self.text.startswith(token,self.pos): raise Unsupported('Unsupported wrapper syntax')
        self.pos+=len(token)
    def ident(self):
        self.space();m=re.match(r'[A-Za-z_$][\w$]*',self.text[self.pos:])
        if not m: raise Unsupported('Expected identifier')
        self.pos+=len(m[0]);return m[0]
    def string(self):
        self.space();quote=self.text[self.pos];self.pos+=1;out=''
        while self.pos<len(self.text):
            char=self.text[self.pos];self.pos+=1
            if char==quote:return out
            if char in '\r\n':raise Unsupported('Unescaped newline')
            if char=='\\':
                if self.pos>=len(self.text):raise Unsupported('Incomplete escape')
                char=self.text[self.pos];self.pos+=1
                escapes={'n':'\n','r':'\r','t':'\t','b':'\b','f':'\f','v':'\v','0':'\0','\\':'\\','"':'"',"'":"'",'/':'/'}
                if char in escapes:char=escapes[char]
                elif char in ('u','x'):
                    size=4 if char=='u' else 2;code=self.text[self.pos:self.pos+size]
                    if not re.fullmatch('[0-9A-Fa-f]{'+str(size)+'}',code):raise Unsupported('Invalid escape')
                    char=chr(int(code,16));self.pos+=size
                else:raise Unsupported('Unsupported escape')
            out+=char
        raise Unsupported('Unterminated string')
    def value(self, depth=0):
        value=self.atom(depth);self.space()
        while self.text[self.pos:self.pos+1] in ('.','['):
            if self.text[self.pos]=='.':
                self.take('.');key=self.ident()
                if key=='slice':
                    self.take('(');start=self.value(depth+1);self.space();end=None
                    if self.text[self.pos:self.pos+1]==',':self.take(',');end=self.value(depth+1)
                    self.take(')')
                    if not isinstance(value,list) or type(start)!=int or (end is not None and type(end)!=int):raise Unsupported('Invalid literal slice')
                    value=value[start:end]
                else:
                    if not isinstance(value,dict) or key not in value:raise Unsupported('Missing stored field')
                    value=value[key]
            else:
                self.take('[');key=self.value(depth+1);self.take(']')
                if isinstance(value,dict) and isinstance(key,str) and key in value:value=value[key]
                elif isinstance(value,list) and type(key)==int and 0<=key<len(value):value=value[key]
                else:raise Unsupported('Unknown stored lookup')
            self.space()
        while self.text[self.pos:self.pos+1]=='+':
            self.take('+');other=self.atom(depth)
            if not isinstance(value,str) or not isinstance(other,(str,int)):raise Unsupported('Only literal string concatenation supported')
            value+=str(other);self.space()
        return value
    def atom(self, depth=0):
        if depth>20:raise Unsupported('Literal nesting limit')
        self.space()
        if self.pos>=len(self.text):raise Unsupported('Missing literal')
        c=self.text[self.pos]
        if self.text.startswith('load(',self.pos):
            self.take('load(');key=self.value(depth+1);self.take(')')
            stored=self.env.get('__recorded_store__',{})
            if not isinstance(key,str) or key not in stored:raise Unsupported('Unknown stored value')
            return stored[key]
        if c=='`':
            self.pos+=1;end=self.text.find('`',self.pos)
            if end<0:raise Unsupported('Unclosed template')
            template=self.text[self.pos:end]
            if '\\' in template:raise Unsupported('Template escapes unsupported')
            def substitute(m):
                key=m.group(1)
                if key not in self.env or not isinstance(self.env[key],(str,int)):raise Unsupported('Dynamic template expression')
                return str(self.env[key])
            value=re.sub(r'\$\{([A-Za-z_$][\w$]*)\}',substitute,template)
            if '${' in value:raise Unsupported('Dynamic template')
            self.pos=end+1;return value
        if c in "\"'":return self.string()
        match=re.match(r'[A-Za-z_$][\w$]*',self.text[self.pos:])
        if match and match[0] != '__recorded_store__' and match[0] in self.env:self.pos+=len(match[0]);return self.env[match[0]]
        if c=='{':
            self.take('{');obj={};self.space()
            if self.text[self.pos:self.pos+1]=='}':self.take('}');return obj
            while True:
                self.space();key=self.string() if self.text[self.pos:self.pos+1] in ('"',"'") else self.ident()
                if key in obj:raise Unsupported('Duplicate key')
                self.space()
                if self.text[self.pos:self.pos+1]==':':self.take(':');obj[key]=self.value(depth+1)
                elif key in self.env:obj[key]=self.env[key]
                else:raise Unsupported('Unknown shorthand')
                self.space()
                if self.text[self.pos:self.pos+1]=='}':self.take('}');return obj
                self.take(',');self.space()
                if self.text[self.pos:self.pos+1]=='}':self.take('}');return obj
        if c=='[':
            self.take('[');items=[];self.space()
            if self.text[self.pos:self.pos+1]==']':self.take(']');return items
            while True:
                items.append(self.value(depth+1));self.space()
                if self.text[self.pos:self.pos+1]==']':self.take(']');return items
                self.take(',')
        for literal,value in [('true',True),('false',False),('null',None)]:
            if self.text.startswith(literal,self.pos):self.pos+=len(literal);return value
        m=re.match(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?',self.text[self.pos:])
        if m:self.pos+=len(m[0]);return json.loads(m[0])
        raise Unsupported('Dynamic JavaScript argument')
    def tool(self):
        keyword=self.ident()
        if keyword!='await':raise Unsupported('Expected await')
        self.take('tools.');name=self.ident();self.take('(');args=self.value();self.take(')');return name,args


def batch(p):
    p.take('await');p.take('Promise.');kind=p.ident()
    if kind not in ('all','allSettled'):raise Unsupported('Unsupported Promise operation')
    p.take('(');p.take('[');items=[];p.space()
    while p.text[p.pos:p.pos+1]!=']':
        p.take('tools.');name=p.ident();p.take('(');args=p.value();p.take(')')
        items.append({'name':name,'args':args,'emit':'text'})
        p.space()
        if p.text[p.pos:p.pos+1]==']':break
        p.take(',');p.space()
    p.take(']');p.take(')')
    return {'name':'Promise.'+kind,'args':{},'emit':'text','batch':kind,'items':items}


def loop_body(p):
    p.space();start=p.pos;brace=p.text[start:start+1]=='{';depth=0;quote=None;escape=False
    for i in range(start,len(p.text)):
        c=p.text[i]
        if quote:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c==quote:quote=None
            continue
        if c in ('"',"'",'`'):quote=c;continue
        if c=='{':depth+=1
        elif c=='}':
            depth-=1
            if brace and depth==0:p.pos=i+1;return p.text[start+1:i]
        elif c==';' and not brace and depth==0:p.pos=i+1;return p.text[start:i+1]
    raise Unsupported('Incomplete loop body')


def indexed_loop(p, variable):
    """Accept only the ascending `for(let i=0;i<v.length;i++)text({i,...v[i]});` emitter."""
    v=re.escape(variable)
    m=re.match(r'for\s*\(\s*let\s+([A-Za-z_$][\w$]*)\s*=\s*0\s*;\s*\1\s*<\s*'+v+r'\.length\s*;\s*\1\s*\+\+\s*\)\s*(\{)?\s*text\(\s*\{\s*\1\s*,\s*\.\.\.\s*'+v+r'\[\s*\1\s*\]\s*\}\s*\)\s*;?\s*(\})?\s*;?',p.text[p.pos:])
    if not m or bool(m.group(2))!=bool(m.group(3)):return None
    p.pos+=len(m[0]);return m.group(1)


def parse_calls(code, _env=None, _depth=0, _prefix=False):
    if not isinstance(code,str) or len(code)>2_000_000:return None
    if _depth>4:return None
    p=Parser(code,_env);calls=[];batch_serial=0
    try:
        p.space()
        while p.pos<len(code):
            if p.text.startswith('if(![',p.pos):
                p.take('if(!');blocked=p.atom();p.take('.some(x=>path.includes(x)))')
                if not isinstance(blocked,list) or not all(isinstance(x,str) for x in blocked) or not isinstance(p.env.get('path'),str):raise Unsupported('Unknown path filter')
                body=loop_body(p)
                entries=parse_calls(body,p.env,_depth+1)
                if entries is None:raise Unsupported('Unsupported filtered body')
                if not any(x in p.env['path'] for x in blocked):calls.extend(entries)
                p.space();continue
            if re.match(r'for\s*\(',p.text[p.pos:]):
                p.take('for');p.take('(');p.take('const');variable=p.ident();p.take('of');values=p.value();p.take(')')
                if not isinstance(values,list) or not values or len(values)>128 or not all(isinstance(v,(str,int,dict)) and not isinstance(v,bool) for v in values):raise Unsupported('Only bounded literal loops')
                body=loop_body(p)
                for value in values:
                    entries=parse_calls(body,dict(p.env,**{variable:value}),_depth+1)
                    if entries is None:raise Unsupported('Unsupported loop body')
                    calls.extend(entries)
                    if len(calls)>1024:raise Unsupported('Expanded call limit')
                p.space();continue
            emit=p.ident()
            if emit in ('const','let'):
                variable=p.ident();p.take('=');entry=batch(p);batch_serial+=1;entry['batchIndex']=batch_serial;p.take(';');p.space()
                indexed=indexed_loop(p,variable)
                if p.text.startswith(variable+'.forEach',p.pos):
                    p.take(variable+'.forEach(text)');p.take(';')
                    batch_index=batch_serial
                    for slot,item in enumerate(entry['items']):calls.append(dict(item,settlement=entry['batch'],slot=slot+1,batchIndex=batch_index))
                elif indexed:
                    # Each emitted block carries its own index, so pairing can verify order.
                    for slot,item in enumerate(entry['items']):calls.append(dict(item,settlement=entry['batch'],slot=slot+1,batchIndex=batch_serial,indexKey=indexed,index=slot))
                else:
                    p.take('text(');p.take(variable);p.take(')');p.take(';');calls.append(entry)
                p.space();continue
            p.take('(');p.space()
            if emit=='text' and re.match(r'await\s+Promise\.',p.text[p.pos:]):
                entry=batch(p);batch_serial+=1;entry['batchIndex']=batch_serial;p.take(')');p.take(';');calls.append(entry);p.space();continue
            if emit=='text':name,args=p.tool();p.take(')')
            elif emit=='image':
                p.take('(');name,args=p.tool();p.take(').image_url)')
                if name!='view_image':raise Unsupported('Unsupported image tool')
            else:raise Unsupported('Unsupported emitter')
            p.take(';');calls.append({'name':name,'args':args,'emit':emit});p.space()
        return calls if calls or _depth else None
    except (Unsupported,IndexError):return calls if _prefix and _depth==0 and calls else None


def expand_pairs(calls, outputs):
    """Promise result arrays preserve input order, never completion order."""
    expanded=[]
    for batch_index,(call,result) in enumerate(zip(calls,outputs),1):
        items=call.get('items',[call]);values=result if 'batch' in call else [result]
        if not isinstance(values,list) or len(items)!=len(values):return None
        for slot,(item,value) in enumerate(zip(items,values),1):
            mode=call.get('batch',call.get('settlement'))
            status='fulfilled'
            if mode=='allSettled':
                if not isinstance(value,dict) or value.get('status') not in ('fulfilled','rejected'):return None
                status=value['status'];key='value' if status=='fulfilled' else 'reason'
                if key not in value:return None
                value=value[key]
            tag=(f"Promise.{mode} batch {call.get('batchIndex',batch_index)} slot {call.get('slot',slot)}" if mode else f'Call {batch_index}')
            expanded.append((item,value,status,tag))
    return expanded


def pair_outputs(output,calls):
    if isinstance(output,str):
        try:output=json.loads(output)
        except ValueError:return None
    if not isinstance(output,list):return None
    blocks=list(output)
    if blocks and isinstance(blocks[0],dict) and blocks[0].get('type') in ('input_text','text') and re.fullmatch(r'Script completed\nWall time [^\n]+\nOutput:\n?',blocks[0].get('text','')):blocks=blocks[1:]
    if len(blocks)!=len(calls):return None
    paired=[]
    for call,block in zip(calls,blocks):
        if not isinstance(block,dict):return None
        if call['emit']=='image':
            if block.get('type') not in ('input_image','image'):return None
            paired.append(block);continue
        if block.get('type') not in ('input_text','text'):return None
        text=block.get('text')
        if not isinstance(text,str):return None
        try:decoded=json.loads(text)
        except ValueError:decoded=text
        key=call.get('indexKey')
        if key:
            if not isinstance(decoded,dict) or decoded.get(key)!=call['index']:return None
            decoded={k:v for k,v in decoded.items() if k!=key}
        paired.append(decoded)
    return paired


def read_requests(command):
    """Locate literal read requests; heredocs excluded to avoid parsing script bodies."""
    if not isinstance(command,str) or '<<' in command:return []
    try:
        lex=shlex.shlex(command,posix=True,punctuation_chars=';&|<>\n');lex.whitespace=' \t\r';lex.whitespace_split=True
        lex.commenters='#';tokens=list(lex)
    except ValueError:return []
    segments=[];current=[]
    for token in tokens:
        if token in (';', '\n', '&&','||'):
            if current:segments.append(current);current=[]
        else:current.append(token)
    if current:segments.append(current)
    if any(words and words[0] in ('cd','pushd','popd') for words in segments):return []
    requests=[]
    for words in segments:
        if any(t in ('|','>','>>','<','&') for t in words):continue
        if not words:continue
        tool=words[0];path=None;start=end=None
        if tool=='cat' and len(words)>=2 and not any(w.startswith('-') for w in words[1:]):
            requests.extend((w,None,None) for w in words[1:] if not any(c in w for c in '$*?`'));continue
        elif tool=='head' and len(words)==3 and re.fullmatch(r'-\d+',words[1]):path=words[2];start=1;end=int(words[1][1:])
        elif tool=='head' and len(words)==4 and words[1]=='-n' and words[2].isdigit():path=words[3];start=1;end=int(words[2])
        elif tool=='sed' and len(words)==4 and words[1]=='-n':
            m=re.fullmatch(r'(\d+),(\d+)p',words[2])
            if m:path=words[3];start,end=map(int,m.groups())
        if path and not any(c in path for c in '$*?`') and (start is None or 0<start<=end):requests.append((path,start,end))
    return requests



def scoped_read_requests(command, cwd):
    """Literal compound readers with one leading cd; paths are lexical, never executed.

    Returned bytes still need independent corroboration. An attempted cd is not
    itself proof that a shell changed directories, so callers must retain that limit.
    """
    if not isinstance(command,str) or '<<' in command:return []
    try:
        lex=shlex.shlex(command,posix=True,punctuation_chars=';&|<>\n')
        lex.whitespace=' \t\r';lex.whitespace_split=True;lex.commenters='#';tokens=list(lex)
    except ValueError:return []
    if tokens[:1]==['cd']:
        if len(tokens)<4 or tokens[2]!='&&' or any(c in tokens[1] for c in '$*?`'):return []
        import os
        cwd=os.path.normpath(tokens[1] if tokens[1].startswith('/') else os.path.join(cwd,tokens[1]))
        tokens=tokens[3:]
    segments=[];current=[]
    for token in tokens+[';']:
        if token in (';','\n','&&','||'):
            if current:segments.append(current)
            current=[]
        else:current.append(token)
    if any(words and words[0] in ('cd','pushd','popd') for words in segments):return []
    import os
    return [(os.path.normpath(target if target.startswith('/') else os.path.join(cwd,target)),start,end)
            for words in segments for target,start,end in read_requests(shlex.join(words))]

def corroborate(path, roots, output, start=None, end=None):
    """Match returned bytes against a bounded current-source witness, never invent contents."""
    resolved=Path(path).resolve()
    if not any(resolved==r or r in resolved.parents for r in roots):return None
    try:
        if resolved.stat().st_size>1_000_000:return None
        contents=resolved.read_text()
    except (OSError,UnicodeError):return None
    if start:contents=''.join(contents.splitlines(keepends=True)[start-1:end])
    if len(contents.strip())<32:return None
    # Whole-line matches reduce accidental attribution to incidental substrings.
    needle=contents.strip('\n')
    if re.search(r'(?:^|\n)'+re.escape(needle)+r'(?:\n|$)',output):return 'partial' if start else 'read'
    lines=needle.splitlines();prefix='\n'.join(lines[:8])
    if start is None and len(prefix)>120 and len(lines)>=8 and re.search(r'(?:^|\n)'+re.escape(prefix)+r'(?:\n|$)',output):return 'partial'
    return None
