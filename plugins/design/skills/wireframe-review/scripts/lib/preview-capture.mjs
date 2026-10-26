// Normalize only evaluator shell presentation; authored frame DOM/styles remain untouched.
export async function capturePreviewBody(page, iframe, output){
 const frame=await(await iframe.elementHandle()).contentFrame();if(!frame)throw Error('Preview frame unavailable');
 const body=frame.locator('body'),inner=await body.evaluate(()=>({width:innerWidth,height:Math.ceil(Math.max(document.documentElement.scrollHeight,document.body.scrollHeight))}));
 const viewport=page.viewportSize();let saved;
 try{
  saved=await iframe.evaluate(e=>{const rows=[];for(let n=e;n;n=n.parentElement){rows.push({style:n.getAttribute('style')});n.style.setProperty('transform','none','important');n.style.setProperty('overflow','visible','important');n.style.setProperty('max-height','none','important')}return rows});
  await iframe.evaluate((e,v)=>{e.style.setProperty('width',v.width+'px','important');e.style.setProperty('height',v.height+'px','important')},inner);
  const r=await iframe.boundingBox();if(!r)throw Error('Preview is hidden');await page.setViewportSize({width:Math.ceil(Math.max(viewport.width,r.x+inner.width+32)),height:Math.ceil(Math.max(viewport.height,r.y+inner.height+32))});
  await iframe.scrollIntoViewIfNeeded();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const bounds=await body.boundingBox(),actual=await body.evaluate(()=>innerWidth),outer=page.viewportSize();
  if(actual!==inner.width||!bounds||Math.abs(bounds.width-inner.width)>1||bounds.x<0||bounds.y<0||bounds.x+bounds.width>outer.width+1||bounds.y+bounds.height>outer.height+1)throw Error('Capture bounds remain transformed or clipped');
  await body.screenshot({path:output,caret:'initial'});return{innerWidth:actual,bounds,outerViewport:outer,normalizedShellOnly:true};
 }finally{
  if(saved)await iframe.evaluate((e,rows)=>{let n=e;for(const row of rows){if(!n)break;if(row.style===null)n.removeAttribute('style');else n.setAttribute('style',row.style);n=n.parentElement}},saved);
  await page.setViewportSize(viewport);
 }
}
