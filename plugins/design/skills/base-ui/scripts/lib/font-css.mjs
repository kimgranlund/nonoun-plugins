import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const root=new URL('../../assets/fonts/',import.meta.url);
// Local, pinned binaries only. No network or system-font dependency during generation.
export function bundledFontCSS(){
 const manifest=JSON.parse(fs.readFileSync(new URL('manifest.json',root),'utf8'));
 const read=record=>{
  const base=fs.realpathSync(root),file=fs.realpathSync(new URL(record.file,root));
  if(!file.startsWith(base+path.sep))throw Error('Font file escapes asset root');
  const bytes=fs.readFileSync(file);
  if(createHash('sha256').update(bytes).digest('hex')!==record.sha256)throw Error('Bundled font integrity mismatch: '+record.file);
  return bytes;
 };
 const licenses=manifest.licenses.map(r=>'/* '+r.file+'\n'+read(r).toString('utf8').replaceAll('*/','* /').replaceAll('<','\\3c ')+'\n*/').join('\n');
 return licenses+'\n'+manifest.faces.map(f=>`@font-face { font-family:${JSON.stringify(f.family)}; font-style:${f.style}; font-weight:${f.weight}; font-display:swap; src:url("data:font/woff2;base64,${read(f).toString('base64')}") format("woff2"); }`).join('\n');
}
