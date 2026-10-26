// Generated from Differential Forms; run npm run build.
import {inputs} from './types.js';
                                              
import {resolveControl} from './resolve-control.js';
import {resolveCurvature} from './resolve-curvature.js';
export function resolveChip(input              ={}) {
 const x=inputs(input),c=resolveControl(input),slot=4*x.unit,height=slot+2*c.inset;
 return {...c,slot,height,labelEdge:c.labelEdge/2,fontSize:2*x.unit+4,lineHeight:slot,radius:resolveCurvature(x.curvature,x.unit,height),iconSize:slot-2*x.border};
}
export function resolveBadge(input              ={},contentWidth=0) {
 const x=inputs(input),c=resolveControl(input),height=4*x.unit,inset=.5*x.unit;
 if(!Number.isFinite(contentWidth)||contentWidth<0) throw new RangeError('contentWidth must be nonnegative');
 return {height,minWidth:height,width:Math.max(height,contentWidth+2*inset),inlineInset:inset,paddingInline:inset-x.border,border:x.border,fontSize:2*x.unit+2,radius:Math.min(c.radius,height/2)};
}
export function resolveChoice(input              ={}) {
 const x=inputs(input),c=resolveControl(input),u=x.unit;
 return {...c,artwork:4*u,checkboxRadius:u,radioRadius:2*u,switchWidth:9*u,switchHeight:5*u,switchInset:.5*u,switchPadding:.5*u-x.border,switchThumb:4*u};
}
