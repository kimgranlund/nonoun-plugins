import assert from 'node:assert/strict';
import {resolvePercentageRadiusGroup as resolve} from '../assets/geometry/curvature.mjs';
const frame=(x,y,width,height)=>({x,y,width,height});
for(const drift of [-.001,0,.001]){
 const g=resolve({amount:100,mode:'nested',frames:[frame(0,0,100,72),frame(drift,drift,100,72)],referenceHeights:[24,24]});
 assert.equal(g.valid,true);assert.equal(g.layers[0].radius,12);assert.equal(g.layers[1].radius,12);
}
const overflow=resolve({amount:100,mode:'nested',frames:[frame(0,0,100,72),frame(-1,0,101,72)],referenceHeights:[24,24]});
assert.equal(overflow.valid,false);assert(overflow.issues.some(x=>x.includes('outside parent')));assert(overflow.layers.every(l=>l.physicalExcess<=.001));
const parent=resolve({amount:100,mode:'standalone',frames:[frame(0,0,100,72)],referenceHeights:[24]});
const rows=[100,10,100].map(width=>resolve({amount:100,mode:'standalone',frames:[frame(0,0,width,24)],referenceHeights:[24],parentRadius:parent.layers[0].radius}));
assert.equal(parent.valid,true);assert.deepEqual(rows.map(g=>g.valid),[true,false,true]);assert(rows.every(g=>g.layers[0].radius===12));assert.equal(rows[1].layers[0].physicalExcess,7);
for(const [height,valid] of [[23.999,true],[23.98,false]])assert.equal(resolve({amount:100,mode:'standalone',frames:[frame(0,0,100,height)],referenceHeights:[24]}).valid,valid);
console.log('PASS containment noise, genuine overflow, independent parent/sibling radii, exact conflict geometry');
