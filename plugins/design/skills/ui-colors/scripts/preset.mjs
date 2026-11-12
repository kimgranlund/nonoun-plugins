#!/usr/bin/env node
// preset.mjs — a named set of seed colours (scripts/presets.json) as source palettes: one scripts/generate.cjs run per colour
// with that colour as its exact tagged source, merged into one output in the generator's own shape, each palette named by
// its colour id (--color-<id>-base-050 … -950 and the Primes). Use for fixed brand sets that aren't an evenly spaced hue
// spectrum; the 12-hue spectrum stays generate.cjs's own `preset: "project"`.
// Usage: node preset.mjs --preset <id> [--request extra.json] --out NEW_DIRECTORY     node preset.mjs --list
//   extra.json may set generate.cjs keys that apply to every palette: output, target, base, prime, toneMin, toneMax, step,
//   falloff, hueBalance, primeBrightnessSteps, primeSpacing (default output "base-primes").
// Exit codes: 0 written, 1 a generator run failed, 2 bad arguments, unknown preset or key, or existing output directory.
import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { parseArgs } from 'node:util';
import { fileURLToPath } from 'node:url';

const here = fileURLToPath(new URL('.', import.meta.url));
const fail = (code, msg) => { process.stderr.write(msg + '\n'); process.exit(code); };
process.stdout.on('error', (e) => { if (e.code === 'EPIPE') process.exit(0); throw e; });
const USAGE = 'usage: node preset.mjs --preset <id> [--request extra.json] --out NEW_DIRECTORY | --list';
let values;
try { ({ values } = parseArgs({ options: { preset: { type: 'string' }, request: { type: 'string' }, out: { type: 'string' }, list: { type: 'boolean' }, help: { type: 'boolean', short: 'h' } } })); } catch (e) { fail(2, e.message + '\n' + USAGE); }
const PRESETS = JSON.parse(readFileSync(here + 'presets.json', 'utf8')); delete PRESETS.$comment;
if (values.help) { console.log(USAGE); process.exit(0); }
if (values.list) { for (const [id, p] of Object.entries(PRESETS)) console.log(`${id} — ${p.name}: ${p.colors.map((c) => c.id).join(', ')}`); process.exit(0); }
if (!values.preset || !values.out) fail(2, USAGE);
const P = PRESETS[values.preset]; if (!P) fail(2, 'unknown preset ' + values.preset + ' (have: ' + Object.keys(PRESETS).join(', ') + ')');
if (existsSync(values.out)) fail(2, 'output directory must be new: ' + values.out);
const ALLOWED = ['output', 'target', 'base', 'prime', 'toneMin', 'toneMax', 'step', 'falloff', 'hueBalance', 'primeBrightnessSteps', 'primeSpacing'];
let extra = {};
if (values.request) { try { extra = JSON.parse(readFileSync(values.request, 'utf8')); } catch (e) { fail(2, 'request: ' + e.message); } const bad = Object.keys(extra).filter((k) => !ALLOWED.includes(k)); if (bad.length) fail(2, 'request: key(s) ' + bad.join(', ') + ' do not apply per palette (allowed: ' + ALLOWED.join(', ') + ')'); }
// Brand sets keep their seeds' punch: a preset may set defaults (field-operator: full Base and Prime chroma, no hue-balance
// art direction, which would pull a brand yellow toward orange); a request file overrides them.
const opts = { output: 'base-primes', target: 'display-p3', ...(P.defaults || {}), ...extra }; // Display P3 by default, as the colour system; extra.json may set target: "srgb"

const hexRgb = (h) => { const m = /^#?([0-9a-f]{6})$/i.exec(h); if (!m) fail(2, 'preset ' + values.preset + ': bad hex ' + h); return [0, 2, 4].map((i) => +(parseInt(m[1].slice(i, i + 2), 16) / 255).toFixed(6)); };
mkdirSync(values.out, { recursive: true });
const work = values.out + '/.runs'; mkdirSync(work);
const palettes = {}, order = [], sources = {}, cssLines = [], notes = [];
try {
  for (const c of P.colors) {
    const rq = work + '/' + c.id + '.json', dir = work + '/' + c.id;
    writeFileSync(rq, JSON.stringify({ source: { colorSpace: 'srgb', components: hexRgb(c.hex), alpha: 1 }, ...opts }));
    execFileSync(process.execPath, [here + 'generate.cjs', '--request', rq, '--out', dir], { stdio: ['ignore', 'ignore', 'pipe'] });
    const d = JSON.parse(readFileSync(dir + '/palettes.json', 'utf8')), key = d.order[0];
    palettes[c.id] = { name: c.name, group: c.group, hex: c.hex, ...d.palettes[key] }; order.push(c.id);
    sources[c.id] = JSON.parse(readFileSync(dir + '/sources.json', 'utf8')).colors[key];
    const css = readFileSync(dir + '/palettes.css', 'utf8').split('\n').filter((l) => /^\s*--/.test(l)).map((l) => l.replace('--' + key + '-', '--color-' + c.id + '-'));
    cssLines.push(`  /* ${c.name} ${c.hex} */`, ...css);
    if (d.notes) notes.push({ id: c.id, notes: d.notes });
  }
} catch (e) { fail(1, 'generation failed: ' + (e.stderr ? String(e.stderr) : e.message)); }
rmSync(work, { recursive: true, force: true });

const out = { kind: 'palette-preset', preset: values.preset, name: P.name, description: P.description, request: opts, generator: 'scripts/generate.cjs per colour (exact tagged source)', order, palettes, notes };
writeFileSync(values.out + '/palettes.json', JSON.stringify(out, null, 2) + '\n');
writeFileSync(values.out + '/sources.json', JSON.stringify({ schemaVersion: 2, colors: sources, sourcePolicies: { version: 'source-policies@1', rules: {} } }, null, 2) + '\n');
const css = `/* ${P.name} — ${P.description} Generated by preset.mjs; do not edit. */\n:root {\n${cssLines.join('\n')}\n}\n`;
writeFileSync(values.out + '/palettes.css', css);
const esc = (s) => String(s).replace(/[&<>"]/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[ch]);
const rows = order.map((id) => { const p = palettes[id], stops = (p.stops || []).map((s) => `<span title="${s.stop}" style="background:var(--color-${id}-base-${String(s.stop).padStart(3, '0')})"></span>`).join(''), primes = (p.prime || []).map((s) => `<i title="${s.name}" style="background:${s.css}"></i>`).join('');
  return `<div class="row"><div class="seed" style="background:${p.hex}"></div><code>${esc(p.name)}<br><small>${p.hex}</small></code><div class="stops">${stops}</div><div class="primes">${primes}</div></div>`; }).join('');
writeFileSync(values.out + '/preview.html', `<!doctype html><meta charset="utf-8"><title>${esc(P.name)}</title><style>${css}
body{margin:0;padding:24px;font:13px system-ui,sans-serif;background:#fff;color:#111}h1{font-size:18px;margin:0 0 4px}p{margin:0 0 16px;color:#555}
.row{display:flex;align-items:center;gap:10px;margin:6px 0}.seed{width:44px;height:44px;border-radius:6px;flex:none}code{width:110px;font-size:12px}small{color:#666}
.stops{display:flex;gap:2px}.stops span{width:28px;height:28px;border-radius:3px}.primes{display:flex;gap:4px;margin-left:12px}.primes i{width:20px;height:20px;border-radius:50%}</style>
<h1>${esc(P.name)}</h1><p>${esc(P.description)} Seed swatch, Base ${(out.palettes[order[0]].stops || []).length} stops, Primes.</p>${rows}`);
console.log(`wrote ${values.out}: ${values.preset} — ${order.length} palettes (${opts.output}), seeds exact: ${order.map((id) => palettes[id].hex).join(' ')}`);
