import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
const [runtime,executablePath]=process.argv.slice(2);
const {chromium}=createRequire(import.meta.url)(runtime);
const browser=await chromium.launch({executablePath});
try {
 const page=await browser.newPage();
 const label='<span data-slot="label">Action</span>',icon='<span data-slot="icon">●</span>',glyph='<span data-slot="glyph">›</span>',media='<span data-slot="media"></span>';
 await page.setContent(`<style>${getAssetBundle().css}</style><body class="product__root">${[label,icon+label,label+glyph,media+label,label+media].map((html,i)=>`<button class="button__root" id="b${i}">${html}</button>`).join('')}</body>`);
 for(const [index,density] of ['tight','compact','regular','spacious','loose'].entries()) {
  let baseline;
  for(const amount of [0,.5,1]) {
   const rows=await page.evaluate(({density,amount})=>{document.body.dataset.density=density;document.body.style.setProperty('--control-radius-amount',amount);return [...document.querySelectorAll('button')].map(e=>{const c=getComputedStyle(e),label=e.querySelector('[data-slot=label]'),s=getComputedStyle(label);return {width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height,outer:parseFloat(c.paddingLeft),gap:parseFloat(c.gap),start:parseFloat(s.paddingLeft),end:parseFloat(s.paddingRight)};});},{density,amount});
   for(const [i,row] of rows.entries()) {assert.equal(row.height,24+index*4);assert.equal(row.outer,index*2);assert.equal(row.gap,index);assert.equal(row.start,i===0?7:[1,3].includes(i)?2:12);assert.equal(row.end,i===0?7:[2,4].includes(i)?2:12);}
   if(baseline)assert.deepEqual(rows,baseline,'shape changes must preserve every spacing and width');else baseline=rows;
  }
 }
 console.log('PASS 75 rendered button contexts: five arrangements × five densities × three shapes, exposed sides and invariant widths.');
} finally {await browser.close();}
