// HISTORICAL: pre-Differential Forms model. Current resolvers/tests are in assets/differential-forms/.
import {CFG} from './scale.mjs';
// Session-local table form of the adopted tier polynomial.
export function defaultTierMapping(){
 return Object.fromEntries(Object.entries(CFG.tiers).map(([tier,[n0,a,k,g]])=>[tier,Object.fromEntries(['sm','md','lg'].map((scale,i)=>[scale,{baseline:n0+a*(i-1),step:k+g*(i-1)}]))]));
}
export function mappedUnit(mapping,tier,scale,size){return mapping[tier][scale].baseline+({sm:-1,md:0,lg:1}[size])*mapping[tier][scale].step;}
export function validateTierMapping(mapping){
 const errors=[],scales=['sm','md','lg'];
 for(const tier of Object.keys(CFG.tiers)){
  for(const scale of scales){const cell=mapping[tier]?.[scale];if(!cell||!Number.isFinite(cell.baseline)||!Number.isFinite(cell.step)||cell.step<=0){errors.push({tier,scale,message:'Baseline and positive size step must be finite.'});continue;}
   for(const size of scales){const n=mappedUnit(mapping,tier,scale,size);if(n<CFG.ladder[0]||n>CFG.ladder[1])errors.push({tier,scale,message:`${tier} / ${scale} / ${size} resolves to n=${n}; use ${CFG.ladder[0]}–${CFG.ladder[1]}.`});}
  }
  if(scales.every(s=>mapping[tier]?.[s]))for(const size of scales)for(let i=1;i<3;i++)if(mappedUnit(mapping,tier,scales[i],size)<=mappedUnit(mapping,tier,scales[i-1],size))errors.push({tier,scale:scales[i],message:`${tier}: scales must increase at ${size} size.`});
 }
 return errors;
}
