import assert from 'node:assert/strict';import {createRequire} from 'node:module';import {settleReview} from './lib/settle-review.mjs';
const[pw,exe]=process.argv.slice(2);const{chromium}=createRequire(import.meta.url)(pw);const b=await chromium.launch({executablePath:exe});
try{const p=await b.newPage();await p.setContent('<button>Changing state</button>');
await p.evaluate(()=>document.querySelector('button').animate([{opacity:.2},{opacity:1}],{duration:80}));assert.equal((await p.evaluate(settleReview)).status,'ready');
await p.evaluate(()=>{window.paused=document.querySelector('button').animate([{opacity:.2},{opacity:1}],{duration:500});window.paused.pause()});assert.equal((await p.evaluate(settleReview,{timeoutMs:100})).status,'unsettled');await p.evaluate(()=>window.paused.cancel());
await p.evaluate(()=>document.querySelector('button').animate([{opacity:.2},{opacity:1}],{duration:500,iterations:Infinity}));assert.equal((await p.evaluate(settleReview)).status,'ready');await p.evaluate(()=>document.getAnimations().forEach(a=>a.cancel()));
// Browser regression model: removed transition has an unresolved old finished promise.
await p.evaluate(()=>{const native=document.getAnimations.bind(document);let first=true;document.getAnimations=()=>{if(!first)return native();first=false;return[{playState:'running',effect:{getComputedTiming:()=>({iterations:1})},finished:new Promise(()=>{})}]}});
assert.equal((await p.evaluate(settleReview,{timeoutMs:200})).status,'ready');
console.log(JSON.stringify({status:'pass',cases:['finite animation settles','paused finite animation blocks','infinite ambient animation excluded','removed transition does not block on stale promise'],scope:'Settling prerequisite only; no visual judgment'}));
}finally{await b.close()}
