import assert from 'node:assert/strict';import{checkMeasurements}from'./review-measurements.mjs';
const contrast={scope:'Rendered text in the current DOM/state',status:'pass',failures:[],unsupported:[]};
const access={scope:'Declared task access only; visual density requires review.',status:'fail',issues:[{code:'TASK_SCROLL_BUDGET'}]};
assert.equal(checkMeasurements({result:'passed',states:[{contrast,access}]}).status,'fail');
assert.equal(checkMeasurements({result:'passed'}).status,'unreviewed');
assert.equal(checkMeasurements({contrast:{...contrast,status:'incomplete',unsupported:[{}]}}).status,'fail');
assert.equal(checkMeasurements([{contrast},{access:{...access,status:'pass',issues:[]}}]).status,'pass');
console.log('PASS measurement gate: detects nested failure despite enclosing passed, unknown scope, unsupported, and positive records');
