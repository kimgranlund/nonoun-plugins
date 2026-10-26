#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [runtime,output]=process.argv.slice(2);if(!runtime||!output)throw Error('Usage: check-native-patterns.mjs PLAYWRIGHT OUTPUT');
fs.mkdirSync(output,{recursive:true});
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const css=['assets/foundation/ultimate-tokens/colors.css','assets/foundation/ultimate-tokens/typography.css','assets/foundation/maison/geometry.css','assets/foundation/maison/layout.css','assets/wireframe.css'].map(read).join('\n');
const recipe=read('assets/recipes/native-patterns.html');
fs.writeFileSync(path.join(output,'index.html'),`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Native patterns verification</title><style>${css}\nbody{padding:24px}main{max-width:960px;margin-inline:auto}</style><body class="product__root" data-tier="product" data-scale="md" data-size="md">${recipe}</body></html>`);
const engines=createRequire(import.meta.url)(runtime);
const report={runs:[],negativeControls:[],pageScripts:false,limits:['Playwright engines, not installed Safari','No screen-reader or physical touch-device audit','WebKit uses Alt+Tab to include links with default macOS keyboard preference']};
for(const name of ['chromium','firefox','webkit']){
 const browser=await engines[name].launch();
 try{const ctx=await browser.newContext({javaScriptEnabled:false});const p=await ctx.newPage();
 for(const width of [360,1200])for(const size of ['sm','md','lg'])for(const dir of ['ltr','rtl']){
  await p.setViewportSize({width,height:900});await p.goto(pathToFileURL(path.resolve(output,'index.html')).href);
  await p.evaluate(({size,dir})=>{document.body.dataset.size=size;document.documentElement.dir=dir;document.documentElement.style.colorScheme=dir==='ltr'?'light':'dark';},{size,dir});
  const trigger=p.locator('#native-nav-trigger'),panel=p.locator('#native-nav-panel');
  p.setDefaultTimeout(5000);const checks={};const check=async(k,fn)=>{checks[k]=await fn();assert(checks[k],JSON.stringify({name,width,size,dir,failed:k}));};
  await check('panelControlRadius',()=>p.evaluate(()=>{const keys=['borderTopLeftRadius','borderTopRightRadius','borderBottomLeftRadius','borderBottomRightRadius'];return ['nav','team'].every(id=>{const a=getComputedStyle(document.querySelector('#native-'+id+'-trigger')),b=getComputedStyle(document.querySelector('#native-'+id+'-panel'));return keys.every(k=>a[k]===b[k]);});}));
  await check('documentContained',()=>p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));const initial=await trigger.boundingBox();await trigger.focus();await p.keyboard.press('Space');
  await check('keyboardOpen',()=>panel.isVisible());
  const geometry=()=>p.evaluate(()=>{const t=document.querySelector('#native-nav-trigger').getBoundingClientRect(),e=document.querySelector('#native-nav-panel'),r=e.getBoundingClientRect(),probe=document.createElement('span');probe.style.cssText='position:absolute;width:calc(var(--g-margin)/2)';e.append(probe);const u=probe.getBoundingClientRect().width;probe.remove();return {gap:Math.abs((r.top>=t.bottom?r.top-t.bottom:t.top-r.bottom)-u)<1,contained:r.left>=-.5&&r.right<=innerWidth+.5&&r.top>=-.5&&r.bottom<=innerHeight+.5,scrollable:getComputedStyle(e).overflowY==='auto',u};});
  await check('halfMarginGap',async()=>(await geometry()).gap);await check('contained',async()=>(await geometry()).contained);
  if(size==='md'&&dir==='ltr')await p.screenshot({path:path.join(output,`${name}-${width}-popover.png`)});
  await check('stableTrigger',async()=>{const r=await trigger.boundingBox();return Math.abs(r.y-initial.y)<.5&&Math.abs(r.height-initial.height)<.5});
  await p.keyboard.press(name==='webkit'?'Alt+Tab':'Tab');await check('linkFocus',()=>panel.locator('a').first().evaluate(e=>e===document.activeElement));
  await p.keyboard.press('Escape');await check('escapeClose',async()=>!await panel.isVisible());await check('returnFocus',()=>trigger.evaluate(e=>e===document.activeElement));
  await trigger.click();await p.locator('#native-team-trigger').focus();await p.keyboard.press('Space');await check('peerCloses',async()=>!await panel.isVisible()&&await p.locator('#native-team-panel').isVisible());await p.mouse.click(width-2,898);await check('outsideCloses',async()=>!await p.locator('#native-team-panel').isVisible());
  await check('disclosureCaretClosed',()=>p.evaluate(()=>{const d=document.querySelector('#native-details-one');d.open=false;const s=d.querySelector('summary'),c=getComputedStyle(s,'::before'),b=getComputedStyle(s),rtl=document.documentElement.dir==='rtl';return b.display==='flex'&&b.alignItems==='center'&&b.justifyContent==='space-between'&&c.order==='1'&&b.fontSize===getComputedStyle(document.querySelector('#native-nav-trigger')).fontSize&&parseFloat(b.paddingInlineStart)>0&&parseFloat(getComputedStyle(d).borderTopWidth)>0&&parseFloat(b.borderTopWidth)===0&&b.listStyleType==='none'&&c.maskImage.includes('data:image/svg+xml')&&c.width===c.height&&parseFloat(c.width)>0&&c.transform===(rtl?'matrix(-1, 0, 0, -1, 0, 0)':'none');}));
  await p.locator('#native-details-one summary').focus();await p.keyboard.press('Enter');
  await check('disclosureCaretOpen',()=>p.evaluate(()=>{const d=document.querySelector('#native-details-one');return d.open&&getComputedStyle(d.querySelector('summary'),'::before').transform==='matrix(0, 1, -1, 0, 0, 0)';}));
  await p.keyboard.press('Enter');
  await p.locator('#native-details-one summary').click();await p.locator('#native-details-two summary').click();await check('exclusiveAccordion',()=>p.evaluate(()=>!document.querySelector('#native-details-one').open&&document.querySelector('#native-details-two').open));
  await p.locator('#native-dialog-open').focus();await p.keyboard.press('Space');await check('modal',()=>p.locator('#native-dialog').evaluate(e=>e.matches(':modal')));await check('dialogInitialFocus',()=>p.locator('#native-display-name').evaluate(e=>e===document.activeElement));for(let i=0;i<4;i++){await p.keyboard.press('Tab');await check('dialogNoBackgroundFocus'+i,()=>p.locator('#native-dialog').evaluate(e=>document.activeElement===document.body||e.contains(document.activeElement)));}await p.locator('#native-nav-trigger').evaluate(e=>e.focus());await check('modalBackgroundInert',()=>p.locator('#native-nav-trigger').evaluate(e=>e!==document.activeElement));await p.locator('#native-dialog-close').click();await check('dialogClosed',async()=>!await p.locator('#native-dialog').isVisible());await check('dialogFocusReturn',()=>p.locator('#native-dialog-open').evaluate(e=>e===document.activeElement));
  await p.locator('#native-dialog-open').click();await p.keyboard.press('Escape');await check('dialogEscape',async()=>!await p.locator('#native-dialog').isVisible());
  await p.evaluate(()=>scrollTo(0,0));await trigger.click();await p.evaluate(()=>scrollBy(0,24));await check('anchorTracksScroll',async()=>{for(let attempt=0;attempt<10;attempt++){if((await geometry()).gap)return true;await new Promise(r=>setTimeout(r,50));}return false;});await p.keyboard.press('Escape');
  // Clipping ancestor and viewport-edge placement are measured on the real recipe.
  await p.evaluate(()=>{const t=document.querySelector('#native-nav-trigger');t.parentElement.style.overflow='hidden';t.style.cssText+=';position:fixed;bottom:8px;right:8px;z-index:1';});await trigger.click();await check('edgeFlipAndContainment',async()=>(await geometry()).contained&&(await geometry()).gap);
  await p.evaluate(()=>{const panel=document.querySelector('#native-nav-panel');for(let i=0;i<60;i++){const link=document.createElement('a');link.href='#native-overview';link.textContent='Long menu entry '+i;link.style.display='block';panel.append(link);}});
  await check('oversizedPanelContained',async()=>(await geometry()).contained);await check('oversizedPanelScrolls',()=>panel.evaluate(e=>e.scrollHeight>e.clientHeight&&getComputedStyle(e).overflowY==='auto'));
  if(size==='md'&&dir==='ltr')await p.screenshot({path:path.join(output,`${name}-${width}.png`)});
  report.runs.push({browser:name,version:browser.version(),width,size,dir,scheme:dir==='ltr'?'light':'dark',checks});
 }
 // A broken panel offset must fail the same geometry assertion used above.
 await p.goto(pathToFileURL(path.resolve(output,'index.html')).href);await p.locator('#native-nav-trigger').click();
 const broken=await p.evaluateHandle(()=>{const s=document.createElement('style');s.textContent='.menu__content {margin:80px!important}';document.head.append(s);return s;});
 const brokenGap=await p.evaluate(()=>{const t=document.querySelector('#native-nav-trigger').getBoundingClientRect(),r=document.querySelector('#native-nav-panel').getBoundingClientRect();return Math.min(Math.abs(r.top-t.bottom),Math.abs(t.top-r.bottom));});assert(brokenGap>10,'offset negative control not detected');await broken.evaluate(e=>e.remove());report.negativeControls.push({browser:name,offsetDetected:true});
 }finally{await browser.close();}
}
fs.writeFileSync(path.join(output,'verification.json'),JSON.stringify(report,null,2));console.log(`PASS ${report.runs.length} native no-JS cases, ${report.negativeControls.length} negative controls across three engines`);
