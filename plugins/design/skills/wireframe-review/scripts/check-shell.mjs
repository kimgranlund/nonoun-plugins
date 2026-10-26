#!/usr/bin/env node
// Optional rendered acceptance test. Supply an installed Playwright package path.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {newReview,selectVariant} from '../assets/model.mjs';
const require=createRequire(import.meta.url),{chromium}=require(process.argv[2]||'playwright');
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),tmp=mkdtempSync(join(tmpdir(),'wireframe-shell-'));
const manifest=JSON.parse(readFileSync(join(root,'assets/example.manifest.json'),'utf8'));
while(manifest.units.length<30){const unit=structuredClone(manifest.units.find(u=>u.id==='hero'));unit.id=`extra-${manifest.units.length}`;unit.title=`Decision ${manifest.units.length}: a deliberately long title that still needs a readable action`;manifest.units.push(unit);}
const review=newReview(manifest);selectVariant(review,'home','B');selectVariant(review,'hero','C');review.pageOverrides.home={hero:'A'};
for(let i=0;i<100;i++)review.comments.push({id:`fixture-${i}`,revision:manifest.revision,target:{scope:'element',pageId:'home',unitId:'hero',variantId:'A',elementId:'headline',viewport:'mobile',position:{x:.5,y:.5}},quote:'A clearer path to begin',category:'layout',priority:i%2?'suggestion':'must-change',text:i===0?'A long feedback paragraph. '.repeat(100):`Feedback item ${i+1}`,status:i%3?'open':'resolved',createdAt:new Date().toISOString(),updatedAt:new Date().toISOString(),response:null,migration:null});
writeFileSync(join(tmp,'manifest.json'),JSON.stringify(manifest));writeFileSync(join(tmp,'review.json'),JSON.stringify(review));
execFileSync(process.execPath,[join(root,'scripts/build.mjs'),join(tmp,'manifest.json'),join(tmp,'demo.html'),join(tmp,'review.json')]);
const browser=await chromium.launch();
try{
 const page=await browser.newPage({viewport:{width:1500,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(join(tmp,'demo.html')).href);
 const frame=await (await page.locator('iframe').first().elementHandle()).contentFrame();await frame.waitForSelector('button');
 const surface=()=>page.evaluate(()=>getComputedStyle(document.body).backgroundColor);
 await page.emulateMedia({colorScheme:'light'});const light=await surface();
 await page.locator('#color-scheme').click();await page.locator('#color-scheme').click();const dark=await surface();assert.notEqual(light,dark);
 assert.equal(await frame.evaluate(()=>getComputedStyle(document.documentElement).colorScheme),'dark');
 await page.locator('#page').selectOption('home');assert.equal(await page.locator('iframe').first().evaluate(e=>e.contentDocument.documentElement.style.colorScheme),'dark');
 await page.reload();await page.waitForFunction(()=>document.documentElement.style.colorScheme==='dark');assert.match(await page.locator('#color-scheme').getAttribute('aria-label'),/Dark/);
 await page.locator('#color-scheme').click();await page.emulateMedia({colorScheme:'dark'});assert.equal(await surface(),dark);
 await page.emulateMedia({colorScheme:'light'});assert.equal(await surface(),light);
 console.log('PASS scheme toggle, iframe inheritance, new frames, reload persistence and System preference.');
 const freshFrame=await (await page.locator('iframe').first().elementHandle()).contentFrame();await freshFrame.waitForSelector('button');
 const artifactChecks=await freshFrame.evaluate(()=>{
   const errors=[],button=document.querySelector('button'),style=getComputedStyle(button),label=getComputedStyle(button.querySelector('[data-slot=label]'));
   for(const [actual,expected] of [[style.height,'32px'],[style.paddingLeft,'8px'],[style.fontSize,'14px'],[style.columnGap,'4px'],[style.borderRadius,'21px'],[label.paddingLeft,'4px']])if(actual!==expected)errors.push([actual,expected]);
   const outer=document.createElement('div');outer.dataset.tier='product';outer.dataset.scale='lg';const inner=document.createElement('div');inner.dataset.size='sm';inner.dataset.radius='sharp';inner.innerHTML='<button><span data-slot="icon"><svg></svg></span><span data-slot="label">Nested</span><span data-slot="indicator"><svg></svg></span></button>';outer.append(inner);document.body.append(outer);
   const b=inner.firstChild,s=getComputedStyle(b),icon=getComputedStyle(b.querySelector('[data-slot=icon] svg')),glyph=getComputedStyle(b.querySelector('[data-slot=indicator] svg'));
   for(const [actual,expected] of [[s.height,'28px'],[s.paddingLeft,'7px'],[s.fontSize,'13px'],[s.borderRadius,'4.875px'],[icon.width,'14px'],[glyph.width,'13px']])if(actual!==expected)errors.push([actual,expected]);
   b.focus();if(getComputedStyle(b).borderLeftColor!=='rgba(0, 0, 0, 0)')errors.push('focus border');
   const card=document.createElement('div');card.className='card__root';document.body.append(card);const cs=getComputedStyle(card);if(cs.paddingLeft!=='32px'||cs.borderRadius!=='27px')errors.push('card geometry');
   document.documentElement.style.setProperty('--ui-action','rgb(1, 2, 3)');if(getComputedStyle(button).backgroundColor!=='rgb(1, 2, 3)')errors.push('theme override');document.documentElement.style.removeProperty('--ui-action');outer.remove();card.remove();return errors;
 });assert.deepEqual(artifactChecks,[]);console.log('PASS iframe control defaults, independent nested axes, icon/glyph sizes, focus border, card geometry, and theme override.');
 assert.equal(await page.locator('.page-map').count(),2);assert.equal(await page.locator('#review-panel').getAttribute('data-scope'),'global');
 await page.locator('#summary').fill('Global feedback survives navigation');
 await page.getByRole('combobox',{name:'Review section on Home proposal A',exact:true}).selectOption({label:'Hero'});assert.equal(await page.locator('#unit').inputValue(),'hero');assert.equal(await page.locator('#review-panel').getAttribute('data-scope'),'context');
 await page.locator('#page').selectOption('');assert.equal(await page.locator('#summary').inputValue(),'Global feedback survives navigation');
 await page.locator('.page-map .page-title').first().click();
 console.log('PASS home page canvas, global scope, section navigation, return home, preserved feedback.');
 await page.locator('#open-decisions').click();assert.equal(await page.locator('[data-panel-section=overview]').isVisible(),true);assert.equal(await page.locator('#decision-search').evaluate(e=>e===document.activeElement),true);
 await page.locator('#decision-search').fill('Hero');assert.equal(await page.locator('[data-panel-section=overview] .decision-row').count(),1);
 await page.locator('[data-panel-section=overview] .text-action').click();assert.equal(await page.locator('[data-panel-section=overview]').isVisible(),false);assert.equal(await page.locator('#unit').inputValue(),'hero');
 await page.locator('#open-decisions').click();await page.locator('#decision-search').fill('');await page.locator('[data-panel-tab=current]').click();await page.locator('#review-panel .decision-row').first().waitFor({state:'attached'});assert.equal(await page.locator('#review-panel .decision-row').count(),30);
 await page.locator('#page').selectOption('home');
 console.log('PASS toolbar Decisions shortcut, search focus and return to Selection.');
 assert.equal(await page.locator('.top #open-decisions').count(),1);
 await page.locator('#open-feedback').click();assert.equal(await page.locator('#feedback-dialog').isVisible(),true);assert.equal(await page.locator('#feedback-dialog .feedback-options button').count(),3);
 await page.keyboard.press('Escape');await page.locator('#feedback-dialog').waitFor({state:'hidden'});assert.equal(await page.locator('#open-feedback').evaluate(e=>e===document.activeElement),true);
 await page.locator('#page').selectOption('');await page.waitForFunction(()=>[...document.querySelectorAll('#canvas iframe')].every(f=>f.dataset.ready==='true'));
 await page.locator('#home-choose-pricing-B').scrollIntoViewIfNeeded();const beforeChoiceY=await page.locator('.workspace > main').evaluate(e=>e.scrollTop);
 await page.locator('#home-choose-pricing-B').click();await page.waitForFunction(()=>!document.getElementById('canvas').style.minHeight);
 assert(Math.abs(await page.locator('.workspace > main').evaluate(e=>e.scrollTop)-beforeChoiceY)<2,'page scroll changed after choosing on a lower row');
 await page.locator('#page').selectOption('home');
 console.log('PASS lower-page selection preserves scroll through asynchronous frame layout.');
 const spacing=await page.evaluate(()=>{
   const failures=[];
   for(const [size,inset,height] of [['sm',5.5,24],['md',8,32],['lg',10,40]]){
     document.documentElement.dataset.size=size;
     for(const button of document.querySelectorAll('button')){
       const style=getComputedStyle(button),label=button.querySelector(':scope > [data-slot=label]');
       if(button.hasAttribute('data-icon-only')){const icon=button.querySelector('[data-slot=icon]');if(!button.getAttribute('aria-label')||!icon||style.width!==style.height||parseFloat(style.paddingLeft)!==0)failures.push('Icon-only anatomy');continue;}
       if(!label){failures.push(`Missing label slot: ${button.textContent}`);continue;}
       const labelStyle=getComputedStyle(label);
       for(const [name,actual,expected] of [['inset-start',style.paddingLeft,inset],['inset-end',style.paddingRight,inset],['gap',style.columnGap,inset/2],['label-start',labelStyle.paddingLeft,inset/2],['label-end',labelStyle.paddingRight,inset/2],['border',style.borderLeftWidth,1],['height',style.height,height]]){
         if(Math.abs(parseFloat(actual)-expected)>.01)failures.push(`${button.textContent}: ${size} ${name} ${actual} expected ${expected}`);
       }
     }
   }
   document.documentElement.dataset.size='md';return failures;
 });assert.deepEqual(spacing,[]);
 await page.keyboard.press('Tab');
 for(const selector of ['#open-feedback','#reviewer','#filter','#summary']){
   const control=page.locator(selector);
   const measure=()=>control.evaluate(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return [r.width,r.height,s.borderLeftWidth];});
   const before=await measure();await control.focus();assert.deepEqual(await measure(),before);
   assert.equal(await control.evaluate(e=>getComputedStyle(e).borderLeftColor),'rgba(0, 0, 0, 0)');
   assert.notEqual(await control.evaluate(e=>getComputedStyle(e).outlineStyle),'none');
 }
 console.log('PASS focused button/input/select/textarea borders are transparent, dimensions stable, focus rings retained.');
 await page.locator('[data-panel-tab=overview]').click();
 const quiet=page.locator('[data-unit=home] .text-action');
 const box=()=>quiet.evaluate(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return [r.width,r.height,s.paddingLeft,s.paddingRight,s.borderLeftWidth];});
 const resting=await box();await quiet.hover();assert.deepEqual(await box(),resting);
 await quiet.evaluate(e=>{e.dataset.appearance='ghost';e.disabled=true;});assert.deepEqual(await box(),resting);
 await quiet.evaluate(e=>{e.disabled=false;});
 console.log('PASS all text buttons preserve root inset, half-inset labels/gaps and border occupancy at sm/md/lg; quiet hover/disabled/ghost dimensions remain stable.');
 await page.locator('[data-panel-tab=current]').click();
 assert.equal(await page.locator('.decision-row').count(),30);assert.equal(await page.locator('.comment').count(),100);
 assert.equal(await page.locator('.variant-states button').count(),90);
 await page.locator('#unit').selectOption('hero');assert.match(await page.locator('#current-choice').innerText(),/This page/);
 await page.locator('.comment').first().getByRole('button',{name:'Locate',exact:true}).click();assert.equal(await page.locator('#preview').inputValue(),'A');assert.equal(await page.locator('#viewport').inputValue(),'mobile');
 await page.frameLocator('iframe').locator('[data-review-id=headline]').waitFor();
 await page.locator('#filter').selectOption('all');
 await page.locator('#note-scope').selectOption('unit');await page.locator('#note-variant').selectOption('B');await page.locator('#add-note').click();await page.locator('#comment-text').fill('Draft survives layout and context switches');await page.locator('#cancel-comment').click();
 await page.getByRole('button',{name:'Decisions',exact:true}).click();assert.equal(await page.locator('[data-panel-section=current]').isVisible(),false);
 await page.getByRole('button',{name:'Selection',exact:true}).click();await page.locator('#add-note').click();assert.equal(await page.locator('#comment-text').inputValue(),'Draft survives layout and context switches');await page.locator('#cancel-comment').click();
 await page.locator('[data-panel-tab=overview]').press('Enter');await page.locator('#decision-search').fill('Decision 29');assert.equal(await page.locator('.decision-row').count(),1);await page.locator('#decision-search').fill('');
 const choice=page.getByRole('button',{name:'Home proposal A: unreviewed. Choose across pages',exact:true});await choice.focus();await choice.press('Enter');assert.equal((await page.locator('[data-unit=home] [aria-pressed=true]').innerText()).replace(/\s+/g,' '),'✓ A');
 const data=await page.evaluate(()=>JSON.parse(localStorage.getItem('wireframe-review:1:sample-service:r1')));assert.equal(data.comments.length,100);assert.equal(data.pageOverrides.home.hero,'A');
 for(const width of [320,390,1500]){await page.setViewportSize({width,height:900});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`overflow at ${width}`);}
 await page.reload();await page.locator('.page-map .page-title').first().click();assert.equal(await page.locator('.comment').count(),100);assert.equal((await page.locator('[data-unit=home] [aria-pressed=true]').innerText()).replace(/\s+/g,' '),'✓ A');assert.deepEqual(errors,[]);
 console.log('PASS: 30 decisions, 100 comments, long content, override source, locate viewport/proposal, draft recovery, two panel views, keyboard selection, search, persistence, 320/390/1500 widths.');
 await page.locator('#intent-context summary').click();assert.match(await page.locator('#intent-content').innerText(),/Intended progress/);
 const beforeChoices=await page.evaluate(()=>JSON.stringify(JSON.parse(localStorage.getItem('wireframe-review:1:sample-service:r1')).choices));
 await page.locator('#missing-approach').click();await page.locator('#comment-text').fill('None supports resuming an interrupted task. B could work if progress is retained.');await page.getByRole('button',{name:'Save feedback',exact:true}).click();
 await page.locator('#open-feedback').click();const downloadReady=page.waitForEvent('download');await page.locator('#download').click();const downloaded=await downloadReady;const exported=JSON.parse(readFileSync(await downloaded.path(),'utf8'));assert.equal(exported.comments.at(-1).target.scope,'decision');assert.equal(exported.comments.at(-1).target.variantId,null);assert.equal(JSON.stringify(exported.choices),beforeChoices);assert.deepEqual(exported.context.intent,manifest.intent);
 await page.reload();await page.locator('.page-map .page-title').first().click();assert.match(await page.locator('#comments').innerText(),/None supports resuming/);
 console.log('PASS intent disclosure, choice-free decision feedback, contextual export and persistence.');
}finally{await browser.close();rmSync(tmp,{recursive:true,force:true});}
