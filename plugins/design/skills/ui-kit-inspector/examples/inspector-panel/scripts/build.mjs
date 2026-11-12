// Builds geometry-runtime/derive.js, a browser copy of ui-geometry's calculator, and records its source hash.
// The source module imports node:fs and node:url for its CLI; the browser copy drops those imports and the CLI.
import { readFile, writeFile, mkdir, rm } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
export const source = new URL('../../../../ui-geometry/scripts/derive.mjs', import.meta.url);
export const target = new URL('../geometry-runtime/', import.meta.url);
export const HEADER = '// Generated from ui-geometry/scripts/derive.mjs by scripts/build.mjs; run npm run build, do not edit.\n';

/** The browser module for one derive.mjs text: no shebang, no node: imports, nothing from the CLI section on. */
export function browserRuntime(text) {
  const cut = text.indexOf('\nfunction loadPreset(');
  if (cut < 0) throw new Error('derive.mjs: CLI section (function loadPreset) not found; update scripts/build.mjs');
  const body = text.slice(0, cut + 1).replace(/^#!.*\n/, '').replace(/^import [^\n]* from 'node:[^']+'\n/gm, '');
  const left = body.match(/\bnode:|readFileSync|realpathSync|fileURLToPath|\bprocess\./);
  if (left) throw new Error(`derive.mjs: the browser copy still uses ${left[0]}; update scripts/build.mjs`);
  return HEADER + body;
}

export const sha256 = (text) => createHash('sha256').update(text).digest('hex');

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const text = await readFile(source, 'utf8');
  await rm(target, { recursive: true, force: true });
  await mkdir(target, { recursive: true });
  await writeFile(new URL('derive.js', target), browserRuntime(text));
  await writeFile(new URL('provenance.json', target), JSON.stringify({ source: 'ui-geometry/scripts/derive.mjs', sha256: sha256(text) }, null, 2) + '\n');
  console.log('Built geometry-runtime/derive.js from ui-geometry');
}
