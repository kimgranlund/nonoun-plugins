import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
const [runtime, executablePath, output] = process.argv.slice(2);
if (!runtime || !executablePath || !output) throw Error('Usage: check-geometry-spacing.mjs PLAYWRIGHT CHROME OUTPUT');
const pw = createRequire(import.meta.url)(path.resolve(runtime));
const browser = await pw.chromium.launch({executablePath});
const steps = ['sm','md','lg'], tiers = ['widget','product','content','brand'];
// Independent expected height matrices from the mathematical tier formula.
const heights = {widget:[20,24,28,24,28,32,28,32,36],product:[24,28,32,28,36,44,32,44,56],content:[32,36,40,36,44,52,40,52,64],brand:[44,48,52,48,56,64,52,64,76]};
const cases = [], errors = [];
fs.mkdirSync(output, {recursive:true});
const fixture = `<main class="page__root page__flow"><section class="card__root flow__root" id="card"><h1>Geometry and spacing</h1><p>Margins belong to the surface. Gutters separate related controls.</p><div class="actions__root" id="actions"><button id="first">Save</button><button>Cancel</button></div><div class="flow__root" data-scale="sm" id="nested"><button data-size="lg" id="nested-button">Nested</button><div data-tier="widget"><button id="nested-widget">Tool</button></div></div><details class="disclosure__root"><summary>Details</summary><div class="disclosure__body flow__root"><p>Expanded content keeps its own margin and a parent-owned gutter.</p><button>Inspect</button></div></details><div class="select__root"><select aria-label="Choice"><option>One</option></select><span data-slot="indicator" aria-hidden="true">⌄</span></div></section></main>`;
const css = getAssetBundle().css;
try {
 const page = await browser.newPage();page.on('pageerror', e=>errors.push(e.message));
 await page.setContent(`<!doctype html><html><meta name="viewport" content="width=device-width"><style>${css}</style><body class="product__root">${fixture}</body></html>`);
 await page.evaluate(()=>document.fonts.ready);
 for (const width of [390,1440]) for (const tier of tiers) for (const scale of steps) for (const size of steps) {
  await page.setViewportSize({width,height:1200});
  await page.locator('body').evaluate((e,x)=>Object.assign(e.dataset,x),{tier,scale,size});
  const m = await page.evaluate(()=>{
   const token=(el,name)=>{const p=document.createElement('i');p.style.cssText=`position:absolute;width:var(${name});height:0`;el.append(p);const n=p.getBoundingClientRect().width;p.remove();return n;};
   const card=document.querySelector('#card'), action=document.querySelector('#first'), group=document.querySelector('#actions');
   return {height:token(action,'--g-height'),margin:token(card,'--g-margin'),gutter:token(group,'--g-gutter'),legacy:token(card,'--g-inset'),cardPadding:parseFloat(getComputedStyle(card).paddingLeft),gap:parseFloat(getComputedStyle(group).columnGap),frame:action.getBoundingClientRect().height,nestedHeight:token(document.querySelector('#nested-button'),'--g-height'),widgetHeight:token(document.querySelector('#nested-widget'),'--g-height'),indicatorPosition:getComputedStyle(document.querySelector('[data-slot=indicator]')).insetInlineEnd,overflow:document.documentElement.scrollWidth>innerWidth+1};
  });
  const expected=heights[tier][steps.indexOf(scale)*3+steps.indexOf(size)];
  assert.equal(m.height,expected);assert.equal(m.legacy,m.margin);assert.equal(m.gutter,m.margin);
  assert(Math.abs(m.cardPadding-(3*m.margin-1))<.6);assert(Math.abs(m.gap-m.gutter)<.6);assert(m.frame>=m.height-.6);
  assert.equal(m.nestedHeight,heights[tier][2]);assert.equal(m.widgetHeight,heights.widget[steps.indexOf(size)]);
  assert.notEqual(m.indicatorPosition,'auto');assert(!m.overflow,JSON.stringify({tier,scale,size,width,m}));
  cases.push({tier,scale,size,width,...m});
 }
 // A gutter override must change sibling spacing without changing the card margin.
 await page.locator('body').evaluate(e=>Object.assign(e.dataset,{tier:'product',scale:'md',size:'md'}));
 await page.locator('#actions').evaluate(e=>e.style.setProperty('--g-gutter','13px'));
 assert.equal(await page.locator('#actions').evaluate(e=>parseFloat(getComputedStyle(e).columnGap)),13);
 assert.equal(await page.locator('#card').evaluate(e=>parseFloat(getComputedStyle(e).paddingLeft)),26);
 await page.locator('#actions').evaluate(e=>e.style.removeProperty('--g-gutter'));
 // Visual samples include every tier, narrow/wide, and expanded content.
 for(const width of [390,1440])for(const tier of tiers){
  await page.setViewportSize({width,height:1200});await page.locator('body').evaluate((e,t)=>e.dataset.tier=t,tier);
  await page.locator('body').evaluate((e,w)=>e.dataset.scale=w<600?'sm':'md',width);
  await page.locator('main').evaluate(e=>e.classList.add('reading-flow__root'));
  await page.locator('details').evaluate(e=>e.open=true);
  await page.screenshot({path:path.join(output,`${tier}-${width}.png`),fullPage:true});
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(output,'verification.json'),JSON.stringify({status:'pass',engine:browser.version(),cases,gutterOverride:true,limits:['Chromium only; no claim for Firefox, WebKit or assistive technology']},null,2)+'\n');
 console.log(`PASS ${cases.length} rendered tier/density/viewport cases, inheritance, spacing ownership, legacy reads and native positioning`);
} finally {await browser.close();}
