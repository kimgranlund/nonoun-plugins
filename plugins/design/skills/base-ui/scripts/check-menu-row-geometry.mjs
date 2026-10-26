import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
const [runtime,executablePath]=process.argv.slice(2);
const {chromium}=createRequire(import.meta.url)(runtime);
const browser=await chromium.launch({executablePath});
try {
 const page=await browser.newPage();
 await page.setContent(`<style>${getAssetBundle().css}</style><body class="product__root" style="--control-radius-amount:1"><div role="menu">${['menuitem','menuitemcheckbox','menuitemradio'].map(role=>`<button class="button__root listbox__option" role="${role}"><span data-slot="label">Command</span></button>`).join('')}</div></body>`);
 for (const [index,density] of ['tight','compact','regular','spacious','loose'].entries()) {
 const rows=await page.evaluate(density=>{document.body.dataset.density=density;return [...document.querySelectorAll('button')].map(el=>{const c=getComputedStyle(el),s=getComputedStyle(el.firstChild);return {height:el.getBoundingClientRect().height,padding:parseFloat(c.paddingTop),inline:parseFloat(c.paddingLeft),gap:parseFloat(c.gap),slot:el.firstChild.getBoundingClientRect().height,label:parseFloat(s.paddingLeft),radius:parseFloat(c.borderTopLeftRadius),parent:parseFloat(c.getPropertyValue('--control-slot-parent-radius'))};});},density);
 for(const row of rows){assert.equal(row.height,24+4*index);assert.equal(row.slot,24);assert.equal(row.padding,2*index);assert.equal(row.inline,2*index);assert.equal(row.gap,0);assert.equal(row.label,4);assert.equal(row.radius,row.height/2);}
 }
 console.log('PASS 15 menu role/density contexts: full frame, fixed slots, per-edge clearance, gap, radius and no label compensation.');
} finally {await browser.close();}
