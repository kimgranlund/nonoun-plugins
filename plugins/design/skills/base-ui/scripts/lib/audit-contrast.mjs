/** Serializable browser audit. Measures solid-background rendered text, not full WCAG conformance. */
export function auditContrast({rootSelector='body',boundarySelectors=[]}={}) {
  const root=document.querySelector(rootSelector);
  const result={version:1,scope:'Rendered text in the current DOM/state; excludes native popup menus, icon graphics and focus indicators; models maintained fully covering translated segmented indicators and isolated inset listbox backgrounds, but not other overlapping sibling paint or image pixels. Control edges are measured only for explicitly supplied boundarySelectors. Repeat after state/theme changes.',status:'pass',measurements:[],boundaryMeasurements:[],failures:[],unsupported:[],excluded:[]};
  if(!root)return {...result,status:'incomplete',summary:{status:'incomplete',measured:0,boundaries:0,failed:0,unsupported:1,excluded:0},unsupported:[{reason:'Root selector did not match',selector:rootSelector}]};
  const canvas=document.createElement('canvas');canvas.width=canvas.height=1;
  const ctx=canvas.getContext('2d',{willReadFrequently:true});
  const rgba=color=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data].map((v,i)=>i===3?v/255:v);};
  const over=(a,b)=>{const alpha=a[3]+b[3]*(1-a[3]);return [0,1,2].map(i=>alpha?(a[i]*a[3]+b[i]*b[3]*(1-a[3]))/alpha:0).concat(alpha);};
  const lum=a=>a.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
  const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
  const identify=e=>e.id?'#'+e.id:e.tagName.toLowerCase()+(e.classList.length?'.'+[...e.classList].join('.'): '');
  const system=document.createElement('span');system.style.cssText='background:Canvas;display:none';root.append(system);const canvasColor=rgba(getComputedStyle(system).backgroundColor);system.remove();
  const candidates=[];
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()){
    const node=walker.currentNode,e=node.parentElement;
    if(!node.textContent.trim()||!e||e.closest('script,style,template,option,textarea,svg'))continue;
    const range=document.createRange();range.selectNodeContents(node);
    const rects=[...range.getClientRects()].filter(r=>r.width>0&&r.height>0);
    if(rects.length)candidates.push({e,text:node.textContent.trim().slice(0,160),rects});
  }
  for(const e of root.querySelectorAll('input,select,textarea')){
    if(e.matches('input[type=hidden],input[type=checkbox],input[type=radio],input[type=range],input[type=color],input[type=file]'))continue;
    const rect=e.getBoundingClientRect();if(!rect.width||!rect.height)continue;
    const placeholder=!e.value&&!!e.placeholder;
    const text=e.tagName==='SELECT'?e.selectedOptions[0]?.textContent:(e.value||e.placeholder);
    if(text)candidates.push({e,text:String(text).slice(0,160),placeholder,rects:[rect]});
  }
  for(const {e,text,placeholder,rects} of candidates){
    const base=getComputedStyle(e), cs=placeholder?getComputedStyle(e,'::placeholder'):base;
    const record={selector:identify(e),text,kind:placeholder?'placeholder':'text'};
    if(base.visibility!=='visible'||base.display==='none'||(e.checkVisibility&&!e.checkVisibility({contentVisibilityAuto:true,visibilityProperty:true})))continue;
    let closed=false;for(let a=e;a;a=a.parentElement)if(a.tagName==='DETAILS'&&!a.open&&!a.querySelector(':scope > summary')?.contains(e)){closed=true;break;}if(closed)continue;
    if(e.closest('[disabled],[aria-disabled="true"],fieldset:disabled')){result.excluded.push({...record,reason:'Inactive control: contrast exemption; not certified'});continue;}
    let reasons=[],layers=[],opaque=false,clipped=false;
    for(let a=e;a;a=a.parentElement){
      const s=getComputedStyle(a),r=a.getBoundingClientRect();
      if(s.visibility!=='visible'||Number(s.opacity)===0){clipped=true;break;}
      if(a!==e&&/(hidden|clip|scroll|auto)/.test(s.overflowX+' '+s.overflowY)&&rects.every(t=>t.right<=r.left||t.left>=r.right||t.bottom<=r.top||t.top>=r.bottom)){clipped=true;break;}
      if(Number(s.opacity)!==1)reasons.push('Ancestor/element opacity requires group compositing');
      if(s.filter!=='none'||s.backdropFilter&&s.backdropFilter!=='none'||s.mixBlendMode!=='normal')reasons.push('Filter or blend effect');
      // Maintained segmented indicators sit behind the direct buttons, after their
      // ancestor background. Resolve actual translated paint, not selection tokens.
      if(!opaque&&a.matches('.segments__root[data-indicators=ready]'))for(const pseudo of ['::before','::after']){
        if(opaque)break;
        const p=getComputedStyle(a,pseudo),alpha=Number(p.opacity);
        if(!alpha||p.display==='none'||p.content==='none')continue;
        const m=new DOMMatrixReadOnly(p.transform==='none'?undefined:p.transform);
        if(!m.is2D||m.a!==1||m.b!==0||m.c!==0||m.d!==1||p.backgroundImage!=='none'||p.filter!=='none'){reasons.push('Unsupported segmented indicator transform/paint');continue;}
        const x=r.left+parseFloat(p.left)+m.e-a.scrollLeft,y=r.top+parseFloat(p.top)+m.f-a.scrollTop,w=parseFloat(p.width),h=parseFloat(p.height);
        const intersects=rects.some(t=>t.right>x&&t.left<x+w&&t.bottom>y&&t.top<y+h);
        if(!intersects)continue;
        if(!rects.every(t=>t.left>=x-.5&&t.right<=x+w+.5&&t.top>=y-.5&&t.bottom<=y+h+.5)){reasons.push('Partially overlapping segmented indicator requires pixel verification');continue;}
        const layer=rgba(p.backgroundColor);layer[3]*=alpha;layers.push(layer);if(layer[3]===1)opaque=true;
      }
      // Isolated listbox paint is behind the option text, above its transparent
      // background. Measure the actual inset layer rather than assuming a fill.
      if(!opaque&&a.matches('.combobox__list > [role=option],.listbox__root > .listbox__option')&&s.isolation==='isolate'){
        const p=getComputedStyle(a,'::before'),alpha=Number(p.opacity),x=r.left+(parseFloat(s.borderLeftWidth)||0)+(parseFloat(p.left)||0),y=r.top+(parseFloat(s.borderTopWidth)||0)+(parseFloat(p.top)||0),w=parseFloat(p.width),h=parseFloat(p.height);
        if(p.content!=='none'&&alpha&&p.display!=='none'){
          if(p.backgroundImage!=='none'||p.transform!=='none'||p.filter!=='none')reasons.push('Unsupported listbox background paint');
          else {
            // Range boxes include text clipped by single-line text slots. Only
            // their visible intersection contributes pixels to contrast.
            let visible=rects.map(t=>({left:t.left,right:t.right,top:t.top,bottom:t.bottom}));
            for(let clip=e;clip&&clip!==a;clip=clip.parentElement){const cs=getComputedStyle(clip),b=clip.getBoundingClientRect();visible=visible.map(t=>({left:/(hidden|clip|auto|scroll)/.test(cs.overflowX)?Math.max(t.left,b.left+clip.clientLeft):t.left,right:/(hidden|clip|auto|scroll)/.test(cs.overflowX)?Math.min(t.right,b.left+clip.clientLeft+clip.clientWidth):t.right,top:/(hidden|clip|auto|scroll)/.test(cs.overflowY)?Math.max(t.top,b.top+clip.clientTop):t.top,bottom:/(hidden|clip|auto|scroll)/.test(cs.overflowY)?Math.min(t.bottom,b.top+clip.clientTop+clip.clientHeight):t.bottom}));}
            visible=visible.filter(t=>t.right>t.left&&t.bottom>t.top);
            if(visible.length&&visible.every(t=>t.left>=x-.5&&t.right<=x+w+.5&&t.top>=y-.5&&t.bottom<=y+h+.5)){const layer=rgba(p.backgroundColor);layer[3]*=alpha;layers.push(layer);if(layer[3]===1)opaque=true;}
            else if(rgba(p.backgroundColor)[3])reasons.push('Partially overlapping listbox background requires pixel verification');
          }
        }
      }
      if(!opaque){
        if(s.backgroundImage!=='none')reasons.push('Image or gradient behind text');
        const layer=rgba(s.backgroundColor);layers.push(layer);if(layer[3]===1)opaque=true;
      }
    }
    if(clipped)continue;
    if(cs.textShadow!=='none')reasons.push('Text shadow requires pixel-level verification');
    if(base.backgroundClip==='text'||base.webkitBackgroundClip==='text')reasons.push('Background clipped to text');
    if(placeholder&&cs.opacity!=='1')reasons.push('Placeholder opacity requires additional compositing');
    if(reasons.length){result.unsupported.push({...record,reasons:[...new Set(reasons)]});continue;}
    let bg=canvasColor;for(const layer of layers.reverse())bg=over(layer,bg);
    const color=placeholder?cs.color:(cs.webkitTextFillColor||cs.color),rawForeground=rgba(color),fg=over(rawForeground,bg);
    const size=parseFloat(cs.fontSize),weight=parseInt(cs.fontWeight)||400,large=size>=24||(size>=18.666666&&weight>=700),threshold=large?3:4.5;
    const measured={...record,foreground:fg,rawForeground,background:bg,fontSize:size,fontWeight:weight,threshold,ratio:ratio(fg,bg)};
    measured.pass=measured.ratio>=threshold;result.measurements.push(measured);if(!measured.pass)result.failures.push(measured);
  }
  const surface=element=>{
    const layers=[],reasons=[];let opaque=false;
    for(let a=element;a;a=a.parentElement){const s=getComputedStyle(a);
      if(Number(s.opacity)!==1||s.filter!=='none'||s.mixBlendMode!=='normal'||s.backdropFilter&&s.backdropFilter!=='none')reasons.push('Boundary compositing effect');
      if(!opaque){if(s.backgroundImage!=='none')reasons.push('Boundary image/gradient');const c=rgba(s.backgroundColor);layers.push(c);if(c[3]===1)opaque=true;}
    }
    let color=canvasColor;for(const c of layers.reverse())color=over(c,color);return {color,reasons};
  };
  for(const selector of boundarySelectors){
    let elements;try{elements=[...root.querySelectorAll(selector)];if(root.matches(selector))elements.unshift(root);}catch{result.unsupported.push({selector,kind:'boundary',reason:'Invalid boundary selector'});continue;}
    if(!elements.length)result.unsupported.push({selector,kind:'boundary',reason:'Boundary selector did not match'});
    for(const e of elements){
      const record={selector:identify(e),kind:'boundary'},s=getComputedStyle(e),r=e.getBoundingClientRect();
      if(!r.width||!r.height||s.visibility!=='visible')continue;
      if(e.matches(':disabled,[aria-disabled="true"]')){result.excluded.push({...record,reason:'Inactive control boundary'});continue;}
      // Text-entry fields retain native spinner/calendar/interior paint with appearance:auto, but
      // their opaque solid CSS outer borders are independently measurable. Do not
      // infer native fill contrast, or alpha-border contrast over native interiors.
      const nativeFieldBorder=s.appearance!=='none'&&e.matches('textarea,input:not([type]),input[type="number"],input[type="date"],input[type="text"]')&&['Top','Right','Bottom','Left'].every(side=>s['border'+side+'Style']==='solid'&&parseFloat(s['border'+side+'Width'])>0&&rgba(s['border'+side+'Color'])[3]===1);
      if(s.appearance!=='none'&&!nativeFieldBorder){result.unsupported.push({...record,reason:'Native appearance requires explicit visual/pixel verification; use appearance:none only when styling an authored control'});continue;}
      const inside=surface(e),outside=surface(e.parentElement),reasons=[...inside.reasons,...outside.reasons];
      if(reasons.length){result.unsupported.push({...record,reasons:[...new Set(reasons)]});continue;}
      const fillRatio=ratio(inside.color,outside.color);
      const edges=['Top','Right','Bottom','Left'].map(side=>({side,width:parseFloat(s['border'+side+'Width']),style:s['border'+side+'Style'],ratio:ratio(over(rgba(s['border'+side+'Color']),inside.color),outside.color)}));
      const borderPass=edges.every(edge=>edge.width>0&&['solid','double'].includes(edge.style)&&edge.ratio>=3);
      const measured={...record,background:inside.color,surrounding:outside.color,threshold:3,fillRatio:nativeFieldBorder?null:fillRatio,edges,coverage:nativeFieldBorder?'Opaque CSS outer border only; native interior, spinner and calendar icons excluded':'Authored fill or outer border',pass:(!nativeFieldBorder&&fillRatio>=3)||borderPass};
      result.boundaryMeasurements.push(measured);if(!measured.pass)result.failures.push(measured);
    }
  }
  // Generated text cannot be assumed to share the host's rendered position/background.
  for(const e of [root,...root.querySelectorAll('*')])for(const pseudo of ['::before','::after']){
    const s=getComputedStyle(e,pseudo);if(s.content&&s.content!=='none'&&s.content!=='normal'&&s.content!=='""'&&s.display!=='none'&&e.getClientRects().length)result.unsupported.push({selector:identify(e),pseudo,reason:'Generated content requires separate visual/contrast verification'});
  }
  result.status=result.failures.length?'fail':result.unsupported.length||!(result.measurements.length+result.boundaryMeasurements.length)?'incomplete':'pass';
  result.counts={measured:result.measurements.length,boundaries:result.boundaryMeasurements.length,failed:result.failures.length,unsupported:result.unsupported.length,excluded:result.excluded.length};
  result.summary={status:result.status,...result.counts};
  return result;
}
