import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
if (process.argv.includes('--help')) {
  console.log('Usage: node scripts/check-semantic-colors.mjs SHEETS PLAYWRIGHT REPORT\n12 engine/width/scheme cases; actual computed semantic-role pairs, keyboard focus, composited disabled action and isolated rejection controls. Findings do not certify whole accessibility or installed Safari.');
  process.exit(0);
}
const [output, playwright, destination] = process.argv.slice(2);
if (!destination) throw Error('SHEETS PLAYWRIGHT REPORT required');
const engines = createRequire(import.meta.url)(playwright);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const inventoryBytes = fs.readFileSync(path.join(output, 'inventory.json'));
const inventory = JSON.parse(inventoryBytes);
const sources = ['assets/recipes/semantic-colors.html','assets/recipes/semantic-colors.js','assets/wireframe.css','assets/foundation/ultimate-tokens/colors.css','references/style/contract.json','references/style/components/contract.json','references/style/product-foundation.md','scripts/lib/sheets/colors.mjs'].map(p => {
  const entry = inventory.sources.find(s => s.path === p);
  if (!entry?.sha256) throw Error('Missing inventory source identity: ' + p);
  return {path:p,sha256:entry.sha256};
});
if (hash(fs.readFileSync(path.join(output,'semantic-colors.js'))) !== sources.find(s=>s.path==='assets/recipes/semantic-colors.js').sha256) throw Error('Copied semantic runtime differs from inventory source');
const report = {schemaVersion:1,sourceHash:inventory.sourceHash,generatorSha256:inventory.generatorSha256,inventorySha256:hash(inventoryBytes),verifierSha256:hash(fs.readFileSync(new URL(import.meta.url))),outputInputs:Object.fromEntries(['index.html','colors.html','foundation.css','sheets.css','sheets.js','semantic-colors.js'].map(p => [p,hash(fs.readFileSync(path.join(output,p)))])),records:[],faultControls:[],limits:['Fixed semantic recipe only; no whole accessibility, generative reliability, native zoom, forced colors, every component state or installed Safari claim. Playwright WebKit is not installed Safari.']};
const root = '#colors-profile-roles';
const selectors = {surface:root+' [data-semantic-role="surface-text"]',label:root+' .field__root > label',help:root+' .field__help',border:root+' .field__root > input'};
// Browser extracts computed paint, then Node independently derives WCAG luminance.
const paint = (element, property) => {
  const rgba = value => {
    if (/var\(|calc\(/.test(value) || !CSS.supports('color',value)) throw Error('Unsupported color: '+value);
    const canvas = document.createElement('canvas');canvas.width=canvas.height=1;
    const ctx=canvas.getContext('2d',{colorSpace:'srgb',willReadFrequently:true});
    ctx.clearRect(0,0,1,1);ctx.fillStyle=value;ctx.fillRect(0,0,1,1);
    return [...ctx.getImageData(0,0,1,1).data].map((x,i)=>i===3?x/255:x);
  };
  const over=(a,b)=>{const alpha=a[3]+b[3]*(1-a[3]);return [0,1,2].map(i=>alpha?(a[i]*a[3]+b[i]*b[3]*(1-a[3]))/alpha:0).concat(alpha);};
  const cs=getComputedStyle(element),ancestors=[];
  for(let e=element.parentElement;e;e=e.parentElement)ancestors.unshift(e);
  let background=[0,0,0,0],unsupported=[];
  const check=(style,ancestor)=>{
    if(style.backgroundImage!=='none'||style.filter!=='none'||style.mixBlendMode!=='normal'||style.textShadow!=='none'||style.boxShadow!=='none'||(style.backdropFilter&&style.backdropFilter!=='none')||(ancestor&&Number(style.opacity)!==1))unsupported.push('Non-flat background, filter, blend or ancestor opacity');
  };
  for(const e of ancestors){const style=getComputedStyle(e);check(style,true);background=over(rgba(style.backgroundColor),background);}
  if(background[3]<1)unsupported.push('Canvas background not explicitly opaque');
  check(cs,false);
  const outside=background,opacity=Number(cs.opacity),fill=rgba(cs.backgroundColor);
  // Group opacity: compose text over the local fill, then the group over its parent.
  const groupFill=over(fill,[0,0,0,0]);
  const faded=a=>[a[0],a[1],a[2],a[3]*opacity];
  const inside=over(faded(groupFill),outside);
  const raw=rgba(cs[property]);
  const foreground=['outlineColor','borderTopColor'].includes(property)?over(faded(raw),outside):over(faded(over(raw,groupFill)),outside);
  const backdrop=['outlineColor','borderTopColor'].includes(property)?outside:inside;
  const tokens=Object.fromEntries(['surface','ink','label','muted','border','action','on-action','action-hover','focus','media-base'].map(role=>{
    if(!cs.getPropertyValue('--ui-'+role).trim())unsupported.push('Missing source role: '+role);
    const probe=document.createElement('span');
    probe.style.position='fixed';probe.style.visibility='hidden';
    probe.style.colorScheme=cs.colorScheme;
    probe.style.setProperty('--ui-'+role,cs.getPropertyValue('--ui-'+role));
    probe.style.color=`var(--ui-${role})`;
    document.body.append(probe);
    const value=rgba(getComputedStyle(probe).color);probe.remove();
    return [role,value];
  }));
  return {rawPaint:{foreground:raw,background:fill},outside,tokensResolved:tokens,computed:{color:cs.color,background:cs.backgroundColor,border:cs.borderTopColor,borderWidth:cs.borderTopWidth,borderStyle:cs.borderTopStyle,outline:cs.outlineColor,outlineWidth:cs.outlineWidth,outlineStyle:cs.outlineStyle,outlineOffset:cs.outlineOffset,opacity:cs.opacity,colorScheme:cs.colorScheme},resolvedPair:{foreground,background:backdrop},unsupported,nativeState:{hover:element.matches(':hover'),active:element.matches(':active'),focusVisible:element.matches(':focus-visible'),activeElement:document.activeElement===element,disabled:element.matches(':disabled')},method:'Actual getComputedStyle; CSS colors converted by sRGB canvas (8-bit quantization); flat alpha/group-opacity compositing; independent Node WCAG relative-luminance derivation'};
};
const luminance = rgb => rgb.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
const contrast = data => {const a=luminance(data.resolvedPair.foreground),b=luminance(data.resolvedPair.background);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);};
function result(data,threshold,reachable,exempt=false){
  const ratio=contrast(data);
  return {...data,ratio,threshold:exempt?null:threshold,thresholdPolicy:exempt?'Disabled action explicitly exempt; observation only':'Enabled text 4.5; relevant border/focus 3',reachability:{reached:reachable},contrastOutcome:data.unsupported.length?'inconclusive':exempt?'exempt':ratio>=threshold?'pass':'fail',outcome:!reachable?'fail':data.unsupported.length?'inconclusive':exempt?'inconclusive':ratio>=threshold?'pass':'fail'};
}
const schemeMatches=(actual,requested)=>actual.trim()===requested;
const equal=(a,b)=>a?.length===b?.length&&a.every((v,i)=>Math.abs(v-b[i])<(i===3?.005:1.1));
const visibleFocus=d=>d.nativeState.activeElement&&d.nativeState.focusVisible&&parseFloat(d.computed.outlineWidth)>0&& !['none','hidden'].includes(d.computed.outlineStyle);
const reached=(d,state)=>state==='hover'?d.nativeState.hover:state==='pressed'?d.nativeState.hover&&d.nativeState.active:state==='keyboard-focus'?visibleFocus(d):state==='disabled-hover'?d.nativeState.disabled&&d.nativeState.hover:state==='disabled'?d.nativeState.disabled&&!d.nativeState.hover:!d.nativeState.hover&&!d.nativeState.activeElement&&!d.nativeState.active;
function identity(d,variant,state){
  const interactive=['hover','pressed'].includes(state);
  const background=variant==='primary'?(interactive?'action-hover':'action'):(interactive?'media-base':'surface');
  const foreground=variant==='primary'?'on-action':'ink';
  const transparent=variant==='ghost'&&!interactive;
  return {backgroundRole:background,foregroundRole:foreground,transparentComposite:transparent,matches:equal(d.rawPaint.foreground,d.tokensResolved[foreground])&&(transparent?d.rawPaint.background[3]===0&&equal(d.resolvedPair.background,d.tokensResolved.surface):equal(d.rawPaint.background,d.tokensResolved[background]))};
}
function accept(d,{variant,state,property='color',threshold=4.5,exempt=false,baseline}={}){
  const entry={state,...result(d,threshold,reached(d,state),exempt)};
  if(variant&&!exempt&&property==='color'){entry.stateIdentity=identity(d,variant,state);if(!entry.stateIdentity.matches)entry.outcome='fail';}
  if(property==='outlineColor'){entry.stateIdentity={role:'focus',adjacentRole:'surface',matches:equal(d.rawPaint.foreground,d.tokensResolved.focus)&&equal(d.outside,d.tokensResolved.surface)};if(!visibleFocus(d)||!entry.stateIdentity.matches)entry.outcome='fail';}
  if(property==='borderTopColor'&&(parseFloat(d.computed.borderWidth)<=0||['none','hidden'].includes(d.computed.borderStyle)))entry.outcome='fail';
  if(baseline){entry.stability={matches:equal(d.resolvedPair.foreground,baseline.resolvedPair.foreground)&&equal(d.resolvedPair.background,baseline.resolvedPair.background)&&d.computed.opacity===baseline.computed.opacity};if(!entry.stability.matches)entry.outcome='fail';}
  return entry;
}
const sampleAccept=s=>s.outcome!=='fail'&&(s.state!=='pressed'||(s.stateIdentity?.matches===true&&s.nativeState?.active===true));
const busyAccept=(snapshot,phase,initial,words)=>phase==='running'?snapshot.disabled&&snapshot.busy==='true'&&snapshot.state==='running'&&!!snapshot.status.trim()&&snapshot.count===initial+1:!snapshot.disabled&&snapshot.busy===null&&snapshot.state==='completed'&&!!snapshot.status.trim()&&snapshot.status!==snapshot.runningStatus&&snapshot.count===initial+1&&snapshot.status===`Local word count completed: ${words} words. Job ${initial+1}.`;
const save=()=>fs.writeFileSync(destination,JSON.stringify(report,null,2)+'\n');
for(const name of ['chromium','firefox','webkit']) {
  let browser;
  try {browser=await engines[name].launch();} catch(error) {
    for(const width of [360,1399])for(const scheme of ['light','dark'])report.records.push({unitId:'colors-profile-roles',specimenId:'colors-profile-roles',checkId:'semantic-role-contrast',outcome:'inconclusive',sourceInputs:sources,environment:{kind:'browser',browser:{name,version:'unavailable'},viewport:{width,height:1000},scheme,reducedMotion:'reduce',keyboardPreference:name==='webkit'?'Alt+Tab':'Tab',geometry:{tier:'product',scale:'md',size:'md'}},error:String(error)});
    save();continue;
  }
  try {for(const width of [360,1399])for(const scheme of ['light','dark']) {
    const page=await browser.newPage({viewport:{width,height:1000},colorScheme:scheme,reducedMotion:'reduce'});
    const key=name==='webkit'?'Alt+Tab':'Tab';
    const environment={kind:'browser',browser:{name,version:browser.version()},viewport:{width,height:1000},scheme,reducedMotion:'reduce',keyboardPreference:key,geometry:{tier:'product',scale:'md',size:'md'}};
    const samples=[],controls=[];
    const fault=(mutation,measurement,kind='browser-mutation')=>controls.push({environment,mutation,kind,rejected:measurement.outcome==='fail',measurement});
    try {
      await page.goto(pathToFileURL(path.join(output,'colors.html')).href);
      await page.locator('#scheme').selectOption(scheme);
      if(await page.locator(root).count()!==1)throw Error('Stable semantic unit must occur exactly once');
      for(const [role,selector]of Object.entries(selectors))if(await page.locator(selector).count()!==1)throw Error('Missing or ambiguous role: '+role);
      const ids=await page.locator('[id]').evaluateAll(es=>es.map(e=>e.id));
      if(new Set(ids).size!==ids.length)throw Error('Duplicate document IDs');
      const fixture=page.locator(root+' .card__root').first();
      const actualScheme=await fixture.evaluate(e=>getComputedStyle(e).colorScheme);
      const schemeAcceptance=actual=>({outcome:schemeMatches(actual,scheme)?'pass':'fail',actual,requested:scheme});
      if(schemeAcceptance(actualScheme).outcome==='fail')throw Error('Semantic scheme mismatch');
      await page.mouse.move(0,0);
      for(const [role,selector]of Object.entries(selectors)){
        const property=role==='border'?'borderTopColor':'color';
        samples.push({role,...accept(await page.locator(selector).evaluate(paint,property),{state:'rest',property,threshold:role==='border'?3:4.5})});
      }
      for(const variant of ['primary','secondary','ghost']){
        const action=page.locator('#semantic-'+variant+'-enabled'),disabled=page.locator('#semantic-'+variant+'-disabled');
        if(await action.count()!==1||await disabled.count()!==1)throw Error('Missing appearance: '+variant);
        const read=async(locator,state,options={})=>accept(await locator.evaluate(paint,options.property||'color'),{variant,state,...options});
        await action.scrollIntoViewIfNeeded();await page.mouse.move(0,0);
        // Click the field to remove focus; move away to establish a real rest state.
        await page.locator(selectors.border).click();await page.mouse.move(0,0);
        const rest=await read(action,'rest');samples.push({role:variant,...rest});
        await action.hover();samples.push({role:variant,...await read(action,'hover')});
        await page.mouse.down();samples.push({role:variant,...await read(action,'pressed')});await page.mouse.up();await page.mouse.move(0,0);
        await page.locator(selectors.border).click();await page.mouse.move(0,0);
        let keyboardReached=false;
        for(let i=0;i<40;i++){await page.keyboard.press(key);if(await action.evaluate(e=>document.activeElement===e)){keyboardReached=true;break;}}
        const focus=await read(action,'keyboard-focus',{property:'outlineColor',threshold:3});focus.reachability.keyboardReached=keyboardReached;focus.reachability.key=key;if(!keyboardReached)focus.outcome='fail';samples.push({role:variant,...focus});
        // Focus text pair is also an enabled text requirement.
        samples.push({role:variant,...await read(action,'keyboard-focus')});
        await action.evaluate(e=>e.style.setProperty('outline','none','important'));
        fault(variant+' real focus outline removed',await read(action,'keyboard-focus',{property:'outlineColor',threshold:3}));await action.evaluate(e=>e.style.removeProperty('outline'));
        await page.mouse.move(0,0);
        const disabledRest=await read(disabled,'disabled',{exempt:true});samples.push({role:variant,...disabledRest});
        await disabled.hover();samples.push({role:variant,...await read(disabled,'disabled-hover',{exempt:true,baseline:disabledRest})});
        await disabled.evaluate(e=>e.style.opacity='.2');fault(variant+' disabled-hover opacity mutation',await read(disabled,'disabled-hover',{exempt:true,baseline:disabledRest}));await disabled.evaluate(e=>e.style.removeProperty('opacity'));
        await action.hover();
        // High contrast swapped role pair; identity must fail independently of ratio.
        await action.evaluate((e,v)=>{e.style.background=v==='primary'?'var(--ui-surface)':'var(--ui-action)';e.style.color=v==='primary'?'var(--ui-ink)':'var(--ui-on-action)';},variant);
        fault(variant+' high-contrast wrong hover pair',await read(action,'hover'));
        await page.mouse.down();fault(variant+' pressed identity wrong pair',await read(action,'pressed'));await page.mouse.up();
        await action.evaluate(e=>{e.style.removeProperty('background');e.style.removeProperty('color');});
        // Omission control exercises the exact real-state predicate with absent identity.
        const held=await (async()=>{await action.hover();await page.mouse.down();const d=await action.evaluate(paint,'color');await page.mouse.up();return d;})();
        const omitted=accept(held,{variant,state:'pressed'});delete omitted.stateIdentity;fault(variant+' pressed identity omission',{...omitted,outcome:sampleAccept(omitted)?'pass':'fail'},'synthetic-predicate-guard');
      }
      await page.mouse.move(0,0);
      const busy=page.locator('#semantic-busy-button'),status=page.locator('#semantic-busy-status');
      const snapshot=()=>page.locator('#semantic-busy-fixture').evaluate(e=>{const b=e.querySelector('button'),s=e.querySelector('[role=status]');return {disabled:b.disabled,busy:b.getAttribute('aria-busy'),state:s.dataset.state,status:s.textContent,count:Number(e.dataset.jobCount)};});
      if(await busy.isDisabled())throw Error('Complete busy runtime did not enable fixture');
      await page.locator(selectors.border).fill('local  counting example');const expectedWords=3;
      const initial=(await snapshot()).count;
      await busy.click();
      const atomic=await page.locator('#semantic-busy-fixture').evaluate((e,paintSource)=>{
        const b=e.querySelector('button'),s=e.querySelector('[role=status]');const take=()=>({disabled:b.disabled,busy:b.getAttribute('aria-busy'),state:s.dataset.state,status:s.textContent,count:Number(e.dataset.jobCount)});
        const readPaint=(0,eval)('('+paintSource+')');const running=take();b.dispatchEvent(new Event('click',{bubbles:true}));const guarded=take();return {running,guarded,busyPaint:readPaint(b,'color'),statusPaint:readPaint(s,'color')};
      },paint.toString());
      const {running,guarded}=atomic;
      const busyResult=(d,phase)=>({phase,...d,outcome:busyAccept(d,phase,initial,expectedWords)?'pass':'fail'});
      samples.push({role:'busy-lifecycle',state:'running',...busyResult(running,'running')});
      samples.push({role:'busy-paint',...accept(atomic.busyPaint,{state:'disabled-hover',exempt:true})});
      samples.push({role:'busy-status',...result(atomic.statusPaint,4.5,true),state:'running'});
      samples.push({role:'busy-reentry',state:'running',...busyResult(guarded,'running')});
      for(const [label,change]of [['aria missing',{busy:null}],['status empty',{status:''}],['native enabled',{disabled:false}],['reentry duplicate job',{count:initial+2}]])fault('busy running '+label,busyResult({...guarded,...change},'running'),'synthetic-predicate-guard');
      await page.waitForFunction(()=>document.getElementById('semantic-busy-status').dataset.state==='completed',null,{timeout:3000});
      const completed={...await snapshot(),runningStatus:running.status};samples.push({role:'busy-lifecycle',state:'completed',...busyResult(completed,'completed')});
      samples.push({role:'busy-status',...result(await status.evaluate(paint,'color'),4.5,true),state:'completed'});
      await status.evaluate(e=>e.textContent='Local word count completed: 0 words. Job 0.');fault('actual incorrect work result',busyResult({...await snapshot(),runningStatus:running.status},'completed'));await status.evaluate((e,text)=>e.textContent=text,completed.status);
      for(const [label,change]of [['busy retained',{busy:'true'}],['disabled retained',{disabled:true}],['status unchanged',{status:running.status}],['completion state missing',{state:'running'}],['job count changed',{count:initial+2}]])fault('busy completion '+label,busyResult({...completed,...change},'completed'),'synthetic-predicate-guard');
      await fixture.evaluate((e,s)=>e.style.colorScheme=s,scheme==='light'?'dark':'light');fault('wrong semantic scheme',schemeAcceptance(await fixture.evaluate(e=>getComputedStyle(e).colorScheme)));await fixture.evaluate(e=>e.style.removeProperty('color-scheme'));
      await page.locator(selectors.label).evaluate(e=>e.style.color=getComputedStyle(e.closest('.card__root')).backgroundColor);
      fault('low label contrast',accept(await page.locator(selectors.label).evaluate(paint,'color'),{state:'rest'}));
      report.records.push({unitId:'colors-profile-roles',specimenId:'colors-profile-roles',checkId:'semantic-role-contrast',sourceInputs:sources,environment,actualScheme,outcome:samples.some(s=>!sampleAccept(s))?'fail':samples.some(s=>s.unsupported?.length)?'inconclusive':'pass',samples,counts:{samples:samples.length,enabled:samples.filter(s=>s.threshold!==null&&s.ratio!==undefined).length,disabledExempt:samples.filter(s=>s.contrastOutcome==='exempt').length,controls:controls.length,rejected:controls.filter(c=>c.rejected).length},limits:report.limits});
    }catch(error){report.records.push({unitId:'colors-profile-roles',specimenId:'colors-profile-roles',checkId:'semantic-role-contrast',outcome:'inconclusive',sourceInputs:sources,environment,samples,error:String(error),counts:{samples:samples.length,controls:controls.length,rejected:controls.filter(c=>c.rejected).length}});}
    finally{report.faultControls.push(...controls);await page.close();save();}
  }}finally{await browser.close();}
}
const summary={records:report.records.length,findings:report.records.filter(r=>r.outcome!=='pass').length,samples:report.records.reduce((n,r)=>n+(r.samples?.length||0),0),controls:report.faultControls.length,rejected:report.faultControls.filter(c=>c.rejected).length};
summary.browserMutationControls=report.faultControls.filter(c=>c.kind==='browser-mutation').length;summary.syntheticPredicateGuards=report.faultControls.filter(c=>c.kind==='synthetic-predicate-guard').length;report.summary=summary;save();console.log(JSON.stringify(summary));
if(summary.findings||!summary.controls||summary.rejected!==summary.controls)process.exitCode=1;
