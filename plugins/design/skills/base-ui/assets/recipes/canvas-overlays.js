/* Optional nonmodal canvas host. No graph layout, evidence inference or automatic fitting. */
function createCanvasOverlayHost(root, scene) {
  const panels=[...root.querySelectorAll('[data-canvas-panel]')], camera={x:0,y:0,scale:1};
  const controller=new AbortController(), signal=controller.signal;
  const unit=()=>{const p=document.createElement('i');p.style.width='var(--g-margin)';p.style.position='absolute';root.append(p);const u=p.getBoundingClientRect().width;p.remove();return u;};
  function paint(){scene.style.transform=`translate(${camera.x}px,${camera.y}px) scale(${camera.scale})`;}
  function clamp(panel){const u=unit(),w=root.clientWidth,h=root.clientHeight,reserve=Math.max(0,Number(panel.dataset.canvasReserveBottom)||0);panel.style.maxWidth=Math.max(1,w-2*u)+'px';panel.style.maxHeight=Math.max(1,h-2*u-reserve)+'px';const r=panel.getBoundingClientRect(),host=root.getBoundingClientRect();panel.style.left=Math.max(u,Math.min(r.left-host.left,w-r.width-u))+'px';panel.style.top=Math.max(u,Math.min(r.top-host.top,h-r.height-u-reserve))+'px';panel.style.right='auto';panel.style.bottom='auto';}
  function textAt(panel,x,y){const walker=document.createTreeWalker(panel,NodeFilter.SHOW_TEXT);let n;while(n=walker.nextNode()){if(!n.textContent.trim())continue;const range=document.createRange();range.selectNodeContents(n);if([...range.getClientRects()].some(r=>x>=r.left&&x<=r.right&&y>=r.top&&y<=r.bottom))return true;}return false;}
  function drag(e,panel){if(e.button!==0||e.target.closest('button,input,select,textarea,a,summary,[contenteditable],[data-no-drag]')||textAt(panel||scene,e.clientX,e.clientY))return;
    const start={x:e.clientX,y:e.clientY},r=(panel||root).getBoundingClientRect(),h=root.getBoundingClientRect(),old={...camera};let moved=false;
    e.preventDefault();e.target.setPointerCapture(e.pointerId);
    const move=ev=>{if(ev.pointerId!==e.pointerId)return;const dx=ev.clientX-start.x,dy=ev.clientY-start.y;if(Math.hypot(dx,dy)<4&&!moved)return;moved=true;if(panel){panel.style.left=r.left-h.left+dx+'px';panel.style.top=r.top-h.top+dy+'px';clamp(panel);}else{camera.x=old.x+dx;camera.y=old.y+dy;paint();}};
    const end=()=>{e.target.removeEventListener('pointermove',move);e.target.removeEventListener('pointerup',end);e.target.removeEventListener('pointercancel',end);};
    e.target.addEventListener('pointermove',move);e.target.addEventListener('pointerup',end);e.target.addEventListener('pointercancel',end);
  }
  root.addEventListener('pointerdown',e=>{const panel=e.target.closest('[data-canvas-panel]');if(panel)drag(e,panel);else if(e.target===root||e.target===scene)drag(e,null);},{signal});
  for(const panel of panels){panel.addEventListener('keydown',e=>{if(e.target!==panel||!e.altKey||!e.key.startsWith('Arrow'))return;e.preventDefault();const r=panel.getBoundingClientRect(),h=root.getBoundingClientRect(),u=unit();panel.style.left=r.left-h.left+(e.key==='ArrowLeft'?-u:e.key==='ArrowRight'?u:0)+'px';panel.style.top=r.top-h.top+(e.key==='ArrowUp'?-u:e.key==='ArrowDown'?u:0)+'px';clamp(panel);},{signal});}
  const observer=new ResizeObserver(()=>panels.filter(p=>!p.hidden).forEach(clamp));observer.observe(root);panels.forEach(p=>observer.observe(p));
  function freeRect(){const u=unit(),h=root.getBoundingClientRect(),boxes=panels.filter(p=>!p.hidden).map(p=>{const r=p.getBoundingClientRect();return {l:r.left-h.left-u,r:r.right-h.left+u,t:r.top-h.top-u,b:r.bottom-h.top+u};});const xs=[u,root.clientWidth-u,...boxes.flatMap(b=>[Math.max(u,b.l),Math.min(root.clientWidth-u,b.r)])],ys=[u,root.clientHeight-u,...boxes.flatMap(b=>[Math.max(u,b.t),Math.min(root.clientHeight-u,b.b)])];let best={x:u,y:u,width:0,height:0};for(const l of xs)for(const r of xs)for(const t of ys)for(const b of ys){if(r<=l||b<=t||boxes.some(q=>q.l<r&&q.r>l&&q.t<b&&q.b>t))continue;if((r-l)*(b-t)>best.width*best.height)best={x:l,y:t,width:r-l,height:b-t};}return best;}
  return {camera,freeRect,clamp,
    select(id){root.querySelectorAll('[data-canvas-node]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.canvasNode===id)));},
    zoom(factor){const x=root.clientWidth/2,y=root.clientHeight/2,s=Math.max(.25,Math.min(3,camera.scale*factor));camera.x=x-(x-camera.x)*s/camera.scale;camera.y=y-(y-camera.y)*s/camera.scale;camera.scale=s;paint();},
    fit(rect){const area=freeRect(),u=unit();if(area.width<8*u||area.height<8*u)return false;const s=Math.min(1,(area.width-2*u)/rect.width,(area.height-2*u)/rect.height);camera.scale=s;camera.x=area.x+(area.width-rect.width*s)/2-rect.x*s;camera.y=area.y+(area.height-rect.height*s)/2-rect.y*s;paint();return true;},
    resize(panel,width,height){panel.style.width=Math.max(12*unit(),width)+'px';panel.style.height=Math.max(8*unit(),height)+'px';clamp(panel);},
    destroy(){observer.disconnect();controller.abort();}
  };
}

/* Three-panel workspace policy: reserve playback space; use an exclusive inspector
   when its measured rectangle intersects controls. Does not move the camera. */
function createCanvasOverlayLayout(root, host, {inspector, controls, player}) {
  const peers=[controls,player],suppressed=new Set(),controller=new AbortController();
  let updating=false;
  function update(){
    if(updating)return;updating=true;
    try{
      for(const p of suppressed)p.hidden=false;
      suppressed.clear();
      controls.dataset.canvasReserveBottom='0';
      for(const p of peers)if(!p.hidden)host.clamp(p);
      if(!controls.hidden&&!player.hidden){
        const c=controls.getBoundingClientRect(),p=player.getBoundingClientRect(),r=root.getBoundingClientRect();
        // Reserve the actual player position, not just its height after a drag.
        if(c.left<p.right&&c.right>p.left&&p.top>c.top){
          controls.dataset.canvasReserveBottom=String(Math.max(0,r.bottom-p.top));host.clamp(controls);
        }
      }
      if(!inspector.hidden){
        host.clamp(inspector);const a=inspector.getBoundingClientRect();
        const collision=peers.some(p=>{if(p.hidden)return false;const b=p.getBoundingClientRect();return a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top});
        if(collision){const restoreFocus=peers.some(p=>p.contains(document.activeElement));for(const p of peers)if(!p.hidden){p.hidden=true;suppressed.add(p)}
          if(restoreFocus)inspector.focus({preventScroll:true});
        }
      }
      root.dataset.canvasExclusive=String(suppressed.size>0);
    }finally{updating=false}
  }
  const observer=new ResizeObserver(update);[root,inspector,...peers].forEach(p=>observer.observe(p));
  root.addEventListener('pointerup',update,{signal:controller.signal});
  root.addEventListener('keyup',update,{signal:controller.signal});
  update();
  return {update,destroy(){observer.disconnect();controller.abort();for(const p of suppressed)p.hidden=false;suppressed.clear();delete root.dataset.canvasExclusive;}};
}
