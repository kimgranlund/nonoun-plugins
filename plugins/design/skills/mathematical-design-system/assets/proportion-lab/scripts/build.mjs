import {readFile,writeFile,mkdir,readdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {resolve,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {stripTypeScriptTypes} from 'node:module';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const upstream=resolve(root,'../differential-forms');
const hash=s=>createHash('sha256').update(s).digest('hex');
const read=p=>readFile(resolve(root,p),'utf8');
const source=await read('specimens/source.html'), css=await read('src/app.css'), app=await read('src/app.js');
const order=['types','resolve-curvature','resolve-control','resolve-small','resolve-collection','resolve-composite','resolve-composed-input','resolve-multiline'];
await mkdir(resolve(root,'dist/runtime/geometry'),{recursive:true});
await mkdir(resolve(root,'dist/styles'),{recursive:true});
const compiled={};
for(const file of (await readdir(resolve(upstream,'geometry'))).filter(f=>f.endsWith('.ts'))){
 const code=stripTypeScriptTypes(await readFile(resolve(upstream,'geometry',file),'utf8')).replaceAll('.ts\'', '.js\'');
 compiled[file.slice(0,-3)]=code;
 await writeFile(resolve(root,'dist/runtime/geometry',file.replace(/\.ts$/,'.js')),code);
}
const unmodule=code=>code.replace(/^import\s+[\s\S]*?from\s+['"][^'"]+['"];?\s*$/gm,'').replace(/\bexport\s+(?=(?:function|const|let|class)\b)/g,'');
const script='(()=>{\n'+order.map(n=>unmodule(compiled[n])).join('\n')+'\n'+unmodule(app)+'\n})();';
const html=source.replace(/<link\b[^>]*href=["']\.\/styles\/differential\.css["'][^>]*>/,()=>'<style>'+css+'</style>')
 .replace(/<script\b[^>]*src=["']\.\/runtime\/app\.js["'][^>]*>\s*<\/script>/,()=>'<script>'+script.replaceAll('</script','<\\/script')+'</script>');
if(html===source||html.includes('./runtime/app.js'))throw Error('Source build markers missing');
await writeFile(resolve(root,'dist/runtime/app.js'),app);
await writeFile(resolve(root,'dist/styles/differential.css'),css);
await writeFile(resolve(root,'dist/index.html'),html);
await writeFile(resolve(root,'specimens/index.html'),html);
const baseline=JSON.parse(await readFile(resolve(upstream,'system.manifest.json'),'utf8'));
await writeFile(resolve(root,'system.manifest.json'),JSON.stringify({name:'Proportion study',version:'1.0.0',source:{fragmentSHA256:hash(source),implementationSHA256:hash(source+css+app),authored:'specimens/source.html'},upstream:{path:'../differential-forms',version:baseline.version,source:baseline.source},provenance:'Consumer migration to shared Differential Forms typed resolvers, 2026-10-22. No upstream formula changes.'},null,2)+'\n');
console.log('Built standalone dist/index.html and specimens/index.html from authored source and shared resolvers.');
