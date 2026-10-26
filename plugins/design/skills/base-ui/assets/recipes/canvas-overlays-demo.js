const canvas=document.querySelector('#canvas'),scene=canvas.querySelector('[data-canvas-scene]'),inspector=canvas.querySelector('.canvas-inspector');
if(canvas.clientWidth<600)inspector.hidden=true;
const host=createCanvasOverlayHost(canvas,scene);
const layout=createCanvasOverlayLayout(canvas,host,{inspector,controls:canvas.querySelector('.canvas-tools'),player:canvas.querySelector('.canvas-player')});
let selected='source',timer=null;
const ids=['source','problem','outcome'],descriptions={source:'Signal: a source return is recorded. It does not establish understanding.',problem:'Problem: output was truncated. Inspect the missing range before drawing a conclusion.',outcome:'Verified outcome: this named fixture passed. It does not certify the entire application.'};
function select(id){selected=id;host.select(id);document.querySelector('#canvas-detail').textContent=descriptions[id];document.querySelector('#canvas-step').textContent=(ids.indexOf(id)+1)+' / 3';}
const runtime=createUIRuntime();runtime.mount({root:canvas,stateKey:'canvas-overlays',definition:{reduce:s=>s,render(){},bind({onAction}){
 onAction('options',(_,b)=>{const p=document.querySelector('#canvas-options');p.hidden=!p.hidden;b.setAttribute('aria-expanded',String(!p.hidden));});
 onAction('select',(_,b)=>select(b.dataset.canvasNode));onAction('in',()=>host.zoom(1.2));onAction('out',()=>host.zoom(1/1.2));
 onAction('inspect',()=>{inspector.hidden=false;layout.update();});onAction('close',()=>{inspector.hidden=true;layout.update();canvas.querySelector('[data-action=inspect]').focus();});
 onAction('fit',()=>{const n=[...scene.children].find(n=>n.dataset.canvasNode===selected);const ok=host.fit({x:n.offsetLeft,y:n.offsetTop,width:n.offsetWidth,height:n.offsetHeight});document.querySelector('#canvas-status').textContent=ok?'':'Close or move an overlay to make room, then fit again.';});
 onAction('reflow',()=>{[...scene.children].forEach((n,i)=>{n.style.left=(64+i*240)+'px';n.style.top=(200+i*80)+'px';});});
 onAction('play',(_,b)=>{if(timer){clearInterval(timer);timer=null;b.textContent='Play';}else{b.textContent='Pause';timer=setInterval(()=>select(ids[(ids.indexOf(selected)+1)%3]),1000);}});
}}});
canvas.querySelector('.canvas-player input').addEventListener('input',e=>select(ids[+e.target.value]));
for(const axis of ['width','height'])document.querySelector('#panel-'+axis).addEventListener('input',e=>host.resize(inspector,axis==='width'?+e.target.value:inspector.offsetWidth,axis==='height'?+e.target.value:inspector.offsetHeight));
canvas.querySelector('#canvas-search').addEventListener('input',e=>{for(const n of scene.children)n.style.opacity=!e.target.value||n.textContent.toLowerCase().includes(e.target.value.toLowerCase())?'1':'.35';});
window.canvasOverlayDemo={host,layout,select};

