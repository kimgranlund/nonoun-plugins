// Browser-side geometry oracle for the maintained canvas composition.
export function measureCanvasGeometry() {
 const errors=[],panels=[],cornerFactor=CSS.supports('corner-shape','superellipse(1.5)')?1.5:1;
 const near=(actual,expected,label)=>{if(Math.abs(actual-expected)>0.6)errors.push({label,actual,expected})};
 for(const panel of document.querySelectorAll('[data-canvas-panel]')){
  if(!panel.getClientRects().length)continue;
  const probe=document.createElement('i');probe.style.cssText='position:absolute;width:var(--g-margin);height:0';panel.append(probe);const n=probe.getBoundingClientRect().width;probe.remove();
  const s=getComputedStyle(panel),measure={role:panel.className,n,radius:parseFloat(s.borderTopLeftRadius),margins:{}};
  for(const side of ['Top','Right','Bottom','Left']){const margin=parseFloat(s['padding'+side])+parseFloat(s['border'+side+'Width']);measure.margins[side]=margin;near(margin,2*n,`${panel.className} ${side} border-inclusive margin`)}
  near(measure.radius,cornerFactor*2*n,`${panel.className} widget radius`);
  for(const group of panel.querySelectorAll('.cluster__root,.canvas-body,header,#canvas-options')){
   if(!group.getClientRects().length)continue;
   const style=getComputedStyle(group);for(const axis of ['rowGap','columnGap']){const gap=parseFloat(style[axis]);if(Number.isFinite(gap))near(gap,n,`${group.className||group.tagName} ${axis}`)}
  }
  const title=panel.querySelector('header h2'),body=panel.querySelector('.canvas-body');
  if(title&&body){near(body.getBoundingClientRect().left+parseFloat(getComputedStyle(body).paddingLeft),title.getBoundingClientRect().left,'inspector shared text rail')}
  for(const range of panel.querySelectorAll('.canvas-body input[type=range]')){
   near(range.getBoundingClientRect().height,Math.max(4*n,24),'inspector range frame');
   near(parseFloat(getComputedStyle(range).marginLeft),0,'inspector range native margin');
  }
  panels.push(measure);
 }
 return {pass:!errors.length,errors,panels};
}
