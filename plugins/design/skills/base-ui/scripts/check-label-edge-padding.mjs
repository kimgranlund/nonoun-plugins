import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
const [runtime,executablePath]=process.argv.slice(2);
const {chromium}=createRequire(import.meta.url)(runtime);
const browser=await chromium.launch({executablePath});
try {
 const page=await browser.newPage();
 const arrangements=[[false,false],[true,false],[false,true],[true,true]];
 await page.setContent(`<style>${getAssetBundle().css}</style><body class="product__root">${arrangements.map(([a,b])=>`<button class="button__root">${a?'<span data-slot="icon"></span>':''}<span data-slot="label">Action</span>${b?'<span data-slot="glyph"></span>':''}</button>`).join('')}</body>`);
 for(const density of ['tight','compact','regular','spacious','loose']) {
  const widths=[];
  for(const shape of [0,1]) {
   const actual=await page.evaluate(({density,shape})=>{document.body.dataset.density=density;document.body.style.setProperty('--control-radius-amount',shape);return [...document.querySelectorAll('button')].map(el=>{const c=getComputedStyle(el.querySelector('[data-slot=label]'));return {start:parseFloat(c.paddingInlineStart),end:parseFloat(c.paddingInlineEnd),width:el.getBoundingClientRect().width};});},{density,shape});
   actual.forEach((r,i)=>{const [a,b]=arrangements[i],edge=!a&&!b?5:10;assert.equal(r.start,2+(a?0:edge));assert.equal(r.end,2+(b?0:edge));});
   widths.push(actual.map(r=>r.width));
  }
  assert.deepEqual(widths[0],widths[1]);
 }
 console.log('PASS 40 rendered button cases: label-only half, single exposed full, occupied zero, equal Sharp/Pill widths across five densities.');
} finally {await browser.close();}
