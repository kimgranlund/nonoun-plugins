// Paint geometry only; native or consumer-owned selection and focus stay intact.
function bindListboxBackgrounds(root,{signal}={}) {
 let frame=0,closed=false;
 const refresh=()=>{if(!closed&&!frame)frame=requestAnimationFrame(()=>{frame=0;const s=getComputedStyle(root);for(const edge of ['top','right','bottom','left']){const key=edge[0].toUpperCase()+edge.slice(1),b=parseFloat(s[`border${key}Width`])||parseFloat(s.getPropertyValue('--m-border-thin'))||0,p=parseFloat(s[`padding${key}`])||0;root.style.setProperty(`--listbox-inset-${edge}`,Math.max(0,b-p)+'px');}for(const option of root.querySelectorAll(':scope > [role=option],:scope > .listbox__option'))option.style.setProperty('--listbox-option-radius',getComputedStyle(option).borderTopLeftRadius);});};
 const resize=new ResizeObserver(refresh);resize.observe(root);
 const mutation=new MutationObserver(refresh);mutation.observe(root,{attributes:true,attributeFilter:['data-compact','class'],childList:true});
 root.addEventListener('listboxgeometrychange',refresh);refresh();
 const destroy=()=>{closed=true;cancelAnimationFrame(frame);resize.disconnect();mutation.disconnect();root.removeEventListener('listboxgeometrychange',refresh)};
 if(signal?.aborted)destroy();else signal?.addEventListener('abort',destroy,{once:true});
 return {refresh,destroy};
}
