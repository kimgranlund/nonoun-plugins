// Measured, non-layout overlays. Rectangles occupy empty space only.
export function paintSpacingGuides(root){
 installGuideReadout(root);
 guideReadout.hidden=true;
 root.querySelectorAll('.content-spacing-overlay').forEach(el=>el.remove());
 const box=el=>el.getBoundingClientRect();
 const jobs=[];
 root.querySelectorAll('.specimen .listbox__option[data-voice],.specimen .button__root,.specimen [role=menuitem],.spacing-demo[data-rule=composed]').forEach(row=>{
  const slots=[...row.querySelectorAll(':scope > [data-slot]')];
  // Bare-text buttons have no slot wrapper; measure their text without adding one.
  const rects=slots.length?slots.map(box):[...row.childNodes].filter(node=>node.nodeType===Node.TEXT_NODE&&node.textContent.trim()).flatMap(node=>{const range=document.createRange();range.selectNodeContents(node);return [...range.getClientRects()];});
  jobs.push({el:row,rects,slots});
 });
 root.querySelectorAll('.specimen .table__root th,.specimen .table__root td,.specimen .data-list__root dt,.specimen .data-list__root dd').forEach(el=>{
  const slot=el.querySelector(':scope > .data-cell-slot');if(slot){jobs.push({el,rects:[box(slot)]});return;}
  const b=box(el),s=getComputedStyle(el);
  const left=b.left+(parseFloat(s.paddingLeft)||0)+(parseFloat(s.borderLeftWidth)||0),right=b.right-(parseFloat(s.paddingRight)||0)-(parseFloat(s.borderRightWidth)||0),top=b.top+(parseFloat(s.paddingTop)||0)+(parseFloat(s.borderTopWidth)||0),bottom=b.bottom-(parseFloat(s.paddingBottom)||0)-(parseFloat(s.borderBottomWidth)||0);
  jobs.push({el,rects:[{left,right,top,bottom,width:right-left,height:bottom-top}]});
 });
 root.querySelectorAll('.specimen .data-list__root > div').forEach(el=>jobs.push({el,rects:[...el.children].map(box)}));
 // Batch layout reads before inserting overlays.
 const measured=jobs.map(job=>({...job,bounds:box(job.el),borderLeft:job.el.clientLeft,borderTop:job.el.clientTop,slotPads:(job.slots??[]).map(el=>{
  const css=getComputedStyle(el),art=el.matches('[data-slot=icon],[data-slot=glyph]')?el.querySelector('.ph,svg,img'):null;
  const base=el.matches('[data-slot=media]')?0:el.matches('[data-slot=label]')?parseFloat(css.getPropertyValue('--surface-inner'))/6:parseFloat(css.getPropertyValue('--slot-padding').trim()||css.getPropertyValue('--wrapper-gutter'))||0;
  return {radius:parseFloat(css.borderTopLeftRadius)||0,box:box(el),left:art?base:parseFloat(css.paddingLeft)||0,right:art?base:parseFloat(css.paddingRight)||0,base,art:art?box(art):null};
 })}));
 let clipIndex=0;
 for(const {el,rects,bounds:b,borderLeft,borderTop,slotPads} of measured){
  if(!rects.length||b.width<=0||b.height<=0)continue;
  const left=Math.max(0,Math.min(...rects.map(r=>r.left))-b.left),right=Math.min(b.width,Math.max(...rects.map(r=>r.right))-b.left);
  const top=Math.max(0,Math.min(...rects.map(r=>r.top))-b.top),bottom=Math.min(b.height,Math.max(...rects.map(r=>r.bottom))-b.top);
  const rect=(x,y,w,h,kind,space=kind)=>w>0.01&&h>0.01?`<rect data-guide="${kind}" data-space="${space}" x="${x}" y="${y}" width="${w}" height="${h}" fill="${space==='slot-padding'?'#acd4ee':space==='centering'?'#b8dec7':kind==='margin'?'#f1cac0':'#d6d6cc'}"/>`:'';
  let marks=rect(0,0,b.width,top,'margin')+rect(0,bottom,b.width,b.height-bottom,'margin')+rect(0,top,left,bottom-top,'margin')+rect(right,top,b.width-right,bottom-top,'margin');
  const orderedRects=[...rects].sort((a,b)=>a.left-b.left);
  orderedRects.slice(1).forEach((r,i)=>{const previous=orderedRects[i];marks+=rect(previous.right-b.left,top,r.left-previous.right,bottom-top,'gutter');});
  for(const pad of slotPads){
   const id='slot-guide-clip-'+clipIndex++,r=Math.min(pad.radius,pad.box.width/2,pad.box.height/2);
   let slotMarks='';for(const region of slotGuideRegions(pad))slotMarks+=rect(region.x-b.left,region.y-b.top,region.width,region.height,'gutter',region.space);
   marks+=`<defs><clipPath id="${id}"><rect x="${pad.box.left-b.left}" y="${pad.box.top-b.top}" width="${pad.box.width}" height="${pad.box.height}" rx="${r}"/></clipPath></defs><g clip-path="url(#${id})" data-slot-clip="${pad.box.left-b.left},${pad.box.top-b.top},${pad.box.width},${pad.box.height},${r}">${slotMarks}</g>`;
  }
  el.insertAdjacentHTML('beforeend',`<svg class="content-spacing-overlay" width="${b.width}" height="${b.height}" viewBox="0 0 ${b.width} ${b.height}" style="left:${-borderLeft}px;top:${-borderTop}px" aria-hidden="true">${marks}</svg>`);
 }
}

let guideReadout;
function installGuideReadout(root){
 if(guideReadout)return;
 guideReadout=document.createElement('div');guideReadout.className='guide-readout';guideReadout.hidden=true;document.body.append(guideReadout);
 const hide=()=>{guideReadout.hidden=true;};
 document.addEventListener('pointermove',e=>{
  const lab=root.querySelector('#lab');if(!lab.classList.contains('guides')){hide();return;}
  let text='';const f=v=>Number(v.toFixed(2));
  for(const rect of lab.querySelectorAll('svg rect[data-guide]')){
   if(getComputedStyle(rect).display==='none')continue;
   const b=rect.getBoundingClientRect();
   const group=rect.closest('[data-slot-clip]');
   if(group){const [x,y,w,h,r]=group.dataset.slotClip.split(',').map(Number),svg=rect.ownerSVGElement,pt=new DOMPoint(e.clientX,e.clientY).matrixTransform(svg.getScreenCTM().inverse()),cx=Math.max(x+r,Math.min(pt.x,x+w-r)),cy=Math.max(y+r,Math.min(pt.y,y+h-r));if(pt.x<x||pt.x>x+w||pt.y<y||pt.y>y+h||Math.hypot(pt.x-cx,pt.y-cy)>r+.01)continue;}
   if(b.width>0&&b.height>0&&e.clientX>=b.left&&e.clientX<=b.right&&e.clientY>=b.top&&e.clientY<=b.bottom){text=`${({ 'slot-padding':'Wrapper padding',centering:'Extra centering' }[rect.dataset.space]??(rect.dataset.guide==='margin'?'Margin':'Gap'))} · ${f(b.width)} × ${f(b.height)} px`;break;}
  }
  if(!text){const demo=e.target.closest('.tier-demo,.spacing-demo');if(demo){const b=demo.getBoundingClientRect(),boxes=[...demo.children].filter(el=>el.matches('span')).map(el=>el.getBoundingClientRect());const inside=boxes.some(r=>e.clientX>=r.left&&e.clientX<=r.right&&e.clientY>=r.top&&e.clientY<=r.bottom);if(!inside&&boxes.length){const left=Math.min(...boxes.map(r=>r.left)),right=Math.max(...boxes.map(r=>r.right)),top=Math.min(...boxes.map(r=>r.top)),bottom=Math.max(...boxes.map(r=>r.bottom));const margin=e.clientX<left||e.clientX>right||e.clientY<top||e.clientY>bottom;if(!lab.classList.contains(margin?'hide-margins':'hide-gutters')){const value=margin?(e.clientX<left?left-b.left:e.clientX>right?b.right-right:e.clientY<top?top-b.top:b.bottom-bottom):parseFloat(getComputedStyle(demo).columnGap);text=`${margin?'Margin':'Gutter'} · ${f(value)} px`;}}}}
  if(!text){hide();return;}
  guideReadout.textContent=text;guideReadout.hidden=false;guideReadout.style.left=Math.max(8,Math.min(e.clientX+12,innerWidth-230))+'px';guideReadout.style.top=Math.max(8,Math.min(e.clientY+16,innerHeight-40))+'px';
 });
 document.addEventListener('scroll',hide,true);document.addEventListener('pointerout',e=>{if(!e.relatedTarget)hide();});
}

// Partition only empty wrapper space; regions never overlap the artwork box.
export function slotGuideRegions({box:b,left,right,base,art}){
 const out=[],add=(x,y,width,height,space)=>{if(width>.01&&height>.01)out.push({x,y,width,height,space});};
 const l=art?Math.max(0,Math.min(left,art.left-b.left)):left;
 const r=art?Math.max(0,Math.min(right,b.right-art.right)):right;
 const bl=Math.min(l,base),br=Math.min(r,base);
 // Only declared wrapper padding is painted; retired compensation adds no region.
 add(b.left,b.top,bl,b.height,'slot-padding');add(b.right-br,b.top,br,b.height,'slot-padding');
 if(art){
  const x=b.left+l,end=b.right-r,top=Math.max(b.top,art.top),bottom=Math.min(b.bottom,art.bottom);
  add(x,b.top,end-x,top-b.top,'centering');add(x,bottom,end-x,b.bottom-bottom,'centering');
  add(x,top,Math.min(end,art.left)-x,bottom-top,'centering');
  add(Math.max(x,art.right),top,end-Math.max(x,art.right),bottom-top,'centering');
 }
 return out;
}
