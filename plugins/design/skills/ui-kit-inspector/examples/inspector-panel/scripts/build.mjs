import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import { stripTypeScriptTypes } from 'node:module';
import { createHash } from 'node:crypto';
const project = new URL('../', import.meta.url);
const source = new URL('../../../../mathematical-design-system/assets/differential-forms/', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('system.manifest.json', source)));
const target = new URL('geometry-runtime/', project);
await mkdir(target, { recursive: true });
const hashes = {};
for (const name of (await readdir(new URL('geometry/', source))).filter(n => n.endsWith('.ts')).sort()) {
  const text = await readFile(new URL(`geometry/${name}`, source), 'utf8');
  hashes[name] = createHash('sha256').update(text).digest('hex');
  const js = stripTypeScriptTypes(text).replaceAll('.ts\'', '.js\'');
  await writeFile(new URL(name.replace('.ts', '.js'), target), '// Generated from Differential Forms; run npm run build.\n' + js);
}
await writeFile(new URL('provenance.json', target), JSON.stringify({ system: manifest.name, version: manifest.version, sourceCommit: manifest.source.commit, geometrySHA256: hashes }, null, 2) + '\n');
console.log(`Built browser geometry from Differential Forms ${manifest.version}`);
