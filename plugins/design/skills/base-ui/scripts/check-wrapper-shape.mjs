import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
const [runtime,executablePath]=process.argv.slice(2);
if(!runtime||!executablePath)throw Error('Usage: check-wrapper-shape.mjs PLAYWRIGHT CHROME');
const {chromium}=createRequire(import.meta.url)(runtime);
const browser=await chromium.launch({executablePath});
try {
 const page=await browser.newPage();
 await page.setContent(`<style>${getAssetBundle().css}</style><body class="product__root" style="corner-shape:superellipse(1.5)"><button class="button__root" id="control">${['icon','glyph','media'].map(slot=>`<span data-slot="${slot}" ${slot==='media'?'data-media="avatar" data-media-shape="control"':''}><svg style="border-radius:3px;overflow:visible;corner-shape:bevel" viewBox="0 0 16 16"><rect width="16" height="16"/></svg></span>`).join('')}<span data-slot="label">Label</span></button><ul class="listbox__root"><li class="listbox__option" style="--listbox-option-radius:10px"><span data-slot="icon"><svg style="border-radius:3px;overflow:visible;corner-shape:bevel"></svg></span></li></ul></body>`);
 let count=0;
 for(const density of ['tight','compact','regular','spacious','loose'])for(const amount of [0,.005,.5,1])for(const retained of [0,1]){
  const actual=await page.evaluate(({density,amount,retained})=>{
   document.body.dataset.density=density;document.body.style.setProperty('--control-radius-amount',amount);document.body.style.setProperty('--control-radius-retained',retained);
   const p=document.querySelector('#control'),height=p.getBoundingClientRect().height;
   return {height,outerClip:getComputedStyle(p).overflow,slots:[...p.querySelectorAll(':scope > :is([data-slot=icon],[data-slot=glyph],[data-slot=media])')].map(el=>{const c=getComputedStyle(el),a=getComputedStyle(el.firstElementChild),r=el.getBoundingClientRect();return {r:parseFloat(c.borderTopLeftRadius),clip:c.overflow,corner:c.cornerShape,artCorner:a.cornerShape,width:r.width,height:r.height,artR:a.borderTopLeftRadius,artOverflow:a.overflow};}),row:parseFloat(getComputedStyle(document.querySelector('.listbox__option > span')).borderTopLeftRadius)};
  },{density,amount,retained});
  assert.equal(actual.outerClip,'hidden');
  for(const slot of actual.slots){assert.equal(slot.width,slot.height);assert.equal(slot.clip,'hidden');assert(['round','superellipse(1)'].includes(slot.corner));assert(['bevel','superellipse(0)'].includes(slot.artCorner));assert.equal(slot.artR,'3px');assert.equal(slot.artOverflow,'visible');assert(Math.abs(slot.r-(amount===0?0:Math.max(slot.height*amount/2,actual.height*amount/2*retained)))<.01);}
  assert(Math.abs(actual.row-(amount===0?0:Math.max(actual.slots[0].height*amount/2,10*retained)))<.01);count++;
 }
 // Measured conflict paint stays clipped; opt-out cleanup is the consumer's explicit API.
 const restored=await page.evaluate(()=>{
  const el=document.querySelector('[data-slot=media]');el.style.setProperty('--media-required-radius','30px');el.dataset.geometryConflict='true';
  const conflict={r:getComputedStyle(el).borderTopLeftRadius,clip:getComputedStyle(el).overflow,outline:getComputedStyle(el).outlineStyle};
  el.removeAttribute('data-media-shape');el.style.removeProperty('--media-required-radius');el.removeAttribute('data-geometry-conflict');
  return {conflict,r:getComputedStyle(el).borderTopLeftRadius,clip:getComputedStyle(el).overflow,artR:getComputedStyle(el.firstElementChild).borderTopLeftRadius};
 });
 assert.deepEqual(restored,{conflict:{r:'30px',clip:'hidden',outline:'dashed'},r:'50%',clip:'hidden',artR:'3px'});
 console.log(`PASS ${count} wrapper density/amount/retention contexts; Sharp/fractional, own-parent radius, artwork preservation, conflict clipping and explicit opt-out cleanup.`);
}finally{await browser.close();}
