#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const [runtime,out]=process.argv.slice(2);
if(!runtime||!out)throw Error('Usage: check-popup-instances.mjs PLAYWRIGHT NEW_OUTPUT');
assert(!fs.existsSync(out),'Preserve prior evidence');fs.mkdirSync(out,{recursive:true});
const root=path.resolve(import.meta.dirname,'..'),pw=createRequire(import.meta.url)(runtime);
const contract=JSON.parse(fs.readFileSync(path.join(root,'references/style/contract.json')));
const css=contract.styles.map(p=>fs.readFileSync(path.resolve(root,'references/style',p),'utf8')).join('\n');
const panel=n=>`<section id="panel-${n}" class="popover__root" popover="auto" aria-labelledby="title-${n}" style="position-anchor:--trigger-${n};inline-size:28rem;min-inline-size:0"><header class="popover__header"><h2 id="title-${n}">Source ${n}: a long contextual title that must remain readable</h2><button type="button" popovertarget="panel-${n}" popovertargetaction="hide">Close source ${n}</button></header><div class="popover__body flow__root"><details><summary>Implementation ${n}</summary><div class="disclosure__body flow__root">${'<p>Long source documentation remains inside this scrolling content region.</p>'.repeat(24)}<label class="field__root">Review note ${n}<input name="note-${n}"></label></div></details></div></section>`;
const fixture=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Clipped collection hosts and independent source popovers</title><style>${css}body{padding:var(--g-margin)}.clip-outer{overflow:hidden;max-inline-size:32rem}.clip-inner{overflow:auto;max-block-size:calc(4 * var(--g-height));padding:var(--g-margin)}.sentinel{margin-block-start:var(--g-margin)}</style><body class="product__root"><section class="card__root clip-outer"><div class="clip-inner"><div class="cluster__root"><button id="trigger-1" type="button" popovertarget="panel-1" style="anchor-name:--trigger-1">Source one</button><button id="trigger-2" type="button" popovertarget="panel-2" style="anchor-name:--trigger-2">Source two</button></div>${panel(1)}${panel(2)}</div></section><p class="sentinel">Following content stays in place.</p></body></html>`;
fs.writeFileSync(path.join(out,'index.html'),fixture);
const cases=[],faults=[];
const measure=async(page,n)=>page.locator('#panel-'+n).evaluate(e=>{
 const r=e.getBoundingClientRect(),h=e.querySelector('header').getBoundingClientRect(),close=e.querySelector('header button').getBoundingClientRect(),body=e.querySelector('.popover__body'),br=body.getBoundingClientRect(),ancestor=e.parentElement.getBoundingClientRect();
 return {rect:r.toJSON(),contained:r.left>=-1&&r.top>=-1&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1,headerContained:h.left>=r.left&&h.right<=r.right&&h.top>=r.top&&h.bottom<=r.bottom,closeReachable:close.top>=r.top&&close.bottom<=r.bottom&&close.left>=r.left&&close.right<=r.right,bodyHeight:br.height,bodyScrollable:body.scrollHeight>body.clientHeight,escapesClip:r.left<ancestor.left||r.right>ancestor.right||r.top<ancestor.top||r.bottom>ancestor.bottom,documentFits:document.documentElement.scrollWidth<=innerWidth+1};
});
const valid=x=>x.contained&&x.headerContained&&x.closeReachable&&x.bodyHeight>0&&x.bodyScrollable&&x.escapesClip;
for(const engine of ['chromium','firefox','webkit']){
 console.log('Checking '+engine+' clipped hosts');const browser=await pw[engine].launch();
 try{
  for(const width of [390,1399])for(const scheme of ['light','dark'])for(const size of ['sm','md','lg'])for(const dir of ['ltr','rtl']){
   const page=await browser.newPage({javaScriptEnabled:false,viewport:{width,height:600}});page.setDefaultTimeout(5000);
   await page.setContent(fixture);await page.evaluate(x=>{document.documentElement.dir=x.dir;document.documentElement.style.colorScheme=x.scheme;document.body.dataset.size=x.size;},{size,scheme,dir});
   const sentinel=()=>page.locator('.sentinel').evaluate(e=>e.getBoundingClientRect().top+scrollY),before=await sentinel();
   const first=page.locator('#trigger-1');await first.focus();await page.keyboard.press('Enter');
   const one=page.locator('#panel-1');assert(await one.evaluate(e=>e.matches(':popover-open')));
   await one.locator('summary').click();assert(valid(await measure(page,1)),JSON.stringify({engine,width,scheme,size,dir,one:await measure(page,1)}));
   const note=one.locator('input');await note.focus();await note.fill('Retained local source note');
   const noteBox=await note.boundingBox(),headerBox=await one.locator('header').boundingBox();assert(noteBox.y>=headerBox.y+headerBox.height-1,'Focused field must not hide beneath header');
   await page.keyboard.press('Escape');await one.waitFor({state:'hidden'});assert(await first.evaluate(e=>e===document.activeElement));
   await page.keyboard.press('Enter');assert(valid(await measure(page,1)));assert.equal(await note.inputValue(),'Retained local source note');
   await one.locator('header button').click();await one.waitFor({state:'hidden'});
   const second=page.locator('#trigger-2');await second.focus();await page.keyboard.press('Enter');
   const two=page.locator('#panel-2');assert(await two.evaluate(e=>e.matches(':popover-open')));assert(!(await two.locator('details').evaluate(e=>e.open)),'Instances must retain independent disclosure state');await two.locator('summary').click();
   const good=await measure(page,2);assert(valid(good),JSON.stringify({engine,width,scheme,size,dir,good}));assert(Math.abs(await sentinel()-before)<1,'Top-layer state must not reflow its clipping host');
   // Prove document overflow alone cannot certify top-layer containment.
   const originalStyle=await two.getAttribute('style');await two.evaluate(e=>{e.style.setProperty('inline-size','calc(100vw + 200px)','important');e.style.setProperty('max-inline-size','none','important')});
   const bad=await measure(page,2);assert(!bad.contained,'Oversized overlay must fail actual bounds');assert(bad.documentFits,'Control demonstrates a layout-overflow false negative');await two.evaluate((e,value)=>e.setAttribute('style',value),originalStyle);assert(valid(await measure(page,2)));
   await two.locator('header button').click();await two.waitFor({state:'hidden'});assert(Math.abs(await sentinel()-before)<1);
   // Opening a second auto popover dismisses its sibling, without cross-instance data changes.
   await first.focus();await page.keyboard.press('Enter');await second.focus();await page.keyboard.press('Enter');assert(!(await one.evaluate(e=>e.matches(':popover-open'))));assert(await two.evaluate(e=>e.matches(':popover-open')));await page.keyboard.press('Escape');assert(await second.evaluate(e=>e===document.activeElement));
   cases.push({engine,version:browser.version(),width,scheme,size,dir,...good,independentState:true,focusedFieldVisible:true,noReflow:true,siblingDismissal:true,keyboardRestoration:true});faults.push({engine,width,scheme,size,dir,overlayBoundsRejected:true,documentOverflowMissed:true,restored:true});fs.writeFileSync(path.join(out,'progress.json'),JSON.stringify({completed:cases.length,cases,faults},null,2));await page.close();
  }
 }finally{await browser.close()}
}
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify({cases,faults,scope:'Authored two-instance native popovers inside overflow-hidden/scrolling ancestors at 600px height, both widths/schemes/densities/directions and three Playwright engines. Actual overlay bounds, focused content, no reflow and per-instance state. Not installed Safari, AT or generative efficacy.'},null,2));
console.log(`PASS ${cases.length} clipped-host/multiple-instance cases and ${faults.length} overlay-vs-document negative controls`);
