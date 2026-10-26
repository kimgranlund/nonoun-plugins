import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync,readdirSync} from 'node:fs';
const root=new URL('../',import.meta.url);
const read=(path:string)=>JSON.parse(readFileSync(new URL(path,root),'utf8'));
test('manifest paths and JSON documents are valid',()=>{
 const manifest=read('system.manifest.json');
 for(const path of manifest.files)assert.ok(existsSync(new URL(path,root)),path);
 for(const dir of ['contracts','recipes','verification'])for(const name of readdirSync(new URL(dir+'/',root)))if(name.endsWith('.json'))read(dir+'/'+name);
});
test('component families and rule IDs are consistent',()=>{
 const families=read('contracts/geometry-families.json').families;
 for(const [name,component] of Object.entries(read('contracts/components.json').components))assert.ok((component as any).geometryFamily in families,name);
 const rules=read('contracts/rules.json').rules;assert.equal(new Set(rules.map((r:any)=>r.id)).size,rules.length);
 for(const rule of rules)assert.ok(['confirmed','experimental','deprecated'].includes(rule.status));
});
test('recipe component references exist',()=>{
 const components=read('contracts/components.json').components;
 function walk(x:any){if(!x||typeof x!=='object')return;if(x.component)assert.ok(x.component in components,x.component);for(const value of Object.values(x))walk(value);}
 for(const file of readdirSync(new URL('recipes/',root)))walk(read('recipes/'+file));
});
