#!/usr/bin/env node
// Optional browser check: suite output directory, then installed Playwright path.
import assert from 'node:assert/strict';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {patternRegistry} from '../assets/demos/marketing-patterns.mjs';
import {scenarios} from '../assets/demos/scenarios.mjs';
import {validateManifest,validateReview,resolveParts,newReview} from '../assets/model.mjs';
const require=createRequire(import.meta.url),{chromium}=require(process.argv[3]||'playwright');
const out=resolve(process.argv[2]);const root=new URL('../',import.meta.url);const ms=JSON.parse(readFileSync(new URL('references/manifest.schema.json',root))),fs=JSON.parse(readFileSync(new URL('references/feedback.schema.json',root)));
const patternIds=new Set(patternRegistry.patterns.map(p=>p.id));assert.equal(patternIds.size,patternRegistry.patterns.length);
for(const p of patternRegistry.patterns){assert(p.intent&&p.contentShape&&p.selectWhen&&p.avoidWhen&&p.requiredContent.length&&p.tradeoff&&p.evaluation);for(const alt of p.alternatives)assert(patternIds.has(alt),`Unknown alternative ${alt}`);}
const browser=await chromium.launch();let rendered=0;
try{
 for(const scenario of scenarios.filter(s=>!process.argv[4]||process.argv[4].split(',').includes(s.id))){
  const manifest=JSON.parse(readFileSync(join(out,`${scenario.id}.manifest.json`),'utf8'));validateManifest(manifest,ms);validateReview(newReview(manifest),fs,manifest);
  const pages=manifest.units.filter(u=>u.kind==='page');assert.equal(pages.length,scenario.pages.length);
  for(const unit of manifest.units)for(const variant of unit.variants){
   for(const match of variant.html.matchAll(/data-page-id="([^"]+)"/g))assert(pages.some(p=>p.id===match[1]),`${scenario.id}: missing destination ${match[1]}`);
   if(unit.kind==='page')for(const part of resolveParts(manifest,newReview(manifest),unit.id,variant.id,false))assert(manifest.units.some(u=>u.id===part.unitId));
  }
  const page=await browser.newPage({viewport:{width:1500,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(join(out,`${scenario.id}.html`)).href);
  assert.equal(await page.locator('.page-map').count(),pages.length);assert.equal(await page.locator('.home-proposal').count(),pages.length*3);
  for(const unit of pages){
   await page.locator('#page').selectOption(unit.id);await page.locator('#view').selectOption('compare');
   for(const viewport of ['desktop','mobile']){
    await page.locator('#viewport').selectOption(viewport);await page.waitForFunction(()=>[...document.querySelectorAll('#canvas iframe')].every(f=>f.dataset.ready==='true'));
    for(const iframe of await page.locator('#canvas iframe').all()){
     const frame=await (await iframe.elementHandle()).contentFrame();
     const dimensions=await frame.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,heading:document.querySelector('h1')?.textContent,controls:[...document.querySelectorAll('button,input,select,textarea')].filter(e=>e.getBoundingClientRect().width>innerWidth).length}));
     assert(dimensions.heading,`${scenario.id}/${unit.id}: missing heading`);assert(dimensions.scroll<=dimensions.width+1,`${scenario.id}/${unit.id}/${viewport}: overflow ${dimensions.scroll}/${dimensions.width}`);assert.equal(dimensions.controls,0);
     const navigation=await frame.evaluate(()=>{
      const nav=document.querySelector('.nav-container,.mh-inner,.product-sidebar'),section=document.querySelector('.section__root');
      if(!nav)return null;
      const labels=[...nav.querySelectorAll('[data-page-id]')].filter(a=>!a.classList.contains('nav-brand')&&!a.classList.contains('mh-brand')).map(a=>a.textContent.trim());
      if(nav.classList.contains('product-sidebar'))return {labels};
      const n=nav.getBoundingClientRect(),r=section.getBoundingClientRect(),style=getComputedStyle(section);
      return {labels,left:Math.abs(n.left-r.left-parseFloat(style.paddingLeft)),right:Math.abs(n.right-r.right+parseFloat(style.paddingRight))};
     });
     if(navigation){assert(navigation.labels.every(label=>label.split(/\s+/).length<=3),`${scenario.id}: long navigation label`);if(navigation.left!==undefined)assert(navigation.left<2&&navigation.right<2,`${scenario.id}: navigation/content edges differ`);}
     const account=await frame.evaluate(()=>{
      const menu=document.querySelector('.nav-account');if(!menu)return null;
      const header=menu.closest('nav'),trigger=menu.querySelector('summary'),panel=menu.querySelector('.nav-account-panel');
      const wasOpen=menu.open;menu.open=false;const before=header.getBoundingClientRect().height;
      menu.open=true;const after=header.getBoundingClientRect().height;
      const gap=panel.getBoundingClientRect().top-trigger.getBoundingClientRect().bottom;
      const expected=parseFloat(getComputedStyle(trigger).paddingTop)/2;menu.open=wasOpen;
      return {before,after,gap,expected};
     });
     if(account){assert.equal(account.before,account.after,'Account dropdown changes header height');assert(Math.abs(account.gap-account.expected)<0.1,'Account dropdown must use half an inset gap');}
     const widths=await frame.evaluate(()=>[...document.querySelectorAll('[data-unit-id] > .section__root,.spec-reading,.agent-briefing-body')].map(e=>{const p=e.parentElement,ps=getComputedStyle(p);return {tag:e.className,actual:e.getBoundingClientRect().width,expected:p.clientWidth-parseFloat(ps.paddingLeft)-parseFloat(ps.paddingRight)};}));
     for(const w of widths)assert(Math.abs(w.actual-w.expected)<2,`${scenario.id}/${unit.id}/${viewport}: narrowed content ${w.tag} ${w.actual}/${w.expected}`);
     if(scenario.id==='marketing'&&unit.id==='home'){const patterns=await frame.locator('[data-pattern]').evaluateAll(nodes=>nodes.map(n=>n.dataset.pattern));assert(new Set(patterns).size>=6,'Homepage regressed to repeated module silhouettes');}
     rendered++;
    }
   }
  }
  if(scenario.agentic){
   await page.locator('#page').selectOption('plan');await page.locator('#view').selectOption('inspect');await page.waitForFunction(()=>document.querySelector('#canvas iframe')?.dataset.ready==='true');
   let af=await (await page.locator('#canvas iframe').elementHandle()).contentFrame();assert(await af.locator('[data-review-id=approve-disabled]').isDisabled());assert.match(await af.locator('[data-review-id=approval-validity]').innerText(),/plan|Approval/);
   if(scenario.id==='switchyard'){assert.equal(await af.locator('.agent-diff del').innerText(),'$180');assert.equal(await af.locator('.agent-diff ins').innerText(),'$216');}
   await page.locator('#page').selectOption('evidence');await page.waitForFunction(()=>document.querySelector('#canvas iframe')?.dataset.ready==='true');af=await (await page.locator('#canvas iframe').elementHandle()).contentFrame();
   const sources=await af.evaluate(()=>[...document.querySelectorAll('.agent-citation[href^="#source-"]')].map(a=>({exists:!!document.getElementById(a.hash.slice(1)),text:a.textContent})));assert.equal(sources.length,3);const signal=await af.locator('[data-review-id=typed-result]').innerText();if(scenario.id==='observatory'){assert.equal(signal,'Targeted field research');assert.equal(await af.locator('[data-review-id=typed-confidence]').innerText(),'Confidence 0.28');}if(scenario.id==='switchyard'){assert.match(signal,/0.94/);assert.equal(await af.locator('[data-review-id=typed-confidence]').count(),0);}if(scenario.id==='atelier'){assert.match(signal,/1.65/);assert.equal(await af.locator('[data-review-id=typed-confidence]').innerText(),'Confidence 0.48');}assert(sources.every(s=>s.exists));await af.locator('.agent-citation[href="#source-s1"]').first().click();assert.equal(await af.evaluate(()=>document.activeElement.id),'source-s1');
   await page.locator('#page').selectOption('options');await page.waitForFunction(()=>document.querySelector('#canvas iframe')?.dataset.ready==='true');af=await (await page.locator('#canvas iframe').elementHandle()).contentFrame();await af.locator('input[name=mission-option]').first().check();assert.equal(await af.locator('input[name=mission-option]:checked').count(),1);
   await page.locator('#page').selectOption('brief');await page.waitForFunction(()=>document.querySelector('#canvas iframe')?.dataset.ready==='true');af=await (await page.locator('#canvas iframe').elementHandle()).contentFrame();await af.getByLabel('Desired outcome',{exact:true}).fill('Prototype-only input is not review feedback');
   console.log(`PASS ${scenario.id}: inspectable citations, bounded disabled approval, mission options and editable direction specimen`);
  }
  // Verify real in-preview navigation in contextual mode and choice-free feedback.
  await page.locator('#page').selectOption(pages[0].id);await page.locator('#view').selectOption('inspect');await page.locator('#viewport').selectOption('desktop');await page.waitForFunction(()=>document.querySelector('#canvas iframe')?.dataset.ready==='true');
  let frame=await (await page.locator('#canvas iframe').elementHandle()).contentFrame();const next=frame.locator('[data-review-id=next-action]').first(),target=await next.getAttribute('data-page-id');await next.click();assert.equal(await page.locator('#page').inputValue(),target);
  await page.locator('#missing-approach').click();await page.locator('#comment-text').fill(`Synthetic ${scenario.id} review: clarify what happens when the intended outcome cannot be reached.`);await page.getByRole('button',{name:'Save feedback',exact:true}).click();
  await page.locator('#open-feedback').click();const pending=page.waitForEvent('download');await page.locator('#download').click();const download=await pending;const review=JSON.parse(readFileSync(await download.path(),'utf8'));validateReview(review,fs,manifest);assert(!JSON.stringify(review).includes('Prototype-only input is not review feedback'));assert.equal(review.comments.at(-1).target.scope,'decision');assert(Object.values(review.choices).every(c=>c.selectedVariant===null));
  for(const width of [390,1500]){await page.setViewportSize({width,height:1000});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));}
  await page.locator('#page').selectOption(pages[0].id);await page.waitForFunction(()=>document.querySelector('#canvas iframe')?.dataset.ready==='true');
  mkdirSync(join(out,'screenshots'),{recursive:true});await page.screenshot({path:join(out,'screenshots',`${scenario.id}.png`)});
  assert.deepEqual(errors,[]);console.log(`PASS ${scenario.id}: ${pages.length} surfaces, all A/B/C at desktop/mobile, links, export and 390px shell`);await page.close();
 }
 console.log(`PASS ${rendered} rendered page proposals across two viewport sizes`);
}finally{await browser.close();}
