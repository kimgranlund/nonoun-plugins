// Shared review mechanics. The builder copies this unchanged; author review.mjs and preview documents.
export function phosphorIcon(source) {
  const full=source.trim().startsWith('<svg');
  const doc=new DOMParser().parseFromString(full?source:`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">${source}</svg>`,'image/svg+xml');
  if(doc.querySelector('parsererror')||doc.documentElement.localName!=='svg'||
    [...doc.querySelectorAll('path')].some(p=>!/^\s*[Mm]/.test(p.getAttribute('d')||'')))
    throw new Error('Invalid Phosphor SVG: pass the imported asset string directly.');
  const svg=document.importNode(doc.documentElement,true);
  svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
  svg.style.cssText='width:16px;height:16px;flex:none;display:block;fill:currentColor!important;stroke:none!important';
  return svg;
}
export async function loadPhosphorIcon(url) {
  const response=await fetch(url);if(!response.ok)throw new Error(`Icon failed to load: ${url}`);
  return phosphorIcon(await response.text());
}

// Read-only assertion: run after real activation, never instead of it.
export function checkPopupVisibility({trigger, popup, open}) {
  if (!trigger || !popup || typeof open !== 'boolean') throw new Error('Popup smoke needs trigger, popup and expected open boolean');
  const view=popup.ownerDocument.defaultView;
  const rect=popup.getBoundingClientRect();
  let visible=rect.width>0 && rect.height>0;
  for(let node=popup;node;node=node.parentElement){
    const style=view.getComputedStyle(node);
    if(node.hidden || style.display==='none' || style.visibility==='hidden' || style.visibility==='collapse' || Number(style.opacity)===0) visible=false;
  }
  const expanded=trigger.getAttribute('aria-expanded')==='true';
  const inViewport=visible && rect.bottom>0 && rect.right>0 && rect.top<view.innerHeight && rect.left<view.innerWidth;
  if(expanded!==open || visible!==open || (open && !inViewport)) throw new Error(`Popup visibility mismatch: expected=${open}, expanded=${expanded}, visible=${visible}, inViewport=${inViewport}`);
  return {open, expanded, visible, inViewport};
}

// Call after constructing the component, including after asynchronous fixture loading.
export function registerPreview(api) {
  if(!api?.element||typeof api.readState!=='function')throw new Error('registerPreview needs {element, readState}');
  window.componentReview=api;
  document.dispatchEvent(new Event('componentreviewready'));
  return api;
}

// Trusted local previews only. Frame isolation is for CSS, not a security boundary.
async function mountFrame(container, variant, changed) {
  const url=new URL(variant.src,location.href);
  if(url.origin!==location.origin)throw new Error(`${variant.id}: preview must be same-origin`);
  const frame=document.createElement('iframe');frame.title=`${variant.id}: ${variant.name}`;
  if(variant.previewHeight!=null&&(!Number.isFinite(variant.previewHeight)||variant.previewHeight<=0))throw new Error(`${variant.id}: previewHeight must be positive`);
  frame.style.height=variant.previewHeight==null?'1px':`${variant.previewHeight}px`;
  const link=document.createElement('a');link.href=url.href;link.target='_blank';link.rel='noopener';link.textContent='Open standalone';
  container.append(frame,link);
  const api=await new Promise((resolve,reject)=>{
    let doc;
    const cleanup=()=>{clearTimeout(timer);doc?.removeEventListener('componentreviewready',ready)};
    const ready=()=>{const api=frame.contentWindow.componentReview;if(api?.element&&typeof api.readState==='function'){cleanup();resolve(api)}};
    const timer=setTimeout(()=>{cleanup();reject(new Error(`${variant.id}: preview not ready; check local imports and call registerPreview({element, readState})`))},10000);
    frame.onload=()=>{doc=frame.contentDocument;doc.addEventListener('componentreviewready',ready);ready()};
    frame.onerror=()=>{cleanup();reject(new Error(`${variant.id}: preview failed to load`))};frame.src=url.href;
  });
  const doc=frame.contentDocument;
  // previewHeight is a minimum, not a second scrolling viewport.
  const fit=()=>{
    const style=frame.contentWindow.getComputedStyle(doc.body);
    const content=doc.body.getBoundingClientRect().height+parseFloat(style.marginTop)+parseFloat(style.marginBottom);
    const element=api.element, surface=element.getBoundingClientRect();
    // Reserve overlay size, never its viewport-relative offset (which can feed back into frame height).
    const overlay=['absolute','fixed'].includes(frame.contentWindow.getComputedStyle(element).position);
    const height=Math.ceil(Math.max(variant.previewHeight||1,content+(overlay?surface.height:0)));
    if(frame.style.height!==`${height}px`)frame.style.height=`${height}px`;
  };
  new ResizeObserver(fit).observe(doc.body);
  doc.addEventListener('reviewstatechange',()=>queueMicrotask(fit));
  for(const event of ['click','input','change','keydown','close','toggle'])doc.addEventListener(event,()=>requestAnimationFrame(fit),true);
  fit();
  const notify=()=>queueMicrotask(changed);
  for(const event of ['click','input','change','keydown','focusin','focusout','close','toggle','reviewstatechange'])doc.addEventListener(event,notify,true);
  new ResizeObserver(changed).observe(doc.documentElement);
  return {
    get element(){return api.element},readState:()=>api.readState(),
    setTheme(scheme){doc.documentElement.style.colorScheme=scheme;api.setTheme?.(scheme)},
  };
}

export async function initReview(review) {
const $=s=>document.querySelector(s),labels=['Keep','Change','Questions','Part or state'];
const storageKey=`component-variants:${review.id}:r${review.revision}`;
let saved={};try{saved=JSON.parse(localStorage.getItem(storageKey)||'{}')||{}}catch{}
const entries=[],components=new Map();
let combineContext=saved.combineContext||null;
const theme=$('#theme'),systemTheme=matchMedia('(prefers-color-scheme: dark)');
try{theme.value=localStorage.getItem(storageKey+':theme')||'system'}catch{}
if(!['system','light','dark'].includes(theme.value))theme.value='system';
function resolvedScheme(){return theme.value==='system'?(systemTheme.matches?'dark':'light'):theme.value}
function refreshExport(){if(!$('#export').hidden)$('#export').value=exportText()}
function applyTheme(){document.documentElement.style.colorScheme=theme.value==='system'?'light dark':theme.value;for(const c of components.values())c.setTheme?.(resolvedScheme());refreshExport()}
theme.onchange=()=>{try{if(theme.value==='system')localStorage.removeItem(storageKey+':theme');else localStorage.setItem(storageKey+':theme',theme.value)}catch{}applyTheme()};
systemTheme.addEventListener('change',applyTheme);applyTheme();
const text=(tag,value)=>{const el=document.createElement(tag);el.textContent=value;return el};
function context(id){
  const c=id?components.get(id):null;
  return structuredClone({...review.context(),scheme:resolvedScheme(),...(c?{
    componentWidth:Math.round(c.element.getBoundingClientRect().width),state:c.readState()
  }:{})});
}
function save(){try{localStorage.setItem(storageKey,JSON.stringify({preferred:$('[name=preferred]:checked')?.value||'',notes:entries.map(e=>({id:e.id,field:e.field,value:e.input.value,context:e.context})),combine:$('#combine').value,combineContext}))}catch{$('#status').textContent='Storage unavailable; copy feedback before leaving.'}if(!$('#export').hidden)$('#export').value=exportText()}
document.title=review.title;
for(const key of ['title','brief','baseline']){const el=$('#'+key);if(el)el.textContent=review[key]}
for(const v of review.variants){
  const article=document.createElement('article');article.append(text('h2',`${v.id} · ${v.name}`),text('p',v.rationale));
  const mount=document.createElement('div');mount.className='preview';article.append(mount,text('p',v.tradeoff));
  const prefer=document.createElement('label');prefer.className='prefer';const radio=document.createElement('input');radio.type='radio';radio.name='preferred';radio.value=v.id;radio.checked=saved.preferred===v.id;radio.onchange=save;prefer.append(radio,` Prefer ${v.id}`);article.append(prefer);
  const details=document.createElement('details');details.className='feedback';const summary=text('summary','Feedback');details.append(summary);
  const updateCount=()=>{const count=entries.filter(e=>e.id===v.id&&e.input.value.trim()).length;summary.textContent=count?`Feedback · ${count} ${count===1?'note':'notes'}`:'Add feedback'};
  for(const field of labels){
    const label=text('label',field),input=document.createElement('textarea');label.append(input);details.append(label);
    const old=Array.isArray(saved.notes)?saved.notes.find(n=>n?.id===v.id&&n.field===field):null;
    input.value=typeof old?.value==='string'?old.value:'';
    const entry={id:v.id,field,input,context:old?.context||null};entries.push(entry);
    input.oninput=()=>{entry.context=input.value.trim()?context(v.id):null;updateCount();save()};
  }
  updateCount();article.append(details);$('#variants').append(article);const component=v.src?await mountFrame(mount,v,refreshExport):await v.mount(mount);
  if(!component?.element||typeof component.readState!=='function')throw new Error(`${v.id}: mount must return {element, readState}`);
  components.set(v.id,component);component.setTheme?.(resolvedScheme());
}
new ResizeObserver(refreshExport).observe($('#variants'));
$('#variants').addEventListener('click',()=>queueMicrotask(refreshExport));
$('#variants').addEventListener('input',()=>queueMicrotask(refreshExport));
$('#variants').addEventListener('change',()=>queueMicrotask(refreshExport));
$('#combine').value=typeof saved.combine==='string'?saved.combine:'';
$('#combine').oninput=()=>{combineContext=$('#combine').value.trim()?{...context(),variants:Object.fromEntries(review.variants.map(v=>[v.id,context(v.id)]))}:null;save()};
$('#clear').onclick=()=>{document.querySelectorAll('[name=preferred]').forEach(el=>el.checked=false);save()};
function exportText(){
  const preferred=review.variants.find(v=>v.id===$('[name=preferred]:checked')?.value);
  const lines=[`Component: ${review.title}`,`Review: ${review.id} / revision ${review.revision}`,`Baseline: ${review.baseline}`,`Preferred: ${preferred?preferred.id+' ('+preferred.name+')':'None selected'}`];
  for(const v of review.variants){lines.push('',`${v.id} (${v.name})`,`Current context: ${JSON.stringify(context(v.id))}`);for(const e of entries.filter(e=>e.id===v.id&&e.input.value.trim()))lines.push(`${e.field}: ${e.input.value.trim()}`,`Context when note last edited: ${JSON.stringify(e.context)}`)}
  if($('#combine').value.trim())lines.push('',`Combine or other direction: ${$('#combine').value.trim()}`,`Context when direction last edited: ${JSON.stringify(combineContext)}`);
  return lines.join('\n');
}
function show(){const out=$('#export');out.hidden=false;out.value=exportText();out.focus();out.select()}
$('#show').onclick=show;$('#copy').onclick=async()=>{try{await navigator.clipboard.writeText(exportText());$('#status').textContent='Copied. Paste it into the agent session.'}catch{show();$('#status').textContent='Select and copy the feedback text below.'}};
}
