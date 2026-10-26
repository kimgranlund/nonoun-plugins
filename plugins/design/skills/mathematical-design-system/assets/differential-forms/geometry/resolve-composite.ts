import type {GeometryInput} from './types.ts';
import {resolveControl} from './resolve-control.ts';
import {resolveChip} from './resolve-small.ts';
import {resolveNestedRadius} from './resolve-curvature.ts';
/** Shared border policy; arbitrary recursive nesting is not supported. */
export function resolveComposite(input:GeometryInput & {insetUnits?:number; childFamily?:'control'|'chip'}={}) {
 if(input.childFamily!==undefined&&!['control','chip'].includes(input.childFamily)) throw new RangeError('unknown composite child family');
 const c=input.childFamily==='chip'?resolveChip(input):resolveControl(input),requestedInset=(input.insetUnits??0)*c.unit;
 if(!Number.isFinite(requestedInset)||requestedInset<0||requestedInset>1.5*c.unit) throw new RangeError('composite inset must be 0..1.5u');
 const effectiveInset=Math.max(c.border,requestedInset),childInset=Math.max(c.border,c.inset-effectiveInset),childHeight=c.slot+2*childInset;
 return {requestedInset,effectiveInset,padding:effectiveInset-c.border,gap:requestedInset,radius:c.radius,
 child:{...c,inset:childInset,padding:childInset-c.border,height:childHeight,radius:resolveNestedRadius(c.radius,effectiveInset,childHeight,requestedInset)},
 singleRowHeight:childHeight+2*effectiveInset};
}
