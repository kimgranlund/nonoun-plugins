// Paint only: the consumer owns aria-pressed and the selected content.
function bindSegmentIndicators(root,{signal}={}) {
 if(CSS.supports('width','anchor-size(width)')&&CSS.supports('anchor-scope','--segment-selected-anchor'))return {mode:'css',refresh(){},destroy(){}};
 let hovered=null,frame=0,closed=false;
 const options=()=>[...root.children].filter(e=>e.matches('button'));
 const selectedOption=()=>options().find(b=>b.getAttribute('aria-pressed')==='true'||b.getAttribute('aria-selected')==='true');
 const paint=(name,button,visible=!!button)=>{
  root.style.setProperty(`--segment-${name}-opacity`,visible?'1':'0');
  if(!button)return;
  const a=root.getBoundingClientRect(),b=button.getBoundingClientRect(),style=getComputedStyle(button);
  // Container padding already protects its outline. Inset either indicator only
  // by the remaining border overlap (compact has zero container padding).
  const container=getComputedStyle(root),inset={};
  for(const edge of ['left','right','top','bottom']){const key=edge[0].toUpperCase()+edge.slice(1);inset[edge]=Math.max(0,(parseFloat(style[`border${key}Width`])||0)-(parseFloat(container[`padding${key}`])||0));}
  for(const [key,value] of Object.entries({x:b.left-a.left+root.scrollLeft+inset.left,y:b.top-a.top+root.scrollTop+inset.top,width:Math.max(0,b.width-inset.left-inset.right),height:Math.max(0,b.height-inset.top-inset.bottom)}))root.style.setProperty(`--segment-${name}-${key}`,value+'px');
  root.style.setProperty(`--segment-${name}-radius`,`max(0px,calc(${style.borderTopLeftRadius} - ${Math.max(inset.top,inset.left)}px))`);
 };
 const update=()=>{frame=0;if(closed)return;const selected=selectedOption(),target=hovered&&hovered!==selected&&!hovered.disabled?hovered:null;paint('selected',selected);paint('hover',target||selected,!!target);root.dataset.indicators='ready';};
 const schedule=()=>{if(!frame&&!closed)frame=requestAnimationFrame(update)};
 const over=e=>{const button=e.target.closest('button'),target=button?.parentElement===root&&!button.disabled&&button!==selectedOption()?button:null;if(target&&!hovered){root.setAttribute('data-hover-seeding','');paint('hover',selectedOption(),false);getComputedStyle(root,'::after').transform;root.removeAttribute('data-hover-seeding');}hovered=target;schedule()};
 const leave=()=>{hovered=null;schedule()};
 root.addEventListener('segmentgeometrychange',schedule);root.addEventListener('pointerover',over);root.addEventListener('pointerleave',leave);
 const resize=new ResizeObserver(schedule);resize.observe(root);options().forEach(b=>resize.observe(b));
 const mutation=new MutationObserver(schedule);mutation.observe(root,{subtree:true,attributes:true,attributeFilter:['aria-pressed','aria-selected','disabled','data-compact'],childList:true,characterData:true});
 const destroy=()=>{closed=true;cancelAnimationFrame(frame);resize.disconnect();mutation.disconnect();root.removeEventListener('segmentgeometrychange',schedule);root.removeEventListener('pointerover',over);root.removeEventListener('pointerleave',leave);delete root.dataset.indicators;};
 if(signal?.aborted)destroy();else{signal?.addEventListener('abort',destroy,{once:true});update();}
 return {refresh:schedule,destroy};
}
