import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {settleReview} from './lib/settle-review.mjs';
import {auditContrast} from './lib/audit-contrast.mjs';
import {auditTaskAccess} from './lib/audit-task-access.mjs';
const [artifact,runtime,output,...args]=process.argv.slice(2);
const usage='audit-review.mjs APP PLAYWRIGHT NEW_OUTPUT_DIR --task SELECTOR --budget SCREENS --rationale TEXT [--executable CHROME] [--boundary SELECTOR]';
const opts={},boundarySelectors=[];
for(let i=0;i<args.length;i++){const k=args[i];if(!['--task','--budget','--rationale','--executable','--boundary'].includes(k)||!args[i+1])throw Error(usage);const v=args[++i];if(k==='--boundary')boundarySelectors.push(v);else opts[k]=v;}
if(!artifact||!runtime||!output||!opts['--task']||!opts['--rationale']||!Number.isFinite(Number(opts['--budget'])))throw Error(usage);
fs.mkdirSync(output); // Preserve previous evidence; a new directory is required.
const pw=createRequire(import.meta.url)(path.resolve(runtime));
const browser=await pw.chromium.launch({headless:true,...(opts['--executable']?{executablePath:opts['--executable']}:{})});
const cases=[];
try {
 for(const width of [320,390,768,1440])for(const scheme of ['light','dark']){
  const page=await browser.newPage({viewport:{width,height:844},colorScheme:scheme,offline:true});
  await page.goto(pathToFileURL(path.resolve(artifact)).href);
  await page.evaluate(s=>{document.documentElement.dataset.theme=s;document.documentElement.style.colorScheme=s},scheme);
  const settled=await page.evaluate(settleReview);
  if(settled.status!=='ready')throw Error(JSON.stringify(settled));
  const contrast=await page.evaluate(auditContrast,{boundarySelectors});
  const taskAccess=await page.evaluate(auditTaskAccess,{taskSelector:opts['--task'],maxScreens:Number(opts['--budget']),rationale:opts['--rationale']});
  const screenshot=`${width}-${scheme}.png`;
  await page.screenshot({path:path.join(output,screenshot),fullPage:true});
  cases.push({width,height:844,scheme,state:'initial',contrast,taskAccess,screenshot});
  await page.close();
 }
}finally{await browser.close();}
const result={artifact:path.resolve(artifact),cases,limitations:'Initial states only. Schemes forced for paint measurements; application theme-toggle behavior is not tested. Inspect screenshots at actual size. Dynamic, expanded, error, selected and focus states require task-owned interaction tests using the exported helpers. Contrast scope and unsupported samples are explicit in each case. Task access is a declared budget, not aesthetic certification.'};
fs.writeFileSync(path.join(output,'measurements.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({output:path.resolve(output),cases:cases.map(c=>({width:c.width,scheme:c.scheme,contrast:c.contrast.status,taskAccess:c.taskAccess.status}))},null,2));
if(cases.some(c=>c.contrast.status!=='pass'||c.taskAccess.status!=='pass'))process.exitCode=1;
