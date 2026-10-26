import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {createRequire} from 'node:module';import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
if(process.argv.includes('--help')){console.log('Usage: node scripts/check-sheet-link-switch.mjs SHEETS PLAYWRIGHT REPORT\nMeasures visible ordinary Index links during immediate and settled light/dark switches under normal/reduced motion, with old color-interpolation controls. Does not certify all interface motion or accessibility.');process.exit(0);}
const [out,pw,file]=process.argv.slice(2);if(!file)throw Error('SHEETS PLAYWRIGHT REPORT required');const engines=createRequire(import.meta.url)(pw),records=[],faults=[];
const measure=()=>{
 const rgb=s=>{const m=s.match(/^rgba?\(([^)]+)\)$/);if(!m)throw Error('Unsupported resolved color: '+s);const n=m[1].split(/[, /]+/).map(Number);if(n[3]!==undefined&&n[3]!==1)throw Error('Unexpected alpha');return n.slice(0,3);};
 const lum=s=>rgb(s).map(c=>c/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4).reduce((n,c,i)=>n+c*[.2126,.7152,.0722][i],0);
 const bg=getComputedStyle(document.body).backgroundColor;
 return [...document.querySelectorAll('a:not(.button__root)')].filter(a=>a.getBoundingClientRect().width>0&&a.getBoundingClientRect().height>0).map(a=>{const s=getComputedStyle(a),parent=getComputedStyle(a.parentElement).color,l=[lum(s.color),lum(bg)].sort((a,b)=>a-b);return {href:a.getAttribute('href'),color:s.color,parentColor:parent,background:bg,ratio:(l[1]+.05)/(l[0]+.05),inheritsImmediately:s.color===parent,transitionProperty:s.transitionProperty};});
};
const accepts=rows=>rows.length>0&&rows.every(r=>r.inheritsImmediately&&r.ratio>=4.5);
for(const name of ['chromium','firefox','webkit']){const b=await engines[name].launch();try{for(const width of [360,1399])for(const motion of ['no-preference','reduce']){const p=await b.newPage({viewport:{width,height:1000},reducedMotion:motion});await p.goto(pathToFileURL(path.resolve(out,'index.html')).href);
 for(const scheme of ['light','dark']){await p.locator('#scheme').selectOption(scheme);const immediate=await p.evaluate(measure);assert(accepts(immediate),name+' immediate '+scheme);await p.waitForTimeout(250);const settled=await p.evaluate(measure);assert(accepts(settled),name+' settled '+scheme);records.push({engine:name,width,motion,scheme,immediate,settled,outcome:'pass'});}
 if(motion==='no-preference'){
  const first=p.locator('main section a').first();const sample=await first.evaluate(e=>{
   e.style.transitionProperty='background-color,color,border-color,outline-color,box-shadow,opacity';
   const before=getComputedStyle(e).color;document.documentElement.style.colorScheme='light';
   const color=getComputedStyle(e).color,parentColor=getComputedStyle(e.parentElement).color;
   return {before,color,parentColor,background:getComputedStyle(document.body).backgroundColor};
  });assert.notEqual(sample.color,sample.parentColor,'Old interpolation must delay inherited foreground');faults.push({engine:name,width,mutation:'Restore color interpolation on an ordinary domain link',sampling:'Synchronous scheme change and computed colors; no automation delay between mutation and sample',rejected:true,sample});
 }
 await p.close();}}finally{await b.close();}}
const inv=JSON.parse(fs.readFileSync(path.join(out,'inventory.json')));fs.writeFileSync(file,JSON.stringify({sourceHash:inv.sourceHash,verifierSha256:createHash('sha256').update(fs.readFileSync(new URL(import.meta.url))).digest('hex'),indexSha256:createHash('sha256').update(fs.readFileSync(path.join(out,'index.html'))).digest('hex'),records,faults,scope:'Ordinary visible Index links against the shared opaque page/card surface during scheme switches. No all-surface/state contrast, installed Safari, AT or motion certification.'},null,2));console.log('PASS24 immediate/settled link-switch contexts and six old-interpolation controls');
