// Generated from Differential Forms; run npm run build.
                                              
import {resolveControl} from './resolve-control.js';
import {resolveChip} from './resolve-small.js';
import {resolveCurvature} from './resolve-curvature.js';
import {inputs} from './types.js';
/** Chip adornments preserve their own slot; containing input grows as needed. */
export function resolveComposedInput(input              ={}) {
 const x=inputs(input),control=resolveControl(input),chip=resolveChip(input);
 const height=Math.max(control.height,chip.height+2*control.inset);
 const radius=resolveCurvature(x.curvature,x.unit,height);
 const distanceInline=control.inset,distanceBlock=(height-chip.height)/2;
 return {...control,height,minWidth:height,radius,adornment:{...chip,minWidth:chip.height,
  distanceInline,distanceBlock,radiusInline:Math.max(0,radius-distanceInline),
  radiusBlock:Math.min(chip.height/2,Math.max(0,radius-distanceBlock))}};
}
