import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
import {resolveDataRowGeometry} from '../assets/geometry/scale.mjs';
const [runtime,executablePath]=process.argv.slice(2);
const {chromium}=createRequire(import.meta.url)(runtime);
const browser=await chromium.launch({executablePath});
try {
 const page=await browser.newPage({viewport:{width:1000,height:800}});
 await page.setContent(`<style>${getAssetBundle().css}</style><body class="product__root"><table class="table__root"><tbody><tr id="row"><th scope="row"><span class="table__slot">Label</span></th><td><span class="table__slot">Value</span></td></tr></tbody></table><dl class="data-list__root"><div id="record"><dt>Label</dt><dd>Value</dd></div></dl></body>`);
 for(const [i,density] of ['tight','compact','regular','spacious','loose'].entries()){
  await page.evaluate(d=>document.body.dataset.density=d,density);
  const m=await page.evaluate(()=>{const q=s=>document.querySelector(s),r=e=>e.getBoundingClientRect(),c=e=>getComputedStyle(e);return {table:r(q('#row')).height,list:r(q('#record')).height,slot:r(q('.table__slot')).height,dt:r(q('dt')).height,start:parseFloat(c(q('th')).paddingLeft),end:parseFloat(c(q('th')).paddingRight),gap:parseFloat(c(q('#record')).columnGap),border:c(q('td')).borderBottomWidth,cellShadow:c(q('td')).boxShadow,rowShadow:c(q('#row')).boxShadow,listShadow:c(q('#record')).boxShadow};});
  const g=resolveDataRowGeometry(8,density);
  assert.equal(m.table,24+4*i);assert.equal(m.list,g.rowHeight);assert.equal(m.slot,24);assert.equal(m.dt,24);assert.equal(m.start,g.cellMargin);assert.equal(m.end,g.cellMargin+g.columnGap/2);assert.equal(m.gap,g.columnGap);assert.equal(m.border,'0px');assert.equal(m.cellShadow,'none');assert(m.rowShadow.includes('inset'));assert(m.listShadow.includes('inset'));
 }
 await page.evaluate(()=>{document.body.dataset.density='regular';document.querySelector('.table__slot').innerHTML='First line<br>Second line<br>Third line';document.querySelector('dt').innerHTML='First line<br>Second line<br>Third line';});
 for(const selector of ['#row','#record'])assert((await page.locator(selector).boundingBox()).height>32,'multiline grows '+selector);
 await page.screenshot({path:'/tmp/base-data-rows.png'});
 console.log('Data rows: five densities, centered slots, internal column gaps, single divider and multiline growth pass');
}finally{await browser.close();}
