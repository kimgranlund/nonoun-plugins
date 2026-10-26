import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)(process.argv[2]||'playwright');
const b=await chromium.launch();try{const p=await b.newPage();await p.setContent(`<style>${fs.readFileSync(new URL('../assets/wireframe.css',import.meta.url),'utf8')}</style><style>.authored-art{border-radius:3px;overflow:visible}</style><button class="button__root" style="--g-media:24px"><span data-slot="media" data-media="avatar" style="--media-required-radius:8px"><svg class="authored-art" viewBox="0 0 24 24"><rect width="24" height="24"/></svg></span><span data-slot="icon"><svg class="authored-art"></svg></span><span data-slot="glyph"><svg class="authored-art"></svg></span></button>`);
for(const shape of ['default','control','circle','intrinsic']){
 const result=await p.evaluate(shape=>{const slot=document.querySelector('[data-slot=media]');if(shape==='default')slot.removeAttribute('data-media-shape');else slot.dataset.mediaShape=shape;const css=getComputedStyle(slot);return {radius:css.borderTopLeftRadius,overflow:css.overflow,art:[...document.querySelectorAll('.authored-art')].map(e=>[getComputedStyle(e).borderTopLeftRadius,getComputedStyle(e).overflow])};},shape);
 assert.equal(result.radius,{default:'50%',control:'8px',circle:'50%',intrinsic:'0px'}[shape]);assert.equal(result.overflow,'hidden');assert.deepEqual(result.art,[['3px','visible'],['3px','visible'],['3px','visible']]);
}
await p.locator('[data-slot=media]').evaluate(e=>e.dataset.geometryConflict='true');assert.equal(await p.locator('[data-slot=media]').evaluate(e=>getComputedStyle(e).overflow),'hidden');console.log('PASS wrapper shape/clipping and authored media/icon/glyph styles across default/control/circle/intrinsic and conflicts');}finally{await b.close();}
