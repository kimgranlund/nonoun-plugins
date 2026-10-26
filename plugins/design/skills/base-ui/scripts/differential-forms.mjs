import {readFileSync, existsSync, mkdirSync, copyFileSync} from 'node:fs';
import {resolve, dirname, isAbsolute, relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';

// One authority: consume the sibling skill's current portable snapshot.
const source = fileURLToPath(new URL('../../mathematical-design-system/assets/differential-forms/', import.meta.url));
const args = process.argv.slice(2);
if (!(args.length === 1 && args[0] === '--check') && !(args.length === 2 && args[0] === '--export')) {
  console.error('Usage: node differential-forms.mjs --check | --export NEW_DIRECTORY');
  process.exit(1);
}
try {
  const manifest = JSON.parse(readFileSync(resolve(source, 'system.manifest.json'), 'utf8'));
  if (manifest.name !== 'Differential Forms' || !Array.isArray(manifest.files)) throw new Error('Expected a Differential Forms manifest');
  const files = [...new Set([...manifest.files, 'system.manifest.json'])];
  for (const file of files) {
    if (typeof file !== 'string' || isAbsolute(file) || relative(source, resolve(source, file)).startsWith('..')) throw new Error(`Invalid manifest path: ${file}`);
    readFileSync(resolve(source, file));
  }
  const authored = readFileSync(resolve(source, 'specimens/source.html'));
  const hash = createHash('sha256').update(authored).digest('hex');
  if (hash !== manifest.source.fragmentSHA256) throw new Error('Authored specimen hash does not match shared manifest');
  if (!readFileSync(resolve(source, 'specimens/index.html'), 'utf8').includes(authored.toString())) throw new Error('Shared generated specimen is stale; rebuild it first');
  let destination;
  if (args[0] === '--export') {
    destination = resolve(args[1]);
    if (existsSync(destination)) throw new Error('Export destination already exists; choose a new directory');
    mkdirSync(destination); // Parent must exist; never overwrite a consumer.
    for (const file of files) {
      const target = resolve(destination, file);
      mkdirSync(dirname(target), {recursive:true});
      copyFileSync(resolve(source, file), target);
    }
    // Verification reports may link supplemental screenshots outside manifest.files.
    for (const file of ['verification/input-focus.png', 'verification/uniform-focus.png']) {
      if (existsSync(resolve(source, file))) copyFileSync(resolve(source, file), resolve(destination, file));
    }
  }
  console.log(JSON.stringify({system:manifest.name, version:manifest.version, source, files:files.length, fragmentSHA256:hash, ...(destination ? {destination} : {}), status:destination ? 'exported' : 'aligned'}, null, 2));
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
