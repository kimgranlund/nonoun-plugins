import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
export const reviewRoot=path.resolve(import.meta.dirname,'..');
export async function loadUI(root=process.env.WIREFRAME_UI_KIT||path.resolve(reviewRoot,'../base-ui')){
 root=path.resolve(root);let d;try{d=JSON.parse(fs.readFileSync(path.join(root,'kit.json')));}catch{throw Error('base-ui dependency missing: install base-ui beside wireframe-review or pass --ui-kit ROOT');}
 if(d.schemaVersion!==1||d.packageId!=='local.base-ui'||d.runtimeApiVersion!==1)throw Error('Incompatible base-ui descriptor/API; install the compatible release pair');
 const api=await import(pathToFileURL(path.join(root,'scripts/api.mjs')));const identity=api.describeKit();const lock=JSON.parse(fs.readFileSync(path.join(reviewRoot,'ui-kit.lock.json')));
 if(lock.contentSHA256!==identity.contentSHA256||lock.version!==identity.version)throw Error('base-ui lock mismatch; reconcile and run sync-ui-kit.mjs explicitly before generation');const mirror=JSON.parse(fs.readFileSync(path.join(reviewRoot,'ui-compatibility.json')));for(const p of mirror.files){if(!fs.readFileSync(path.join(reviewRoot,p)).equals(fs.readFileSync(path.join(root,p))))throw Error('UI compatibility drift: '+p+'; reconcile source and sync explicitly');}return {root,api,identity};
}
export function takeKitOption(args){const i=args.indexOf('--ui-kit');if(i<0)return undefined;const value=args[i+1];if(!value||value.startsWith('--'))throw Error('--ui-kit needs ROOT');args.splice(i,2);return value;}
