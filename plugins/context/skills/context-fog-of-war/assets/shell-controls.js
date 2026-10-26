let restoreFogInspector=()=>{};
function openFogEvidence(){document.getElementById('report-panel').hidden=true;document.getElementById('report-toggle').setAttribute('aria-expanded','false');const panel=document.getElementById('evidence-panel');panel.hidden=false;document.getElementById('evidence-toggle').setAttribute('aria-expanded','true');restoreFogInspector();}
function setupFogShell(){
 const $=id=>document.getElementById(id);
 const controls=$('controls-panel'),controlsToggle=$('controls-toggle');
 controlsToggle.onclick=()=>{controls.hidden=!controls.hidden;controlsToggle.setAttribute('aria-expanded',String(!controls.hidden));positionFogControls();};
 controls.addEventListener('keydown',e=>{if(e.key==='Escape'){e.stopPropagation();controls.hidden=true;controlsToggle.setAttribute('aria-expanded','false');controlsToggle.focus();}});
 for(const name of ['evidence','report']){const panel=$(name+'-panel'),toggle=$(name+'-toggle'),close=$(name+'-close');toggle.onclick=()=>{panel.hidden=!panel.hidden;toggle.setAttribute('aria-expanded',String(!panel.hidden));if(name==='evidence'&&!panel.hidden)restoreFogInspector();};close.onclick=()=>{panel.hidden=true;toggle.setAttribute('aria-expanded','false');(toggle.getClientRects().length?toggle:$('controls-toggle')).focus();};panel.addEventListener('keydown',e=>{if(e.key==='Escape'){e.stopPropagation();close.click();}});}
 $('timeline').addEventListener('click',openFogEvidence);$('map').addEventListener('click',openFogEvidence);
}
setupFogShell();

function positionFogControls(){
 const bar=document.querySelector('.canvas-toolbar'),panel=document.getElementById('controls-panel');if(panel.hidden)return;
 const r=bar.getBoundingClientRect(),gap=8,w=panel.offsetWidth,h=panel.offsetHeight;
 panel.style.left=Math.max(gap,Math.min(r.left,innerWidth-w-gap))+'px';
 const below=r.bottom+gap;
 panel.style.top=Math.max(gap,Math.min(below+h<=innerHeight?below:r.top-h-gap,innerHeight-h-gap))+'px';
}
function setupFogDragging(){
 const key='context-fog-floating:v1:'+location.pathname;let saved={};
 try{saved=JSON.parse(localStorage.getItem(key)||'{}')||{};}catch{}
 const items=[];const persist=()=>{try{localStorage.setItem(key,JSON.stringify(saved));}catch{}};
 for(const handle of document.querySelectorAll('[data-drag]')){
  const name=handle.dataset.drag,el=handle;
  function place(x,y,remember=false){const r=el.getBoundingClientRect(),gap=8;x=Math.max(gap,Math.min(x,innerWidth-r.width-gap));y=Math.max(gap,Math.min(y,innerHeight-r.height-gap));Object.assign(el.style,{left:x+'px',top:y+'px',right:'auto',bottom:'auto',transform:'none'});if(remember){saved[name]={x,y};persist();}positionFogControls();}
  function restore(){const value=saved[name];if(value&&Number.isFinite(value.x)&&Number.isFinite(value.y))place(value.x,value.y);else positionFogControls();}
  let drag=null;
  handle.addEventListener('pointerdown',e=>{if(e.button!==0||e.target.closest('button,input,select,textarea,a,summary')&&e.target!==handle)return;e.preventDefault();e.stopPropagation();const r=el.getBoundingClientRect();drag={id:e.pointerId,x:e.clientX,y:e.clientY,left:r.left,top:r.top};handle.setPointerCapture(e.pointerId);el.classList.add('dragging');});
  handle.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;place(drag.left+e.clientX-drag.x,drag.top+e.clientY-drag.y);});
  const finish=e=>{if(!drag||drag.id!==e.pointerId)return;const r=el.getBoundingClientRect();place(r.left,r.top,true);drag=null;el.classList.remove('dragging');if(handle.hasPointerCapture(e.pointerId))handle.releasePointerCapture(e.pointerId);};
  handle.addEventListener('pointerup',finish);handle.addEventListener('pointercancel',finish);handle.addEventListener('lostpointercapture',finish);
  handle.addEventListener('keydown',e=>{if(e.target!==handle)return;const offsets={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};if(e.key==='Home'){e.preventDefault();delete saved[name];persist();for(const k of ['left','top','right','bottom','transform'])el.style[k]='';positionFogControls();}else if(offsets[e.key]){e.preventDefault();const r=el.getBoundingClientRect(),step=e.shiftKey?32:8,[x,y]=offsets[e.key];place(r.left+x*step,r.top+y*step,true);}});
  items.push(restore);restore();new ResizeObserver(restore).observe(el);
 }
 addEventListener('resize',()=>items.forEach(restore));
}
setupFogDragging();

function setupFogInspector(){
 const panel=document.getElementById('evidence-panel'),key='context-fog-inspector:v1:'+location.pathname;let saved=null;
 try{saved=JSON.parse(localStorage.getItem(key)||'null');}catch{}
 function apply(box,save=false){
  const gap=8,w=Math.max(Math.min(280,innerWidth-16),Math.min(box.width,innerWidth-16)),h=Math.max(Math.min(220,innerHeight-16),Math.min(box.height,innerHeight-16));
  const x=Math.max(gap,Math.min(box.x,innerWidth-w-gap)),y=Math.max(gap,Math.min(box.y,innerHeight-h-gap));
  Object.assign(panel.style,{left:x+'px',top:y+'px',right:'auto',bottom:'auto',width:w+'px',height:h+'px'});
  if(save){saved={x,y,width:w,height:h};try{localStorage.setItem(key,JSON.stringify(saved));}catch{}}
 }
 restoreFogInspector=()=>{if(!panel.hidden&&saved&&['x','y','width','height'].every(k=>Number.isFinite(saved[k])))apply(saved);};
 function reset(){saved=null;try{localStorage.removeItem(key);}catch{}for(const k of ['left','top','right','bottom','width','height'])panel.style[k]='';}
 for(const [id,resize] of [['evidence-move',false],['evidence-resize',true]]){
  const handle=document.getElementById(id);let drag=null;
  handle.addEventListener('pointerdown',e=>{if(e.button!==0||e.target.closest('button,input,select,textarea,a,summary')&&e.target!==handle)return;e.preventDefault();e.stopPropagation();const r=panel.getBoundingClientRect();drag={id:e.pointerId,x:e.clientX,y:e.clientY,box:{x:r.x,y:r.y,width:r.width,height:r.height}};handle.setPointerCapture(e.pointerId);});
  handle.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y,b=drag.box;apply(resize?{...b,width:b.width+dx,height:b.height+dy}:{...b,x:b.x+dx,y:b.y+dy});});
  const finish=e=>{if(!drag||e.pointerId!==drag.id)return;const r=panel.getBoundingClientRect();apply({x:r.x,y:r.y,width:r.width,height:r.height},true);drag=null;if(handle.hasPointerCapture(e.pointerId))handle.releasePointerCapture(e.pointerId);};
  for(const event of ['pointerup','pointercancel','lostpointercapture'])handle.addEventListener(event,finish);
  handle.addEventListener('keydown',e=>{if(e.target!==handle)return;const dirs={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};if(e.key==='Home'){e.preventDefault();reset();}else if(dirs[e.key]){e.preventDefault();const [dx,dy]=dirs[e.key],step=e.shiftKey?32:8,r=panel.getBoundingClientRect();apply({x:r.x+(resize?0:dx*step),y:r.y+(resize?0:dy*step),width:r.width+(resize?dx*step:0),height:r.height+(resize?dy*step:0)},true);}});
 }
 addEventListener('resize',restoreFogInspector);restoreFogInspector();
}
setupFogInspector();
