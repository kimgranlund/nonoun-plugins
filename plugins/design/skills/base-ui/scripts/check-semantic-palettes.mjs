import fs from 'node:fs';import assert from 'node:assert/strict';import {createRequire} from 'node:module';import {getAssetBundle,compileControls} from './api.mjs';import {auditRendered} from './lib/audit-rendered.mjs';
const [modulePath,executablePath]=process.argv.slice(2);const {chromium}=createRequire(import.meta.url)(modulePath);
const contract=JSON.parse(fs.readFileSync(new URL('../references/semantic-palettes.json',import.meta.url))),families=JSON.parse(fs.readFileSync(new URL('../references/style/components/contract.json',import.meta.url))).families;
for(const html of ['<button class="button__root" data-intent="bogus">Bad</button>','<div data-intent="danger"></div>','<span class="badge__root" data-intent="warning" data-appearance="ghost"></span>','<button class="button__root secondary" data-intent="info"></button>'])assert.throws(()=>compileControls(html),/Unsupported semantic/);
const b=await chromium.launch({headless:true,executablePath});let count=0,min=Infinity;
try{const p=await b.newPage({viewport:{width:1000,height:800},reducedMotion:'reduce'});const errors=[];p.on('pageerror',e=>errors.push(e.message));
const css=getAssetBundle().css;
const measure=()=>{const e=document.querySelector('#probe'),s=getComputedStyle(e),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');canvas.width=canvas.height=1;const rgb=c=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data].slice(0,3).map(v=>v/255)};const lum=c=>rgb(c).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);const a=lum(s.color),d=lum(s.backgroundColor);return {ratio:(Math.max(a,d)+.05)/(Math.min(a,d)+.05),bg:s.backgroundColor,fg:s.color,opacity:s.opacity};};
for(const scheme of ['light','dark']){await p.emulateMedia({colorScheme:scheme});await p.setContent('<style>'+css+'</style><main id="host"></main>');
 for(const intent of Object.keys(contract.intents))for(const component of contract.components.filter(c=>c.class!=='field__root'))for(const appearance of component.appearances){
 const tag=component.class==='button__root'?'button':'div';await p.locator('#host').evaluate((e,{tag,component,intent,appearance})=>{e.innerHTML=`<${tag} id="probe" class="${component.class}" data-intent="${intent}" data-appearance="${appearance}">Visible status</${tag}>`;},{tag,component,intent,appearance});
 for(const state of component.class==='button__root'?['rest','hover','active','disabled']:['rest']){
  if(state==='rest')await p.mouse.move(999,799);if(state==='hover')await p.locator('#probe').hover();if(state==='active')await p.mouse.down();if(state==='disabled'){await p.mouse.up();await p.locator('#probe').evaluate(e=>e.disabled=true)}
  const m=await p.evaluate(measure);assert(m.ratio>=4.5,JSON.stringify({scheme,intent,appearance,state,...m}));min=Math.min(min,m.ratio);count++;
  const solid=appearance==='solid';const role=solid?(state==='hover'?'hover':state==='active'?'active':'solid'):(state==='hover'?'soft-hover':state==='active'?'soft-active':'soft');
  const mapping=contract.roles[role],sample=mapping[scheme],family=contract.intents[intent];
  const matches=await p.evaluate(({family,group,sample})=>{const probe=document.querySelector('#probe'),span=document.createElement('span');span.style.color=`var(--bu-source-${family}-${group}-${sample})`;document.body.append(span);const canvas=document.createElement('canvas');canvas.width=canvas.height=1;const ctx=canvas.getContext('2d');const pixels=color=>{ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data]};const actual=pixels(getComputedStyle(probe).backgroundColor),expected=pixels(getComputedStyle(span).color);span.remove();return actual.every((v,i)=>Math.abs(v-expected[i])<=1);},{family,group:mapping.group,sample});
  assert(matches,`Source-group paint mismatch: ${scheme} ${intent} ${appearance} ${state}`);
  if(state==='disabled'){const before=m;await p.mouse.move(999,799);assert.deepEqual(await p.evaluate(measure),before)}
 }
 }
 for(const intent of Object.keys(contract.intents)){
  await p.locator('#host').evaluate((e,intent)=>e.innerHTML=`<div class="field__root" data-intent="${intent}"><label for="field">Email</label><input id="field" aria-invalid="true" aria-describedby="probe"><span id="probe" class="field__error">Enter a valid email</span></div>`,intent);
  const m=await p.evaluate(measure);assert(m.ratio>=4.5);min=Math.min(min,m.ratio);count++;
  await p.locator('#field').focus();assert(await p.locator('#field').evaluate(e=>getComputedStyle(e).outlineStyle!=='none'&&parseFloat(getComputedStyle(e).outlineWidth)>0));
 }
 await p.locator('#host').evaluate(e=>e.innerHTML='<section class="notice__root" data-intent="danger"><p>Danger notice</p><button id="nested" class="button__root">Neutral child</button><button id="explicit" class="button__root" data-intent="success">Success child</button></section><button id="control" class="button__root">Neutral reference</button>');
 assert.equal(await p.locator('#nested').evaluate(e=>getComputedStyle(e).backgroundColor),await p.locator('#control').evaluate(e=>getComputedStyle(e).backgroundColor));assert.notEqual(await p.locator('#explicit').evaluate(e=>getComputedStyle(e).backgroundColor),await p.locator('#nested').evaluate(e=>getComputedStyle(e).backgroundColor));
 await p.locator('#host').evaluate(e=>e.insertAdjacentHTML('beforeend','<div data-intent="unknown">Injected unsupported variant</div>'));
 const audit=await p.evaluate(auditRendered,{families,retrieved:families.map(f=>f.id)});assert(audit.issues.some(i=>i.code==='SEMANTIC_VARIANT'));
}
await p.emulateMedia({forcedColors:'active'});assert(await p.locator('#explicit').evaluate(e=>getComputedStyle(e).backgroundColor===getComputedStyle(document.body).backgroundColor));assert.deepEqual(errors,[]);
console.log(JSON.stringify({result:'PASS semantic palette browser checks',contrastCases:count,minimumTextContrast:min,checks:['exact Prime/Base rendered source mapping','static rejected variants','dynamic rejected variant','nested neutral and explicit intent isolation','disabled hover stable','forced colors system paint'],errors}));
}finally{await b.close()}
