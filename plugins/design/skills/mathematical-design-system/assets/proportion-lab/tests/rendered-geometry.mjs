import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require(process.argv[2]||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.argv[4]}),p=await b.newPage({viewport:{width:1440,height:1000}});await p.goto(process.argv[3]||'http://127.0.0.1:8741/');await p.waitForTimeout(600);const result=await p.evaluate(async()=>{const issues=[];let count=0;const change=(id,v)=>{const e=document.getElementById(id);e.value=v;e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input',{bubbles:true}));};for(const [tier,scale,size] of [['widget','sm','sm'],['product','md','md'],['brand','lg','lg']])for(const amount of [0,50,100]){change('tier',tier);change('scale',scale);change('size',size);change('controlAmount',amount);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));for(const el of document.querySelectorAll('.specimen .button__root,.specimen .listbox__option')){const cs=getComputedStyle(el),S=parseFloat(cs.getPropertyValue('--surface-inner')),M=parseFloat(cs.getPropertyValue('--surface-margin')),W=S/6,R=amount*el.getBoundingClientRect().height/200,slots=[...el.children].filter(e=>e.hasAttribute('data-slot'));for(const [i,slot]of slots.entries()){const r=slot.getBoundingClientRect(),s=getComputedStyle(slot),type=slot.dataset.slot;const test=(a,b,k)=>{if(Math.abs(a-b)>.1)issues.push({tier,scale,size,amount,id:el.id,section:el.closest('section')?.id,type,k,a,b})};if(['icon','glyph','media'].includes(type)){test(r.width,S,'width');test(r.height,S,'height');if(type==='media')test(parseFloat(s.paddingLeft)+parseFloat(s.paddingRight),0,'media padding');}if(type==='label'){const button=!el.matches('.listbox__option');test(parseFloat(s.paddingInlineStart),W,'start');test(parseFloat(s.paddingInlineEnd),W,'end');}}count++;}}return {count,issues};});assert.deepEqual(result.issues,[]);console.log(`PASS ${result.count} rendered controls: fixed wrappers, media padding and uniform half-unit labels`);
for(const width of [390,1440]){
 await p.setViewportSize({width,height:1000});
 const checks=await p.evaluate(async()=>{
  const errors=[];const set=(id,value)=>{const e=document.getElementById(id);e.value=value;e.dispatchEvent(new Event('input',{bubbles:true}));};
  const settle=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  for(const amount of [0,50,100])for(const retained of [0,100]){
   set('controlAmount',amount);set('controlRetained',retained);
   for(const toggle of document.querySelectorAll('[data-media-toggle=avatarInherit],[data-media-toggle=logoInherit]'))if(toggle.getAttribute('aria-checked')!=='true')toggle.click();await settle();
   for(const e of document.querySelectorAll('.specimen [data-slot=media],.specimen [data-slot=icon],.specimen [data-slot=glyph],.spacing-demo[data-rule=composed] [data-slot=icon],.spacing-demo[data-rule=composed] [data-slot=glyph]')){
    if(getComputedStyle(e).overflow!=='hidden')errors.push('Artwork wrapper does not clip');
    const box=e.getBoundingClientRect(),parent=Number(e.parentElement.dataset.requiredRadius),shape=e.parentElement.dataset.comparisonShape,A=shape?(shape==='sharp'?0:100):amount,T=shape?0:retained,expected=A===0?0:Math.max(A*box.height/200,T*parent/100);
    if(Math.abs(Number(e.dataset.requiredRadius)-expected)>.01)errors.push('Media radius differs from immediate-parent formula');
    if((e.dataset.radiusConflict==='true')!==(expected>Math.min(box.width,box.height)/2+0.001))errors.push('Artwork wrapper physical conflict differs');
    if(Math.abs(parseFloat(getComputedStyle(e).borderTopLeftRadius)-(e.dataset.radiusConflict==='true'?0:expected))>.01)errors.push('Wrapper painted radius differs from validated value');
   }
  }
  for(const toggle of document.querySelectorAll('[data-media-toggle=avatarInherit],[data-media-toggle=logoInherit]'))toggle.click();await settle();
  for(const e of document.querySelectorAll('.specimen [data-slot=media]')){const expected=e.dataset.media==='avatar'?e.getBoundingClientRect().height/2:0;if(Number(e.dataset.requiredRadius)!==expected)errors.push('Asset-owned shape not restored');}
  for(const [key,space] of [['wrapperGuides','slot-padding'],['centeringGuides','centering'],['gutterGuides','gutter']]){
   const button=document.querySelector(`[data-key=${key}][data-action=card-guide]`);button.click();await settle();
   if([...document.querySelectorAll(`.content-spacing-overlay [data-space=${space}]`)].some(e=>getComputedStyle(e).display!=='none'))errors.push(key+' did not hide its contribution');
   button.click();await settle();
  }
  return errors;
 });assert.deepEqual(checks,[]);
}
console.log('PASS narrow/wide icon/glyph/media inheritance and clipping, Sharp, conflicts, media opt-out and separate guides');
assert.equal(await p.locator('[data-key=compensationGuides], [data-space=compensation]').count(),0);
const widths=[];
for(const amount of [0,50,100]){
 await p.locator('#controlAmount').evaluate((el,value)=>{el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));},String(amount));
 await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
 widths.push(await p.locator('#button-density-grid .density-button').evaluateAll(els=>els.map(el=>el.getBoundingClientRect().width)));
}
assert.equal(widths[0].length,50);
assert.deepEqual(widths[0],widths[1]);assert.deepEqual(widths[0],widths[2]);
console.log('PASS 50 density/arrangement/shape widths unchanged across Sharp, intermediate and Pill');
const pairs=await p.locator('#button-density-grid .density-arrangement').evaluateAll(es=>es.map(e=>[...e.querySelectorAll('button')].map(b=>({width:b.getBoundingClientRect().width,height:b.getBoundingClientRect().height,radius:parseFloat(getComputedStyle(b).borderRadius)}))));
assert.equal(pairs.length,25);for(const [sharp,pill] of pairs){assert.equal(sharp.width,pill.width);assert.equal(sharp.radius,0);assert.equal(pill.radius,pill.height/2);}
const cardMetrics=()=>p.locator('#button-density-grid .canvas').evaluateAll(es=>es.map(e=>({margin:parseFloat(getComputedStyle(e).paddingTop),gap:parseFloat(getComputedStyle(e).gap),radius:parseFloat(getComputedStyle(e).borderRadius),widths:[...e.querySelectorAll('button')].map(b=>b.getBoundingClientRect().width)})));
const before=await cardMetrics();
for(const [id,value] of [['containerAmount','100'],['containerGutter','100']])await p.locator('#'+id).evaluate((e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));},value);
await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const after=await cardMetrics();for(let i=0;i<5;i++){assert.equal(after[i].radius,after[i].margin);assert.equal(after[i].gap,after[i].margin);assert.deepEqual(before[i].widths,after[i].widths);}
console.log('PASS 25 equal-width Sharp/Pill pairs and independent Container card response');

// Check supporting examples too: CSS overrides must not leave stale gap guides
// or quarter-unit label padding in the role/tier comparisons.
for(const density of ['tight','compact','regular','spacious','loose']){
 await p.locator('#density').evaluate((el,value)=>{el.value=value;el.dispatchEvent(new Event('change',{bubbles:true}));},density);
 await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
 const errors=await p.evaluate(()=>{
  const errors=[],near=(a,b,label)=>{if(Math.abs(a-b)>.05)errors.push({label,a,b});};
  for(const el of document.querySelectorAll('.specimen .button__root,.specimen .listbox__option,.spacing-demo[data-rule=composed],.tier-demo[data-role=control]')){
   const tier=el.matches('.tier-demo'),slots=[...el.children].filter(s=>tier?s.tagName==='SPAN':s.hasAttribute('data-slot'));
   const ordered=slots.map(s=>s.getBoundingClientRect()).sort((a,b)=>a.left-b.left);
   for(let i=1;i<ordered.length;i++)near(ordered[i].left-ordered[i-1].right,0,'measured slot gap');
   if(tier||el.matches('.spacing-demo')){
    const S=parseFloat(getComputedStyle(el).getPropertyValue(tier?'--example-height':'--rule-inner'));
    for(const slot of slots)if(tier||slot.dataset.slot==='label'){
     near(parseFloat(getComputedStyle(slot).paddingInlineStart),S/6,'label start');
     near(parseFloat(getComputedStyle(slot).paddingInlineEnd),S/6,'label end');
    }
    for(const slot of slots.slice(1))near(parseFloat(getComputedStyle(slot,'::before').width)||0,0,'obsolete gap guide');
   }
  }
  return errors;
 });assert.deepEqual(errors,[],density);
}
console.log('PASS five densities: actual slot gaps, half-unit role/tier labels and zero obsolete gap guides');
await b.close()})()
