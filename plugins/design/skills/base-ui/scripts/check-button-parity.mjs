import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
import {resolve} from '../../mathematical-design-system/scripts/lib/scale.mjs';
const [runtime,executablePath,out]=process.argv.slice(2);
if(!out)throw Error('Usage: check-button-parity.mjs PLAYWRIGHT CHROME OUTPUT');
fs.mkdirSync(out,{recursive:true});
const pw=createRequire(import.meta.url)(runtime),browser=await pw.chromium.launch({executablePath});
const mathCSS=['tokens.css','button.css'].map(f=>fs.readFileSync(new URL('../../mathematical-design-system/scripts/lib/'+f,import.meta.url),'utf8')).join('\n');
const icon='<span data-slot="icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3v18M3 12h18" stroke="currentColor"/></svg></span>';
const label='<span data-slot="label">Save</span>';
const glyph=icon.replace('data-slot="icon"','data-slot="glyph"');
const variants={plain:'Save',label,leading:icon+label,trailing:label+icon,both:icon+label+icon,icon,glyph:glyph+label,mixed:icon+glyph+label+glyph+icon,assetGlyph:'<span data-slot="glyph" aria-hidden="true"><span data-slot="mark" class="ph-icon"></span></span>'+label,text:label.replace('data-slot="label"','data-slot="text"')};
const measure=e=>{
 const s=getComputedStyle(e),r=e.getBoundingClientRect(),icons=[...e.querySelectorAll('[data-slot=icon]')].map(i=>{const b=i.getBoundingClientRect();return {x:b.x-r.x,y:b.y-r.y,w:b.width,h:b.height};});
 const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let node,text=null;
 while(node=walker.nextNode()){if(!node.textContent.trim())continue;const q=document.createRange();q.selectNodeContents(node);const b=q.getBoundingClientRect();text={x:b.x-r.x,y:b.y-r.y,w:b.width,h:b.height};break;}
 return {width:r.width,height:r.height,font:s.fontSize,weight:s.fontWeight,line:s.lineHeight,radius:s.borderTopLeftRadius,shape:s.cornerShape,padding:[s.paddingTop,s.paddingRight,s.paddingBottom,s.paddingLeft],gap:s.columnGap,icons,text};
};
const cases=[];
try{
 const pages=await Promise.all([browser.newPage(),browser.newPage()]);
 for(const [i,css]of [mathCSS,getAssetBundle().css].entries()){
  const cls=i?'button__root':'mds-button';
  await pages[i].setContent(`<!doctype html><style>${css}\nbody{margin:0}button{font-family:Arial,sans-serif}#buttons{display:flex;align-items:start;gap:16px;padding:24px}</style><div id="context"><div id="buttons">${Object.entries(variants).map(([key,value])=>`<button type="button" class="${cls}" id="${key}" ${key==='icon'?'data-icon-only aria-label="Add"':''}>${value}</button>`).join('')}</div></div>`);
  await pages[i].evaluate(()=>document.fonts.ready);
 }
 for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg'])for(const dir of ['ltr','rtl']){
  const v=resolve(tier,scale,size);
  for(const p of pages)await p.locator('#context').evaluate((e,x)=>{Object.assign(e.dataset,x);e.dir=x.dir;},{tier,scale,size,dir});
  for(const key of Object.keys(variants)){
   const [a,b]=await Promise.all(pages.map(p=>p.locator('#'+key).evaluate(measure)));
   assert.deepEqual(b,a,`${tier}/${scale}/${size}/${dir}/${key}`);
   assert(Math.abs(a.height-v.h)<.1,JSON.stringify({tier,scale,size,key,a}));
   assert.equal(a.shape,'superellipse(1.5)');assert.equal(parseFloat(a.font),v.type.control);assert.equal(parseFloat(a.radius),v.n*1.5);assert.equal(parseFloat(a.gap),['plain','icon'].includes(key)?v.n:0);
   if(key==='plain'||key==='label'||key==='text'){assert(Math.abs(a.text.x-2*v.n)<.1);}
   if(!['plain','icon'].includes(key)){const slot=await pages[1].locator('#'+key+' > :is([data-slot=label],[data-slot=text])').evaluate(e=>{const s=getComputedStyle(e);return {height:e.getBoundingClientRect().height,padding:parseFloat(s.paddingInlineStart)}});assert(slot.height>=v.icon);assert.equal(slot.padding,v.n);}
   if(key==='glyph'||key==='assetGlyph'){const g=await pages[1].locator('#'+key+' > [data-slot=glyph]').evaluate(e=>{const a=e.getBoundingClientRect(),b=e.firstElementChild.getBoundingClientRect();return {slot:a.width,mark:b.width,offset:b.x-a.x}});assert.equal(g.slot,v.icon);assert.equal(g.mark,v.glyph);assert.equal(g.offset,v.c);}
   if(key==='icon'){assert.equal(a.width,v.h);assert.equal(a.icons[0].w,2*v.n);assert.equal(a.icons[0].x,v.n);}
   if(a.text){const border=1;assert(a.text.y>=border-.1);assert(a.text.y+a.text.h<=a.height-border+.1,`Text overflows ${tier}/${scale}/${size}/${key}`);}
   cases.push({tier,scale,size,dir,variant:key,height:a.height,radius:a.radius});
  }
 }
 // Compact chips share half-n outer margins; text slots own half-n separation.
 for(const p of pages)await p.locator('#buttons').evaluate(e=>{for(const id of ['plain','leading','trailing'])e.querySelector('#'+id).setAttribute('data-chip','');});
 let chipCases=0;
 for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg'])for(const dir of ['ltr','rtl']){
  const v=resolve(tier,scale,size);
  for(const p of pages)await p.locator('#context').evaluate((e,x)=>{Object.assign(e.dataset,x);e.dir=x.dir;},{tier,scale,size,dir});
  for(const key of ['plain','leading','trailing']){
   const [a,b]=await Promise.all(pages.map(p=>p.locator('#'+key).evaluate(measure)));
   assert.deepEqual(a,b,`Chip parity ${tier}/${scale}/${size}/${dir}/${key}`);
   assert(Math.abs(a.height-Math.max(3*v.n,Math.max(v.icon,1.2*v.type.fieldLabel)+2))<.1,'Chip nominal frame or text-driven growth');
   assert(Math.abs(parseFloat(a.padding[1])+1-(key==='plain'?1:.5)*v.n)<.01,'Chip inline margin');
   assert(Math.abs(parseFloat(a.padding[3])+1-(key==='plain'?1:.5)*v.n)<.01,'Chip opposite margin');
   if(a.icons.length){const icon=a.icons[0];assert(Math.abs(Math.min(icon.x,a.width-icon.x-icon.w)-v.n/2)<.1,'Chip media edge');}
   if(key!=='plain')assert.equal(await pages[1].locator('#'+key+' > [data-slot=label]').evaluate(e=>parseFloat(getComputedStyle(e).paddingInlineStart)),v.n/2,'Chip text gutter');
   chipCases++;
  }
 }
 // Retired presentation knobs must not restore the old radius model.
 for(const radius of ['default','round','sharp','pill']){
  await pages[1].locator('#context').evaluate((e,r)=>e.dataset.radius=r,radius);
  assert.deepEqual(await pages[1].locator('#label').evaluate(measure),await pages[0].locator('#label').evaluate(measure));
 }
 // Shared wrapping behavior, including doubled text, must remain equal and readable.
 for(const p of pages)await p.locator('#label').evaluate(e=>{e.querySelector('[data-slot=label]').textContent='Save the updated configuration';e.style.maxInlineSize='180px';e.style.fontSize='44px';});
 assert.deepEqual(await pages[1].locator('#label').evaluate(measure),await pages[0].locator('#label').evaluate(measure));
 for(const p of pages){const v=await p.locator('#label').evaluate(measure);assert(v.text.y>=1-.1);assert(v.text.y+v.text.h<=v.height-1+.1,'Enlarged wrapped text exceeds border box');}
 // Prove the comparison detects the previous radius mismatch.
 await pages[1].locator('#label').evaluate(e=>e.style.borderRadius='99px');
 assert.notDeepEqual(await pages[1].locator('#label').evaluate(measure),await pages[0].locator('#label').evaluate(measure));
 const report={status:'pass',engine:browser.version(),cases,negativeControl:'radius divergence detected',chipCases,scope:'720 paired cases: 36 contexts × 2 directions × 10 button anatomies; retired presets and enlarged wrapping text',limits:['Same font in both comparisons; fonts and colors are presentation choices','Chromium only']};
 fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(report,null,2)+'\n');
 console.log('PASS '+report.scope);
}finally{await browser.close();}
