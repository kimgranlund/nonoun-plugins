// Bind local stylesheets, scripts and static ES module dependencies without executing them.
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
function moduleReferences(source){
 const parser="const fs=require('node:fs'),vm=require('node:vm');const m=new vm.SourceTextModule(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(m.dependencySpecifiers));";
 const result=spawnSync(process.execPath,['--no-warnings','--experimental-vm-modules','-e',parser],{input:source,encoding:'utf8',maxBuffer:1024*1024});
 if(result.status!==0)throw Error('Cannot bind module dependencies: '+(result.error?.message||result.stderr));
 return JSON.parse(result.stdout);
}
function attributes(text){
 const values={};
 for(const m of text.matchAll(/([^\s=/>]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/g))values[m[1].toLowerCase()]=m[2]??m[3]??m[4];
 return values;
}
export function localAssets(artifact){
 const base=path.dirname(path.resolve(artifact)),seen=new Set(),modules=new Set(),assets=[];
 function visit(file,module=false){
  const text=fs.readFileSync(file,'utf8'),refs=[];
  function addModules(source){for(const ref of moduleReferences(source)){if(!/^(?:\.{1,2}\/|\/|[a-z]+:)/i.test(ref))throw Error('Review binding does not resolve bare module imports/import maps: '+ref);refs.push({ref,module:true});}}
  if(module){if(modules.has(file))return;modules.add(file);addModules(text);}
  if(file.endsWith('.html')){
   for(const m of text.matchAll(/<(link|script)\b([^>]*)>/gi)){
    const attr=attributes(m[2]),ref=attr.src??attr.href;
    if(m[1].toLowerCase()==='script'&&attr.type?.toLowerCase()==='importmap')throw Error('Review binding does not resolve import maps');
    if(ref&&(/\.css(?:[?#]|$)/i.test(ref)||m[1].toLowerCase()==='script'))refs.push({ref,module:m[1].toLowerCase()==='script'&&attr.type?.toLowerCase()==='module'});
   }
   for(const m of text.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)){const attr=attributes(m[1]);if(attr.type?.toLowerCase()==='module'&&!attr.src)addModules(m[2]);}
  }
  if(file.endsWith('.css'))for(const m of text.matchAll(/(?:@import\s+(?:url\()?|url\()\s*["']?([^"'\s)]+)["']?\s*\)?/g))refs.push({ref:m[1],module:false});
  for(const {ref,module:isModule} of refs){
   if(/^(?:[a-z]+:|\/\/|#)/i.test(ref))continue;
   const target=path.resolve(path.dirname(file),decodeURIComponent(ref.split(/[?#]/)[0]));
   if(!target.startsWith(base+path.sep))throw Error('Local asset must be inside the page directory: '+ref);
   if(!seen.has(target)){seen.add(target);const bytes=fs.readFileSync(target);assets.push({file:path.relative(base,target),sha256:createHash('sha256').update(bytes).digest('hex')});if(/\.(css|html)$/.test(target))visit(target);}
   if(isModule)visit(target,true);
  }
 }
 visit(path.resolve(artifact));return assets.sort((a,b)=>a.file.localeCompare(b.file));
}
