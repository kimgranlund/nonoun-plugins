// Serializable, bounded prerequisite before measuring a settled UI state.
export async function settleReview({timeoutMs=1500}={}) {
 let timer,expired=false;
 const ready=(async()=>{
  await document.fonts.ready;
  let quietFrames=0,maxFiniteAnimations=0;
  while(!expired&&quietFrames<2){
   await new Promise(resolve=>requestAnimationFrame(resolve));
   // Re-sample live animations: style replacement can detach an animation while
   // its old finished promise stays pending in Chromium. New animations count too.
   const active=document.getAnimations().filter(a=>a.effect?.getComputedTiming().iterations!==Infinity&&!['finished','idle'].includes(a.playState));
   maxFiniteAnimations=Math.max(maxFiniteAnimations,active.length);
   quietFrames=active.length?0:quietFrames+1;
  }
  return {status:'ready',finiteAnimations:maxFiniteAnimations};
 })();
 const result=await Promise.race([ready,new Promise(resolve=>{timer=setTimeout(()=>{expired=true;resolve({status:'unsettled',reason:'Fonts or finite animations exceeded measurement timeout'});},timeoutMs)})]);
 clearTimeout(timer);return result;
}
