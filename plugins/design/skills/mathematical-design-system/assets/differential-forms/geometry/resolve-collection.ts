import {inputs} from './types.ts';
import type {GeometryInput} from './types.ts';
import {resolveCurvature} from './resolve-curvature.ts';
export function resolveCollection(input:GeometryInput={}) {
 const x=inputs(input),inset=[1,2,3][x.index]*x.unit;
 return {inset,gap:inset,rowSeparation:.5*x.unit,paddingBlock:inset-x.border,cellPaddingInline:inset/2-x.border,outerCellPaddingInline:inset-x.border,radius:resolveCurvature(x.curvature,x.unit,Infinity,'container')};
}
export function resolveCard(input:GeometryInput={}) {
 const x=inputs(input),inset=[3,4.5,6][x.index]*x.unit;
 return {inset,gap:inset,padding:inset-x.border,radius:resolveCurvature(x.curvature,x.unit,Infinity,'container')};
}
