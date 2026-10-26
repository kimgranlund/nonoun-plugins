import {resolveGeometry as resolve} from './scale.mjs?v=source-a72d65add853';
export const version=3;
export const storageKey='proportion-inspector';
export const schema={
 tier:{options:['widget','product','content','brand']},scale:{options:['sm','md','lg']},size:{options:['sm','md','lg']},density:{options:['tight','compact','regular','spacious','loose']},
 ...Object.fromEntries(['pageGutter','containerGutter','groupGutter','controlGutter'].map(k=>[k,{min:0,max:200,step:5}])),
 ...Object.fromEntries(['containerAmount','controlAmount','containerRetained','controlRetained'].map(k=>[k,{min:0,max:100,step:1}])),
 avatarInherit:{type:'boolean'},logoInherit:{type:'boolean'},slotBoundaries:{type:'boolean'},comparisonSelection:{options:['none','all','current']},radiusFamily:{options:['container','control']},guides:{type:'boolean'},marginGuides:{type:'boolean'},gutterGuides:{type:'boolean'},wrapperGuides:{type:'boolean'},centeringGuides:{type:'boolean'},voice:{options:['Helvetica','Georgia','Monospace']},nestedVoice:{options:['Helvetica','Georgia','Monospace']}
};
export const configOf=s=>Object.fromEntries(Object.keys(schema).map(k=>[k,s[k]]));
export function validate(s){
 const checks=Object.entries(schema).map(([key,p])=>({id:key,level:'contract',pass:p.options?p.options.includes(s[key]):p.type?typeof s[key]===p.type:typeof s[key]==='number'&&Number.isFinite(s[key])&&s[key]>=p.min&&s[key]<=p.max&&Number.isInteger(s[key]/p.step),title:key,detail:`${String(s[key])}; expected ${p.options?.join(' / ')??p.type??`${p.min}–${p.max}, step ${p.step}`}`}));
 if(checks.every(c=>c.pass)){try{resolve(s.tier,s.scale,s.size,s.density);checks.push({id:'geometry',level:'contract',pass:true});}catch(e){checks.push({id:'geometry',level:'contract',pass:false,title:'Supported geometry',detail:e.message});}}
 return checks;
}
export function parseConfig(text,defaults){
 const saved=JSON.parse(text);
 if((saved?.v===1||saved?.v===2)&&saved.cfg&&typeof saved.cfg==='object'){saved.v=version;saved.cfg.controlGutter=25;}
 if(!saved||saved.v!==version||!saved.cfg||Array.isArray(saved.cfg)||typeof saved.cfg!=='object')throw Error('Expected a version 3 configuration: { v: 3, cfg: { … } }.');
 const cfg=configOf(defaults),ignored=[];
 for(const [k,v] of Object.entries(saved.cfg)){if(k==='mediaInherit'||k==='compensationGuides')continue;if(!Object.hasOwn(schema,k)||typeof v!==typeof cfg[k]){ignored.push(k);continue;}cfg[k]=v;}
 // Older saves used one Gutters switch for all internal contributions.
 for(const key of ['wrapperGuides','centeringGuides'])if(!Object.hasOwn(saved.cfg,key)&&typeof saved.cfg.gutterGuides==='boolean')cfg[key]=saved.cfg.gutterGuides;
 for(const key of ['avatarInherit','logoInherit'])if(!Object.hasOwn(saved.cfg,key)&&typeof saved.cfg.mediaInherit==='boolean')cfg[key]=saved.cfg.mediaInherit;
 const failures=validate(cfg).filter(c=>!c.pass);if(failures.length)throw Error(failures.map(c=>`${c.title}: ${c.detail}`).join('; '));
 return {cfg,ignored};
}
export const serialize=s=>JSON.stringify({v:version,cfg:configOf(s)},null,2);
export function createInspectorState(root,defaults){
 const panel=root.querySelector('.controls');
 panel.querySelector('h2').insertAdjacentHTML('beforeend','<span class="jig-count">Defaults</span>');
 panel.querySelector('h2').insertAdjacentHTML('afterend','<div class="jig-status" role="status"></div><div class="jig-alert" role="alert" hidden></div>');
 panel.insertAdjacentHTML('beforeend','<details class="inspector-section jig-config"><summary>Configuration <i class="ph ph-caret-right" aria-hidden="true"></i></summary><p class="inspector-hint">Autosaved in this browser. Copy JSON to keep a variant.</p><textarea aria-label="Configuration JSON" spellcheck="false"></textarea><div class="jig-config-actions"><button type="button" data-config="copy">Copy</button><button type="button" data-config="apply">Apply</button></div><p class="jig-save-status" role="status"></p></details>');
 panel.insertAdjacentHTML('beforeend','<details class="inspector-section" id="geometry-issues"><summary>Issues <span class="issue-count"></span></summary><div class="issue-list"></div></details>');
 const issuePanel=panel.querySelector('#geometry-issues');
 const mediaDiagnostics=root.querySelector('#media-diagnostics');if(mediaDiagnostics)issuePanel.append(mediaDiagnostics);
 const status=panel.querySelector('.jig-status'),alert=panel.querySelector('.jig-alert'),textarea=panel.querySelector('textarea'),message=panel.querySelector('.jig-save-status');
 let current=defaults,lastSaved='',dispatch;
 const error=text=>{alert.hidden=!text;alert.textContent=text;};
 let initial=defaults;
 try{const raw=localStorage.getItem(storageKey);if(raw){const saved=JSON.parse(raw);if(saved.v===version||saved.v===1||saved.v===2)initial={...defaults,...parseConfig(raw,defaults).cfg};else message.textContent='Older saved configuration ignored.';}}catch(e){message.textContent='Saved configuration unavailable; using defaults.';}
 panel.querySelector('[data-config=apply]').addEventListener('click',()=>{try{const parsed=parseConfig(textarea.value,defaults);dispatch({type:'configuration',value:parsed.cfg});message.textContent=parsed.ignored.length?'Applied; ignored unknown or mistyped fields: '+parsed.ignored.join(', '):'Configuration applied.';textarea.blur();}catch(e){error(e.message+' Current configuration unchanged.');}});
 panel.querySelector('[data-config=copy]').addEventListener('click',async()=>{const text=serialize(current);try{await navigator.clipboard.writeText(text);message.textContent='Copied.';}catch{textarea.value=text;panel.querySelector('.jig-config').open=true;textarea.focus();textarea.select();message.textContent='Press ⌘C or Ctrl+C to copy the selected JSON.';}});
 return {initial,bind(fn){dispatch=fn;},accept(candidate){const checks=validate(candidate),bad=checks.filter(c=>!c.pass);error(bad.map(c=>`${c.title}: ${c.detail}`).join('; '));return !bad.length;},sync(s){
 current=s;let changed=0;
 for(const k of Object.keys(schema)){const different=s[k]!==defaults[k];if(different)changed++;const input=root.querySelector('#'+k);input?.closest('.field__root')?.classList.toggle('jig-changed',different);const button=root.querySelector(`[data-action="${k==='guides'?'guides':'card-guide'}"][data-key="${k}"]`)??(k==='guides'?root.querySelector('[data-action=guides]'):null);button?.classList.toggle('jig-changed',different);}
 panel.querySelector('.jig-count').textContent=changed?`${changed} changed`:'Defaults';
 if(document.activeElement!==textarea)textarea.value=serialize(s);
 const text=serialize(s);if(text!==lastSaved){try{localStorage.setItem(storageKey,text);lastSaved=text;message.textContent='Saved in this browser.';}catch{message.textContent='Storage unavailable. Use Copy to keep this configuration.';}}
 },properties(){
 const entries=[];
 root.querySelectorAll('[data-radius-conflict="true"],.radius-example[data-conflict="true"],[data-slot-conflict="true"],[data-containment-issues]').forEach(el=>{
  const issues=JSON.parse(el.dataset.containmentIssues||'[]');
  if(el.matches('[data-radius-conflict="true"],[data-slot-conflict="true"],.radius-example[data-conflict="true"]'))issues.push(el.title||el.querySelector('.radius-status')?.textContent||'Geometry conflict');
  if(!issues.length)return;const section=el.closest('section');const density=el.closest('[data-density]')?.dataset.density;
  entries.push({el,section,density,text:[...new Set(issues)].join('; ').replace(/-?\d+\.\d+/g,x=>Number(Number(x).toFixed(2)))});
 });
 status.textContent=entries.length?`Inputs valid · ${entries.length} affected elements`:'Inputs valid · geometry fits';
 issuePanel.querySelector('.issue-count').textContent=String(entries.length);issuePanel.hidden=!entries.length;
 const list=issuePanel.querySelector('.issue-list');list.replaceChildren();
 entries.forEach(({el,section,density,text})=>{const item=document.createElement('div'),link=document.createElement('button'),detail=document.createElement('p');link.type='button';link.textContent=[section?.querySelector('h2')?.textContent||'Example',density].filter(Boolean).join(' · ');link.addEventListener('click',()=>{el.scrollIntoView({block:'center',inline:'center',behavior:'smooth'});el.setAttribute('tabindex','-1');el.focus({preventScroll:true});});detail.textContent=text;item.append(link,detail);list.append(item);});
 },error};
}
