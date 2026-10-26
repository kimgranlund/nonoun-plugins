#!/usr/bin/env node
// Bounded dependency discovery: no filesystem crawling or automatic install/download.
import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import{createRequire}from'node:module';
const require=createRequire(import.meta.url),args=process.argv.slice(2);let check=false,moduleOverride,executableOverride;
for(let n=0;n<args.length;n++){
 const arg=args[n];if(arg==='--check'){check=true;continue;}
 if(!['--path','--executable'].includes(arg)||!args[n+1]||args[n+1].startsWith('--'))throw Error('Usage: resolve-browser.mjs [--path PLAYWRIGHT] [--executable CHROME] [--check]');
 if(arg==='--path')moduleOverride=args[++n];else executableOverride=path.resolve(args[++n]);
}
const explicit=moduleOverride??process.env.UI_PLAYWRIGHT_PATH,candidates=explicit?[path.resolve(explicit)]:['playwright',path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright')],tried=[];let result;
for(const candidate of candidates){try{const modulePath=require.resolve(candidate),pw=require(modulePath);if(!pw.chromium)throw Error('No Chromium API');const executable=executableOverride??pw.chromium.executablePath();if(!fs.existsSync(executable))throw Error('Chromium executable unavailable');if(check){const browser=await pw.chromium.launch({headless:true,executablePath:executable});await browser.close();}result={dependencyStatus:"resolved",modulePath,executable,launchChecked:check,interactionChecks:"not-run",tried};break}catch(e){tried.push({candidate,error:e.message})}}
if(!result)throw Error('Browser dependency unavailable. Set UI_PLAYWRIGHT_PATH or pass --path and, for a known installed browser, --executable; no install attempted. '+JSON.stringify(tried));console.log(JSON.stringify(result));
