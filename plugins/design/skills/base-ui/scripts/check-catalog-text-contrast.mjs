import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const [runtime,out]=process.argv.slice(2);if(!runtime||!out)throw Error('Usage: check-catalog-text-contrast.mjs PLAYWRIGHT OUTPUT');
const root=path.resolve(import.meta.dirname,'..'),pw=createRequire(import.meta.url)(runtime),contract=JSON.parse(fs.readFileSync(path.join(root,'references/style/contract.json')));
const css=contract.styles.map(p=>fs.readFileSync(path.resolve(root,'references/style',p),'utf8')).join('\n');fs.mkdirSync(out,{recursive:true});
const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>${css}</style><body>${fs.readFileSync(path.join(root,'assets/recipes/components.html'),'utf8')}<script>${fs.readFileSync(path.join(root,'assets/recipes/components.js'),'utf8')}</script></body></html>`;fs.writeFileSync(path.join(out,'index.html'),html);
const audit=scheme=>{
 const canvas=document.createElement('canvas');canvas.width=canvas.height=1;const ctx=canvas.getContext('2d',{colorSpace:'srgb'});
 const parse=color=>{if(!CSS.supports('color',color))throw Error('Unresolved computed color: '+color);ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data].map((n,i)=>i===3?n/255:n);};
 const mix=(fg,bg)=>fg.slice(0,3).map((n,i)=>n*fg[3]+bg[i]*(1-fg[3]));
 const luminance=rgb=>rgb.map(n=>n/255).map(n=>n<=.04045?n/12.92:((n+.055)/1.055)**2.4).reduce((sum,n,i)=>sum+n*[.2126,.7152,.0722][i],0);
 const rows=[];
 const sample=(e,text,kind,pseudo=null)=>{
  if(!text.trim()||!e.getClientRects().length||getComputedStyle(e).visibility!=='visible')return;
  const base={text:text.trim().slice(0,120),kind,tag:e.tagName,id:e.id};
  if(e.closest(':disabled')||e.closest('label')?.querySelector(':disabled')||e.closest('.input-group__root')?.querySelector('input:disabled')){rows.push({...base,status:'inactive-excluded'});return;}
  const trail=[];for(let x=e;x;x=x.parentElement)trail.push(x);
  if(trail.some(x=>{const s=getComputedStyle(x);return s.backgroundImage!=='none'||parseFloat(s.opacity)!==1||s.filter!=='none'||s.mixBlendMode!=='normal';})){rows.push({...base,status:'unsupported-paint'});return;}
  // The fixture has opaque authored page surfaces. This is not a general screenshot compositor.
  let bg=Array(3).fill(scheme==='dark'?0:255);for(const x of [...trail].reverse())bg=mix(parse(getComputedStyle(x).backgroundColor),bg);
  const s=getComputedStyle(e,pseudo),color=parse(s.color);color[3]*=parseFloat(s.opacity);
  const fg=mix(color,bg),a=luminance(fg),b=luminance(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
  const threshold=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=18.6667&&parseFloat(s.fontWeight)>=700)?3:4.5;
  rows.push({...base,font:s.fontSize,weight:s.fontWeight,foreground:fg,background:bg,ratio,threshold,status:Math.abs(ratio-threshold)<.05?'quantization-boundary':ratio>=threshold?'pass':'fail'});
 };
 const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;while(node=walker.nextNode()){const e=node.parentElement;if(!e.closest('script,style,noscript'))sample(e,node.textContent,'text-node');}
 for(const e of document.querySelectorAll('input:not([type=checkbox],[type=radio],[type=range],[type=hidden]),textarea,select')){
  const value=e.tagName==='SELECT'?e.selectedOptions[0]?.textContent||'':e.value;
  if(value)sample(e,value,'control-value');else if(e.placeholder)sample(e,e.placeholder,'placeholder','::placeholder');
 }
 return rows;
};
const cases=[],faults=[];
for(const engine of ['chromium','firefox','webkit']){const b=await pw[engine].launch();try{for(const scheme of ['light','dark'])for(const size of ['sm','md','lg']){const p=await b.newPage({viewport:{width:1399,height:900},colorScheme:scheme});await p.setContent(html);await p.locator('body').evaluate((e,size)=>e.dataset.size=size,size);const samples=await p.evaluate(audit,scheme);assert(samples.filter(x=>x.status==='pass').length>=100,'Unexpectedly empty text inventory');assert(!samples.some(x=>x.status==='fail'||x.status==='quantization-boundary'),JSON.stringify({engine,scheme,size,failures:samples.filter(x=>x.status==='fail'||x.status==='quantization-boundary')}));
const mutation=await p.addStyleTag({content:'#choices-heading{color:var(--ui-surface)!important}'});const bad=(await p.evaluate(audit,scheme)).find(x=>x.id==='choices-heading');assert.equal(bad.status,'fail');assert(bad.ratio<1.1);await mutation.evaluate(e=>e.remove());assert(!((await p.evaluate(audit,scheme)).some(x=>x.status==='fail')));cases.push({engine,version:b.version(),scheme,size,samples});faults.push({engine,scheme,size,lowContrastDetected:true,ratio:bad.ratio});await p.close();}}finally{await b.close();}}
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify({cases,faults,method:'Computed colors rendered to 8-bit sRGB canvas; opaque/alpha ancestor backgrounds composited; WCAG relative luminance and unrounded 4.5/3 thresholds. Within .05 of the threshold is inconclusive. Inactive controls excluded; unsupported group paint explicitly listed.',scope:'Initial authored component catalog at 1399px, two schemes/three sizes/three engines, text nodes/control values/placeholders. Not non-text contrast, all interactive states, every generated interface, installed Safari, native zoom or accessibility certification.',source:'https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html'},null,2));console.log(`PASS ${cases.length} catalog text-contrast contexts and ${faults.length} low-contrast controls; inspect unsupported paint inventory separately`);
