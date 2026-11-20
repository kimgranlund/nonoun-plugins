// Writes kit/styles/tokens.css from the three sibling skills (docs/specs/css-contract.md, T1 to T6).
//
//   node scripts/tokens.mjs           write the file
//   node scripts/tokens.mjs --check   exit 1 if the file differs from what the siblings and the recipes give now
//
// The sibling skills are looked up in ~/.claude/skills, or in the folder SKILLS_DIR names.
//   colour:    ui-colors' system.css, unchanged, wrapped in the tokens cascade layer (T1)
//   material:  ui-materials' base block from references/fills.md, its Flat values (T2)
//   geometry:  the rows of ui-geometry's derive.mjs that some recipe reads, as literal lengths per density (T3 to T5)
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { reads, trim } from './trim-tokens.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const skills = process.env.SKILLS_DIR ?? path.join(os.homedir(), '.claude/skills');
const check = process.argv.includes('--check');
const config = JSON.parse(fs.readFileSync(path.join(root, 'kit/styles/kit.config.json'), 'utf8'));
const LAYERS = '@layer reset, base, tokens, recipes, utilities;';
const indent = (text, by = '  ') => text.split('\n').map((line) => (line ? by + line : line)).join('\n');
const run = (script, args) => {
  const result = spawnSync(process.execPath, [path.join(skills, script), ...args], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
  if (result.status !== 0) throw new Error(`${script} failed: ${result.stderr || result.stdout}`);
  return result.stdout;
};

// ---------- colour (T1) ----------
function colour() {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'kit-colours-'));
  fs.writeFileSync(path.join(temp, 'request.json'), JSON.stringify(config.colors));
  run('ui-colors/scripts/system.mjs', ['--request', path.join(temp, 'request.json'), '--out', path.join(temp, 'out')]);
  const css = fs.readFileSync(path.join(temp, 'out/system.css'), 'utf8').trimEnd();
  fs.rmSync(temp, { recursive: true, force: true });
  return css;
}

// ---------- material (T2) ----------
/**
 * The selectors under which the colour system changes mode: the root, and each class that sets color-scheme.
 * A material token holds var(--colors-…), and a custom property resolves where it is declared. Declared on the
 * root alone, the tokens would keep the root's colours inside a nested .dark or .light scope.
 */
export function modeScopes(colourCss) {
  const classes = [...colourCss.matchAll(/^(\.[a-z0-9.-]+) \{\n\s+color-scheme:/gm)].map((m) => m[1]);
  return [':root', ...new Set(classes)];
}
function material(colourCss) {
  const fills = fs.readFileSync(path.join(skills, 'ui-materials/references/fills.md'), 'utf8');
  const block = /## Base block[\s\S]*?```css\n([\s\S]*?)```/.exec(fills);
  if (!block) throw new Error('ui-materials/references/fills.md has no base block');
  if (!/^:root \{/m.test(block[1])) throw new Error('the base block of ui-materials no longer starts with ":root {"');
  const scopes = modeScopes(colourCss).join(', ');
  const rings = Object.entries(config.flatRings).filter(([name]) => name.startsWith('--')).map(([name, value]) => `  ${name}: ${value};`).join('\n');
  return `/* Declared on every scope where the colour mode changes, so each token takes that mode's colours. */\n${block[1].trimEnd().replace(/^:root \{/m, scopes + ' {')}\n/* The Flat rings this kit sets (kit.config.json, flatRings). */\n${scopes} {\n${rings}\n}`;
}
/** The names of the material tokens and palette inputs the base block declares. */
export const materialNames = (css) => [...css.matchAll(/(--[a-z0-9-]+)\s*:/g)].map((m) => m[1]);

// ---------- geometry (T3 to T5) ----------
const variable = (id) => '--' + id.replaceAll('.', '-');
/** Rows that are stacked with no gap, so that a hit area cannot grow past the box: the box itself keeps the pointer's target (D96). */
const FLOORED = new Set(['collections.rows.menu-row', 'collections.rows.segment-tab']);
function rows(density) {
  const all = JSON.parse(run('ui-geometry/scripts/derive.mjs', ['--n', String(config.n), '--density', density, ...(config.archetype === undefined ? [] : ['--archetype', String(config.archetype)]), ...(config.kappa === undefined ? [] : ['--kappa', String(config.kappa)]), '--json']));
  const floor = all.find((r) => r.id === 'controls.target.t_hit-pointer')?.px ?? 0;
  return all.map((r) => (FLOORED.has(r.id) && r.px < floor ? { ...r, px: floor } : r));
}
/** Every recipe file of the kit, the framework targets' included. */
function recipeFiles() {
  const out = [];
  for (const dir of fs.readdirSync(path.join(root, 'kit'), { withFileTypes: true })) {
    if (!dir.isDirectory() || dir.name === 'styles') continue;
    for (const id of fs.readdirSync(path.join(root, 'kit', dir.name))) { const file = path.join(root, 'kit', dir.name, id, `${id}.css`); if (fs.existsSync(file)) out.push(file); }
  }
  return out;
}
/** Every custom property a recipe reads. */
function readByRecipes() {
  const components = path.join(root, 'kit/components');
  const names = new Set();
  for (const id of fs.readdirSync(components)) {
    const file = path.join(components, id, `${id}.css`);
    if (!fs.existsSync(file)) continue;
    for (const m of fs.readFileSync(file, 'utf8').matchAll(/var\(\s*(--[A-Za-z0-9_-]+)/g)) names.add(m[1]);
  }
  for (const value of Object.values(config.flatRings)) for (const m of String(value).matchAll(/var\(\s*(--[A-Za-z0-9_-]+)/g)) names.add(m[1]);
  return names;
}
function geometry() {
  const wanted = readByRecipes();
  const byDensity = Object.fromEntries(config.densities.map((d) => [d, Object.fromEntries(rows(d).map((r) => [variable(r.id), r.px]))]));
  const names = Object.keys(byDensity.default).filter((name) => wanted.has(name)).sort();
  const line = (name, px) => `  ${name}: ${px === 0 ? '0' : px + 'px'};`;
  const blocks = [`:root, [data-density="default"] {\n${names.map((n) => line(n, byDensity.default[n])).join('\n')}\n}`];
  for (const density of config.densities.filter((d) => d !== 'default')) {
    const changed = names.filter((n) => byDensity[density][n] !== byDensity.default[n]);
    if (changed.length) blocks.push(`[data-density="${density}"] {\n${changed.map((n) => line(n, byDensity[density][n])).join('\n')}\n}`);
  }
  return { css: blocks.join('\n'), names, all: Object.keys(byDensity.default) };
}

export function build() {
  const g = geometry();
  const c = colour();
  const m = material(c);
  const text = `${LAYERS}

/* Generated by scripts/tokens.mjs from ui-colors, ui-materials and ui-geometry. Do not edit.
   Inputs: kit/styles/kit.config.json. Font size n = ${config.n}px${config.kappa === undefined ? '' : `, curvature κ = ${config.kappa}`}${config.archetype === undefined ? '' : `, archetype ${config.archetype}`}. */

@layer tokens {
  /* ---------- colour: ui-colors system.css, request ${JSON.stringify(config.colors)} ---------- */
${indent(c)}

  /* ---------- material: ui-materials base block, Flat ---------- */
${indent(m)}

  /* ---------- geometry: the ui-geometry rows the recipes read, at n = ${config.n}px ---------- */
${indent(g.css)}
}
`;
  // "tokens": "used" in the config keeps only what the kit's stylesheets reach, and what "keep" names (D103).
  const used = config.tokens === 'used';
  const sheets = [...recipeFiles(), ...['icons.css', 'native.css'].map((f) => path.join(root, 'kit/styles', f)).filter((f) => fs.existsSync(f))].map((f) => fs.readFileSync(f, 'utf8'));
  const out = used ? trim(text, new Set([...reads(sheets), ...readByRecipes()]), config.keep ?? []).text : text;
  return { text: out, geometryNames: g.names, geometryAll: g.all, materialNames: materialNames(m) };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const target = path.join(root, 'kit/styles/tokens.css');
  const { text, geometryNames } = build();
  const current = fs.existsSync(target) ? fs.readFileSync(target, 'utf8') : null;
  if (check) {
    if (current !== text) { console.log(`ERROR kit/styles/tokens.css is ${current === null ? 'missing' : 'stale'}; run node scripts/tokens.mjs`); process.exit(1); }
    console.log('tokens.css matches the sibling skills and the recipes');
  } else {
    fs.writeFileSync(target, text);
    console.log(`wrote kit/styles/tokens.css: ${text.length} bytes, ${geometryNames.length} geometry variable(s)`);
  }
}
