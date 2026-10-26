import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require(process.argv[2]||'playwright');
const browser=await chromium.launch(),page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
page.on('pageerror',e=>errors.push(e.message));
await page.goto(process.argv[3]||'http://127.0.0.1:8741/');
await page.waitForSelector('#listbox-density-grid [data-slot=media]');
const artwork=await page.evaluate(()=>{
 const media=document.querySelector('#button-density-grid [data-media=avatar]'),art=media.querySelector('svg');
 const initial=getComputedStyle(art).borderTopLeftRadius;
 const style=document.createElement('style');style.textContent='.authored-art{border-radius:3px;overflow:visible}';document.head.append(style);art.classList.add('authored-art');
 const result={initial,radius:getComputedStyle(art).borderTopLeftRadius,overflow:getComputedStyle(art).overflow,wrapper:getComputedStyle(media).overflow};
 style.remove();art.classList.remove('authored-art');return result;
});
assert.deepEqual(artwork,{initial:'0px',radius:'3px',overflow:'visible',wrapper:'hidden'});
const result=await page.evaluate(async()=>{
 const settle=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
 const click=s=>document.querySelector(s).click();
 const set=(id,v)=>{const e=document.getElementById(id);e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));};
 const shapes=()=>Object.fromEntries(['avatar','logo'].map(k=>[k,[...document.querySelectorAll(`.specimen [data-media=${k}]`)].every(e=>e.dataset.mediaShape===(k==='avatar'?'control':'intrinsic'))]));
 const dims=()=>[...document.querySelectorAll('#button-density-grid [data-slot]')].map(e=>{const r=e.getBoundingClientRect();return [r.width,r.height]});
 click('[data-media-toggle=avatarInherit]');set('controlAmount',100);set('controlRetained',100);await settle();
 const independent=shapes(),before=dims();click('[data-media-toggle=slotBoundaries]');await settle();const after=dims();
 const conflicts=[...document.querySelectorAll('#media-diagnostics figcaption')].map(e=>e.textContent);
 const states=[];for(const state of ['none','all','current']){click(`[data-media-selection=${state}]`);await settle();states.push([...document.querySelectorAll('#listbox-density-grid [aria-selected=true]')].length);}
 return {independent,before,after,conflicts,states};
});
assert.deepEqual(result.independent,{avatar:true,logo:true});assert.deepEqual(result.before,result.after);assert.deepEqual(result.states,[0,15,5]);assert(result.conflicts.some(t=>t.includes('Required R 20px / cap 12px')&&t.includes('Excess 8px')));
await page.locator('#media-diagnostics').evaluate(e=>e.open=true);
await page.locator('#media-comparison-controls').scrollIntoViewIfNeeded();await page.waitForTimeout(350);await page.screenshot({path:'/tmp/media-comparison-wide.png'});
await page.reload();await page.waitForSelector('#listbox-density-grid [data-slot=media]');assert.equal(await page.locator('#avatarInherit').getAttribute('aria-checked'),'true');assert.equal(await page.locator('#logoInherit').getAttribute('aria-checked'),'false');assert.equal(await page.locator('#slotBoundaries').getAttribute('aria-checked'),'true');
await page.setViewportSize({width:390,height:900});await page.reload();await page.waitForSelector('#listbox-density-grid [data-slot=media]');assert.equal(await page.locator('#listbox-densities .formula-summary').getAttribute('open'),null);assert(await page.evaluate(()=>document.documentElement.scrollWidth===innerWidth));await page.locator('#media-comparison-controls').scrollIntoViewIfNeeded();await page.waitForTimeout(350);await page.screenshot({path:'/tmp/media-comparison-narrow.png'});
assert.deepEqual(errors,[]);await browser.close();console.log('PASS media comparison: independent asset settings, diagnostics, unchanged slot dimensions, equivalent selection, persistence and narrow layout');
