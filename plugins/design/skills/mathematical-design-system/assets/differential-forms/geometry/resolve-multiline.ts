import type {GeometryInput} from './types.ts';
import {resolveCollection} from './resolve-collection.ts';
/** Collection density and container curvature; no composite subtraction. */
export function resolveMultiline(input:GeometryInput={}) {
 const row=resolveCollection(input),unit=input.unit??4,slot=6*unit;
 return {...row,slot,padding:row.paddingBlock,titleMinHeight:slot,descriptionGap:unit,
  minHeight:slot+2*row.inset,labelEdge:0,height:'auto' as const};
}
