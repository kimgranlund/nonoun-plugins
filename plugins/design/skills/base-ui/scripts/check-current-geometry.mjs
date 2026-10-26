import assert from 'node:assert/strict';
import {resolveGeometry,resolveControlAnatomy} from '../assets/geometry/control.mjs';
let count=0;
for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg'])for(const [density,q] of Object.entries({tight:2,compact:3,regular:4,spacious:5,loose:6})) {
 const {n}=resolveGeometry(tier,scale,size,density);
 for(const [hasLeading,hasTrailing] of [[false,false],[true,false],[false,true],[true,true]]) {
  const r=resolveControlAnatomy({n,density,radius:(q+4)*n/4,hasLeading,hasTrailing});
  assert.equal(r.surface.height,(q+4)*n/2);
  assert.equal(r.surface.mediaSize,3*n);assert.equal(r.surface.mediaPadding,0);
  assert.equal(resolveControlAnatomy({n,density,gutterPercent:200,slots:['media','label']}).valid,true);
  assert.equal(r.surface.iconSlotWidth,3*n);assert.equal(r.surface.glyphSlotWidth,3*n);
  assert.equal(r.surface.glyph,n+6);assert.equal(r.surface.slotGap,r.surface.margin/2);
  assert.equal(r.padding.labelStart,n/2);
  assert.equal(r.padding.labelEnd,n/2);
  assert.equal(r.padding.inlinePadding,r.surface.margin);
  assert.equal(r.padding.compensation,0);
  assert.equal(r.padding.edgePadding,r.padding.compensation);assert.equal(r.surface.labelPadding,n/2);assert.equal(r.surface.wrapperGap,0);
  for(const radius of [0,r.surface.height/4,r.surface.height/2,r.surface.height]) {
   const changed=resolveControlAnatomy({n,density,radius,hasLeading,hasTrailing});
   assert.deepEqual(changed.padding,r.padding,'radius must never affect padding, even on physical conflict');
  }
  const conflict=resolveControlAnatomy({n,density,gutterPercent:200});
  assert.equal(conflict.valid,false);assert.equal(conflict.surface.iconSlotWidth,3*n);
  count++;
 }
}
console.log(`Current geometry: ${count} contexts/arrangements; fixed-budget negative controls passed`);
