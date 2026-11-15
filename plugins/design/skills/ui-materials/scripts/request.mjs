#!/usr/bin/env node
// Prints the ui-colors request fragment for ui-materials' paint roles: { "translucent": { "paint-<use>": { of, alpha, … } } }.
// It only assembles data: the alphas come from references/paint.json, the cast alphas from ui-geometry's elevation layers,
// and ui-colors generates the colours. Node built-ins only; reads no network.
//
//   node scripts/request.mjs                          the fragment, on stdout
//   node scripts/request.mjs --merge request.json     that request with the paint roles merged into its `translucent` key
//   node scripts/request.mjs --layers 5               five cast layers (default: paint.json › cast.layers)
//   node scripts/request.mjs --no-casts               without cast roles (also what happens when ui-geometry is not installed)

import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const DERIVE = resolve(ROOT, '..', 'ui-geometry', 'scripts', 'derive.mjs');
const round = (x) => +x.toFixed(4);

export const loadPaint = () => JSON.parse(readFileSync(join(ROOT, 'references', 'paint.json'), 'utf8'));

/** ui-geometry's cast alphas per scheme, { light: [α_0…], dark: [α_0…] }, or null when ui-geometry is not installed beside this skill. */
export function castAlphas(paint, layers = paint.cast.layers) {
  if (!existsSync(DERIVE)) return null;
  const one = (scheme) => JSON.parse(execFileSync(process.execPath, [DERIVE, '--elevation', paint.cast.level, '--json', '--layers', String(layers), '--scheme', scheme], { encoding: 'utf8' }))[0].layers.map((l) => l.alpha);
  return { light: one('light'), dark: one('dark') };
}

/** The request fragment. casts: the result of castAlphas(), or null to leave the cast roles out. */
export function fragment(paint, casts) {
  const out = {};
  for (const [name, r] of Object.entries(paint.roles)) {
    const base = paint.bases[r.base];
    if (!base) throw new Error(`paint.json: role ${name} names the unknown base ${r.base}`);
    const e = { of: base.of };
    if (base.darkOf != null) e.darkOf = base.darkOf;
    if (r.cast != null) {
      if (!casts) continue;
      const k = r.cast - 1;
      if (casts.light[k] == null || casts.dark[k] == null) continue;      // a layer this run of ui-geometry does not have
      e.alpha = round(casts.light[k]); e.darkAlpha = round(casts.dark[k]);
    } else {
      e.alpha = r.alpha;
      if (r.darkAlpha != null) e.darkAlpha = r.darkAlpha;
      else if (!r.fixed && base.darkScale != null) e.darkAlpha = round(Math.min(1, r.alpha * base.darkScale));
    }
    out[paint.prefix + name] = e;
  }
  return { translucent: out };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2), val = (flag) => (args.includes(flag) ? args[args.indexOf(flag) + 1] : undefined);
  const paint = loadPaint(), layers = val('--layers') ? Number(val('--layers')) : paint.cast.layers;
  if (!Number.isInteger(layers) || layers < 1) { process.stderr.write('request: --layers must be a whole number\n'); process.exit(2); }
  const casts = args.includes('--no-casts') ? null : castAlphas(paint, layers);
  if (!casts && !args.includes('--no-casts')) process.stderr.write('request: ui-geometry is not installed beside this skill, so the cast roles are left out\n');
  const frag = fragment(paint, casts);
  let request = frag;
  if (val('--merge')) {
    const given = JSON.parse(readFileSync(val('--merge'), 'utf8'));
    request = { ...given, translucent: { ...(given.translucent || {}), ...frag.translucent } };
  }
  process.stdout.write(JSON.stringify(request, null, 1) + '\n');
}
