// Browser-evaluated test utility. Restores prior inline styles before remeasuring,
// so repeated audits and newly rendered descendants do not compound the scale.
export function applyTextScale(scale){
 if(!Number.isFinite(scale)||scale<=0)throw Error('Positive text scale required');
 const key=Symbol.for('base-ui.audit.original-text-style');const originals=window[key]||(window[key]=new WeakMap());
 const elements=[document.body,...document.body.querySelectorAll('*')];
 for(const e of elements){if(!originals.has(e))originals.set(e,{font:e.style.fontSize,line:e.style.lineHeight,fontPriority:e.style.getPropertyPriority('font-size'),linePriority:e.style.getPropertyPriority('line-height')});const old=originals.get(e);e.style.setProperty('font-size',old.font,old.fontPriority);e.style.setProperty('line-height',old.line,old.linePriority);}
 const sizes=elements.map(e=>{const s=getComputedStyle(e);return[e,parseFloat(s.fontSize),parseFloat(s.lineHeight)]});
 for(const[e,font,line]of sizes){e.style.setProperty('font-size',font*scale+'px','important');if(Number.isFinite(line))e.style.setProperty('line-height',line*scale+'px','important');}
}
