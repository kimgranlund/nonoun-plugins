#!/usr/bin/env node
// Standard skill generation: publish only after all mandatory gates succeed.
import fs from 'node:fs';import path from 'node:path';import {spawnSync}from'node:child_process';import {createHash} from 'node:crypto';import {reviewRoot as root,loadUI} from './ui-kit.mjs';const sha=b=>createHash('sha256').update(b).digest('hex');
import {verifySource} from './lib/source-preservation.mjs';
const usage='Usage: generate.mjs MANIFEST NEW_OUTPUT_DIRECTORY PLAYWRIGHT [--controller JS] [--review JSON] [--policy JSON] [--acceptance EVALUATOR_JSON] [--preserve BASELINE_JSON] [--mode draft|delivery]';
if(process.argv.length===3&&['--help','-h'].includes(process.argv[2])){console.log(usage);process.exit(0);}
const args=process.argv.slice(2),[input,destination,requestedPW]=args.splice(0,3),options={};
if(!input||!destination||!requestedPW)throw Error('Usage: generate.mjs MANIFEST NEW_OUTPUT_DIRECTORY PLAYWRIGHT [--controller JS] [--review JSON] [--policy JSON] [--acceptance EVALUATOR_JSON] [--preserve BASELINE_JSON] [--mode draft|delivery]');
while(args.length){const key=args.shift(),value=args.shift();if(!['--controller','--review','--policy','--acceptance','--preserve','--mode','--ui-kit'].includes(key)||!value||options[key])throw Error('Invalid or duplicate option: '+key);options[key]=value;}
const mode=options['--mode']||(options['--acceptance']?'delivery':'draft');if(!['draft','delivery'].includes(mode))throw Error('Unknown generation mode');if(mode==='delivery'&&!options['--acceptance'])throw Error('Delivery mode requires evaluator --acceptance; use draft for incomplete emission');
const kit=await loadUI(options['--ui-kit']);
let pw=requestedPW;if(pw==='auto'){const resolved=spawnSync(process.execPath,[path.join(kit.root,'scripts/resolve-browser.mjs')],{encoding:'utf8'});if(resolved.status!==0)throw Error('Browser routing failed: '+resolved.stderr);pw=JSON.parse(resolved.stdout).modulePath;}

const output=path.resolve(destination);if(fs.existsSync(output))throw Error('Preserve delivered output; choose a new directory');
fs.mkdirSync(path.dirname(output),{recursive:true});const stage=fs.mkdtempSync(path.join(path.dirname(output),'.wireframe-generation-'));
const stages=[],summary={uiKit:kit.identity,mode,status:'running',stages,limitations:['Compile, structural verification, executed startup and lint establish artifact emission; task delivery needs independent acceptance. Named accepted limitations remain separate.']};
function run(name,script,params){const r=spawnSync(process.execPath,[path.join(root,'scripts',script),...params],{encoding:'utf8',env:{...process.env,WIREFRAME_UI_KIT:kit.root}});stages.push({name,exit:r.status,signal:r.signal,stdout:r.stdout,stderr:r.stderr});if(r.error||r.status!==0)throw Error(name+' failed: '+(r.error?.message||r.stderr||r.stdout));}
try{
 if(options['--preserve'])summary.preservation=verifySource(options['--preserve']);
 const source=fs.readFileSync(input);fs.writeFileSync(path.join(stage,'source.manifest.json'),source);summary.source={path:path.resolve(input),sha256:sha(source)};
 const buildArgs=[path.join(stage,'source.manifest.json'),path.join(stage,'artifact.html')];
 for(const [flag,name]of [['--review','review.json'],['--controller','controller.js'],['--policy','lint-policy.json'],['--acceptance','acceptance.json']])if(options[flag]){const bytes=fs.readFileSync(options[flag]);fs.writeFileSync(path.join(stage,name),bytes);summary[flag.slice(2)]={path:path.resolve(options[flag]),sha256:sha(bytes)};}
 if(options['--review'])buildArgs.push(path.join(stage,'review.json'));if(options['--controller'])buildArgs.push('--controller',path.join(stage,'controller.js'));
 run('compile','build.mjs',buildArgs);
 const html=fs.readFileSync(path.join(stage,'artifact.html'),'utf8'),match=html.match(/const MANIFEST=(.*);\n/);if(!match)throw Error('Compiled manifest missing');
 // Build-time select compilation changes anatomy; verify the manifest actually emitted.
 fs.writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(JSON.parse(match[1]),null,2));
 run('artifact-verification','verify-artifact.mjs',[path.join(stage,'manifest.json'),path.join(stage,'artifact.html'),path.join(stage,'verification.json')]);
 run('runtime-startup','check-runtime-startup.mjs',[path.join(stage,'manifest.json'),path.join(stage,'artifact.html'),pw,path.join(stage,'runtime.json')]);
 run('preventive-lint','lint-artifact.mjs',[path.join(stage,'artifact.html'),pw,path.join(stage,'lint.json'),...(options['--policy']?[path.join(stage,'lint-policy.json')]:[])]);
 const lint=JSON.parse(fs.readFileSync(path.join(stage,'lint.json')));summary.findings={warnings:lint.findings.filter(f=>f.severity==='warning'),unverified:lint.findings.filter(f=>f.severity==='unverified')};
 summary.delivery={status:'delivery-incomplete',reason:'No evaluator task acceptance supplied'};
 if(options['--acceptance']){summary.delivery={status:'delivery-incomplete',reason:'Acceptance executing'};run('task-acceptance','verify-acceptance.mjs',[path.join(stage,'artifact.html'),path.join(stage,'acceptance.json'),path.join(stage,'acceptance-report.json'),pw]);summary.delivery={status:'delivery-verified',scope:'Applicable evaluator cases only; completeness and independence require review'};}
 if(options['--preserve'])summary.preservation=verifySource(options['--preserve']);
 summary.status=summary.findings.unverified.length?'passed-with-unverified-coverage':summary.findings.warnings.length?'passed-with-warnings':'passed';
 summary.artifactSHA256=sha(fs.readFileSync(path.join(stage,'artifact.html')));
 // Make report paths valid in the final directory; source hashes and observations are unchanged.
 for(const file of ['verification.json','lint.json','runtime.json',...(options['--acceptance']?['acceptance-report.json']:[])]){const report=fs.readFileSync(path.join(stage,file),'utf8').split(stage).join(output);fs.writeFileSync(path.join(stage,file),report);}
 summary.stages=stages.map(s=>({...s,stdout:s.stdout.split(stage).join(output),stderr:s.stderr.split(stage).join(output)}));
 summary.reports=Object.fromEntries(['verification.json','lint.json','runtime.json',...(options['--acceptance']?['acceptance-report.json']:[])].map(f=>[f,sha(fs.readFileSync(path.join(stage,f)))]));
 summary.pipelineSHA256=sha(fs.readFileSync(path.join(root,'scripts/generate.mjs')));
 fs.writeFileSync(path.join(stage,'generation.json'),JSON.stringify(summary,null,2));
 if(fs.existsSync(output))throw Error('Output appeared during generation; refusing replacement');fs.renameSync(stage,output);
 console.log(JSON.stringify({output,status:summary.status,artifact:path.join(output,'artifact.html'),warnings:summary.findings.warnings.length,unverified:summary.findings.unverified.length,report:path.join(output,'generation.json')}));
}catch(e){summary.status='failed';summary.error=e.message;fs.writeFileSync(path.join(stage,'generation.json'),JSON.stringify(summary,null,2));console.error(JSON.stringify({status:'failed',diagnostics:stage,error:e.message}));process.exitCode=1;}
