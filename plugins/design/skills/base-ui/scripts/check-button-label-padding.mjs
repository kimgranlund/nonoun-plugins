import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
const [runtime,executablePath]=process.argv.slice(2);
const {chromium}=createRequire(import.meta.url)(runtime);
const browser=await chromium.launch({executablePath});
try {
 const page=await browser.newPage();
 const slot=(kind)=>`<span data-slot="${kind}" aria-hidden="true"></span>`;
 const arrangements=[['label'],['icon','label'],['label','glyph'],['icon','label','glyph'],['media','label'],['label','media']];
 await page.setContent(`<style>${getAssetBundle().css}</style><body class="product__root">${arrangements.flatMap(slots=>[0,1].map(shape=>`<button class="button__root" style="--control-radius-amount:${shape}" data-arrangement="${slots.join('-')}" data-shape="${shape}">${slots.map(s=>s==='label'?'<span data-slot="label">Label</span>':slot(s)).join('')}</button>`)).join('')}</body>`);
 let count=0;
 for(const direction of ['ltr','rtl'])for(const [index,density]of ['tight','compact','regular','spacious','loose'].entries()){
  const rows=await page.evaluate(({direction,density})=>{document.body.dir=direction;document.body.dataset.density=density;return [...document.querySelectorAll('button')].map(el=>{const c=getComputedStyle(el),label=getComputedStyle(el.querySelector('[data-slot=label]')),rects=[...el.children].map(s=>s.getBoundingClientRect()).sort((a,b)=>a.left-b.left);return {h:el.getBoundingClientRect().height,w:el.getBoundingClientRect().width,m:parseFloat(c.paddingInlineStart),start:parseFloat(label.paddingInlineStart),end:parseFloat(label.paddingInlineEnd),gaps:rects.slice(1).map((r,i)=>r.left-rects[i].right)};});},{direction,density});
  for(const r of rows){assert.equal(r.h,24+4*index);assert.equal(r.m,2*index);assert.equal(r.start,4);assert.equal(r.end,4);for(const gap of r.gaps)assert(Math.abs(gap)<.01);count++;}
  for(let i=0;i<rows.length;i+=2)assert.equal(rows[i].w,rows[i+1].w,'Sharp/Pill width differs');
 }
 console.log(`PASS ${count} rendered button contexts: half-unit labels, zero gaps, density margin and equal Sharp/Pill widths in LTR/RTL`);
} finally {await browser.close();}
