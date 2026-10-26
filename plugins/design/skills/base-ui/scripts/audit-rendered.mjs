import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {auditRendered} from './lib/audit-rendered.mjs';
import {applyTextScale} from './lib/text-scale.mjs';
const args=process.argv.slice(2), [artifact,runtime]=args;
const usage='Usage: audit-rendered.mjs ARTIFACT.html PLAYWRIGHT [--contracts actions,fields,disclosure] [--executable CHROME] [--discover]';
if(!artifact||!runtime)throw Error(usage);
let retrieved=[], executablePath, discover=false;
for(let i=2;i<args.length;i++) {
  if(args[i]==='--discover')discover=true;
  else if(args[i]==='--contracts'&&args[i+1])retrieved=args[++i].split(',');
  else if(args[i]==='--executable'&&args[i+1])executablePath=args[++i];
  else throw Error(usage);
}
const contract=JSON.parse(fs.readFileSync(new URL('../references/style/components/contract.json',import.meta.url)));
const families=contract.families;
for(const id of retrieved)if(!families.some(f=>f.id===id)&&!['native-select','navigation-menu'].includes(id))throw Error('Unknown retrieved family: '+id);
const pw=createRequire(import.meta.url)(path.resolve(runtime));
const browser=await pw.chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
const cases=[];
try {
  for(const width of (discover?[390]:[320,390,768,1440])) for(const textScale of (discover?[1]:[1,2])) {
    const page=await browser.newPage({viewport:{width,height:1000}});
    await page.goto(pathToFileURL(path.resolve(artifact)).href);
    const inspect=async state=>{await page.evaluate(()=>document.fonts.ready);await page.evaluate(applyTextScale,textScale);cases.push({width,textScale,state,...await page.evaluate(auditRendered,{families,retrieved})});};
    await inspect('initial');
    if(!discover) {
      // Visit each disclosure separately: named accordions may close their siblings.
      const disclosures=page.locator('details:not(.sidebar__root details)');
      for(let i=0;i<await disclosures.count();i++) {
        const d=disclosures.nth(i),summary=d.locator(':scope > summary');
        if(!await summary.isVisible())continue;
        if(!await d.evaluate(e=>e.open))await summary.click();
        await inspect(`expanded-${i+1}`);
      }
    }
    await page.close();
  }
} finally {await browser.close();}
const detectedFamilies=[...new Set(cases.flatMap(c=>c.detectedFamilies))].sort();
console.log(JSON.stringify({detectedFamilies,cases,limitations:'Initial application view and reachable disclosures at320/390/768/1440 and normal/doubled computed text. This is not browser zoom. Scheme and dynamic task coverage remain app-owned. Exercise filters, selections and conditional content in task tests; call the exported audit after each relevant state.'},null,2));
if(!discover&&cases.some(c=>c.issues.length))process.exitCode=1;
