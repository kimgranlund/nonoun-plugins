// The review shell's own trimmed kit: foundation CSS, control compilation and token membership.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {geometryCSS} from './geometry.mjs';
export const kitRoot=path.resolve(import.meta.dirname,'../assets/kit');
const read=name=>fs.readFileSync(path.join(kitRoot,name));
// Local, pinned font binaries only; each face and license is checked against the manifest hash.
function fontCSS(){
  const manifest=JSON.parse(read('fonts/manifest.json'));
  const bytes=record=>{const b=read(path.join('fonts',record.file));if(createHash('sha256').update(b).digest('hex')!==record.sha256)throw Error('Bundled font integrity mismatch: '+record.file);return b;};
  const licenses=manifest.licenses.map(r=>'/* '+r.file+'\n'+bytes(r).toString('utf8').replaceAll('*/','* /').replaceAll('<','\\3c ')+'\n*/').join('\n');
  return licenses+'\n'+manifest.faces.map(f=>`@font-face { font-family:${JSON.stringify(f.family)}; font-style:${f.style}; font-weight:${f.weight}; font-display:swap; src:url("data:font/woff2;base64,${bytes(f).toString('base64')}") format("woff2"); }`).join('\n');
}
export function foundationCSS(){
  if(!fs.existsSync(kitRoot))throw Error('Missing vendored kit: '+kitRoot);
  return [fontCSS(),read('colors.css').toString('utf8'),read('typography.css').toString('utf8'),geometryCSS()].join('\n');
}
// Lexical membership only: every var(--x) must be declared in the foundation or the checked CSS itself.
export function unknownTokens(css,foundation=foundationCSS()){
  const strip=t=>t.replace(/\/\*[\s\S]*?\*\//g,'');
  const declared=new Set([...strip(foundation+'\n'+css).matchAll(/(--[\w-]+)\s*:/g)].map(m=>m[1]));
  return [...new Set([...strip(css).matchAll(/var\(\s*(--[\w-]+)(?=\s*[,)])/g)].map(m=>m[1]).filter(n=>!declared.has(n)))].sort();
}
// Phosphor caret-down, the trailing indicator for a native select.
const SELECT_INDICATOR='<span data-slot="indicator" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true" focusable="false"><path fill="currentColor" stroke="none" d="M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z"/></svg></span>';
// Build-time markup compilation for the shell: class normalization and the native select wrapper.
export function compileControls(html){
  const parts=html.match(/<!--[\s\S]*?-->|<(script|style|textarea)\b(?:[^>"']|"[^"]*"|'[^']*')*>[\s\S]*?<\/\1\s*>|<(?:[^>"']|"[^"]*"|'[^']*')*>|[^<]+|</gi)||[];
  const stack=[];let out='';
  for(let token of parts){
    if(!/^<\/?[a-z]/i.test(token)||/^<(script|style|textarea)\b/i.test(token)){out+=token;continue;}
    const tag=token.match(/^<\/?([\w-]+)/)[1].toLowerCase();
    if(/^<\//.test(token)){const i=stack.findLastIndex(item=>item.tag===tag);const item=i<0?null:stack[i];if(i>=0)stack.splice(i);out+=token;if(tag==='select'&&item?.wrapped)out+=SELECT_INDICATOR+'</span>';continue;}
    token=token.replace(/\sclass\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i,(_,a,b,c)=>' class="'+[...new Set((a??b??c).split(/\s+/).filter(Boolean))].join(' ')+'"');
    const classes=(token.match(/\sclass="([^"]*)"/)?.[1]||'').split(/\s+/);
    const wrapped=tag==='select'&&!stack.at(-1)?.classes.includes('select__root');
    if(wrapped)out+='<span class="select__root">';
    out+=token;
    if(!/^(?:area|base|br|col|embed|hr|img|input|link|meta|param|source|track|wbr)$/.test(tag)&&!token.endsWith('/>'))stack.push({tag,wrapped,classes});
  }
  return out;
}
