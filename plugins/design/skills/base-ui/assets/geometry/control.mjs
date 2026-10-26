import {resolveControlSurface,resolveButtonPadding} from './scale.mjs';
export {resolveGeometry,resolveSpacingRoles,composeContainer,resolveDataRowGeometry} from './scale.mjs';
export {resolvePercentageRadiusGroup,resolveMediaRadius} from './curvature.mjs';
/** Required geometry remains unchanged when invalid. Caller exposes issues. */
export function resolveControlAnatomy({n,density='regular',gutterPercent=25,radius=0,hasLeading=false,hasTrailing=false,slots=['icon','glyph']}) {
 const surface=resolveControlSurface(n,density,gutterPercent);
 const padding=resolveButtonPadding({margin:surface.margin,wrapperInset:surface.labelPadding,height:surface.height,hasLeading,hasTrailing});
 const issues=[];
 for(const [slot,art] of [['icon',surface.icon],['glyph',surface.glyph]])
  if(slots.includes(slot)&&2*surface.slotPadding+art>surface.slotHeight)issues.push(`${slot}: wrapper padding exceeds fixed square budget`);
 if(radius>surface.height/2)issues.push('radius exceeds height cap; validate measured width too');
 return {surface,padding,issues,valid:issues.length===0};
}
