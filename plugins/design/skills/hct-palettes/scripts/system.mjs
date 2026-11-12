#!/usr/bin/env node
// system.mjs — a complete colour system from one request (contract: ../references/system.md).
// Per mode (light, dark, high-contrast light and dark, dim, or your own): 12-step ramps placed by APCA contrast for twelve
// perceptually even hues plus a tinted neutral, transparent steps, semantic roles, anchors and endpoints, solids solved to a
// light (white first) or dark label per family with an even APCA key run 9→12, a data series. Mode-independent: a 050–950 tonal scale per family (and optional Primes) from the
// bundled HCT source-palette generator, seeded with each family's solid. Outputs CSS (sRGB with a Display P3 upgrade),
// JSON, DTCG, a preview, and optionally a diverging ramp, a Tailwind 4 theme, Figma variables and a 1280 × 960 showcase sheet.
// Contrast is APCA only (|Lc| from system/contrast.js › apcaLc, text first, background second), at the thresholds below.
// Checks it reports (it never moves a colour to pass them): an APCA contrast matrix per mode, the data series under
// simulated colour-vision deficiency, and how closely the tonal 050–950 layer agrees with the 12-step ramps.
// Usage: node system.mjs --request request.json --out NEW_DIRECTORY
// Exit codes: 0 written, 1 generation failed, 2 bad arguments or request.
import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { parseArgs } from 'node:util';
import { fileURLToPath } from 'node:url';
import { endpointVars, families, generateSpectrum, normalizeSpectrum, resolveRoles, spectrumDiagnostics, spectrumOverrides, alphaRamps, apcaLc, roleVariables, ramps as rampsOf, parseAnchorColor, SCALE_ROLES } from './system/index.js';
import { rampVar, rampName, ROLE_STEPS, roleStep, withAlpha, selectionVars } from './system/roles.js';
import { clampChroma, applyAnchors, shapeKeys, deriveKeys, deriveNeutral } from './system/anchors.js';
import { DEFAULT_TARGETS } from './system/contrast.js';
import { showcaseHtml, mountable } from './system/showcase.js';

const USAGE = 'usage: node system.mjs --request request.json --out NEW_DIRECTORY';
const fail = (code, msg) => { process.stderr.write(msg + '\n'); process.exit(code); };
process.stdout.on('error', (e) => { if (e.code === 'EPIPE') process.exit(0); throw e; });
let values;
try { ({ values } = parseArgs({ options: { request: { type: 'string' }, out: { type: 'string' }, help: { type: 'boolean', short: 'h' } } })); } catch (e) { fail(2, e.message + '\n' + USAGE); }
if (values.help) { console.log(USAGE); process.exit(0); }
if (!values.request || !values.out) fail(2, USAGE);
if (existsSync(values.out)) fail(2, 'output directory must be new: ' + values.out);
let req;
try { req = JSON.parse(readFileSync(values.request, 'utf8')); } catch (e) { fail(2, 'request: ' + e.message); }
if (!req || typeof req !== 'object' || Array.isArray(req)) fail(2, 'request: must be a JSON object');

// ── Request ───────────────────────────────────────────────────────────────────────────────────────────────
const KEYS = ['apca', 'brightHues', 'neutrals', 'settings', 'roles', 'anchors', 'endpoints', 'scope', 'modes', 'extraModes', 'selectors', 'lightDark', 'p3Fallback', 'alpha', 'series', 'tonal', 'primes', 'diverging', 'tailwind', 'figma', 'dtcg', 'split', 'preset', 'familyNames', 'tonalRoles', 'showcase'];
const unknown = Object.keys(req).filter((k) => !KEYS.includes(k));
if (unknown.length) fail(2, 'request: unknown key(s) ' + unknown.join(', ') + ' (allowed: ' + KEYS.join(', ') + ')');
for (const k of ['lightDark', 'p3Fallback', 'alpha', 'series', 'primes', 'diverging', 'tailwind', 'figma', 'dtcg', 'split', 'tonalRoles', 'showcase']) if (k in req && typeof req[k] !== 'boolean') fail(2, 'request: ' + k + ' must be true or false');
// Presets fill keys the request leaves out; an explicit key always wins.
const PRESETS = { minimal: { extraModes: false, alpha: false, tonal: false } };
if ('preset' in req && !(req.preset in PRESETS)) fail(2, 'request: preset must be one of ' + Object.keys(PRESETS).join(', '));
const R0 = req, eff = { ...(PRESETS[req.preset] || {}), ...req };
// Ramp shape default: tints and borders (steps 1–8) keep 76% of the chroma and the solids and text (9–12) get double, so a ramp
// reads as quiet surfaces with punchy keys. The engine's own defaults (base 100, keyIntensity 100) give every step similar
// chroma; pass them explicitly in settings to get that flat ramp. Explicit values (top level or per mode) always win.
const RAMP_SHAPE = { base: 76, keyIntensity: 200 };
eff.settings = { ...RAMP_SHAPE, ...(eff.settings || {}) };
const familyNames = eff.familyNames ?? 'hue';
if (!['hue', 'index'].includes(familyNames)) fail(2, 'request: familyNames must be "hue" (families named after their hue, the default) or "index" (hue-1…hue-N)');
const MODE_KEYS = ['settings', 'roles', 'anchors', 'endpoints'];
const DEFAULT_EXTRA = [{ id: 'light-contrast', scheme: 'light', contrast: true }, { id: 'dark-contrast', scheme: 'dark', contrast: true }, { id: 'dim', scheme: 'dark', settings: { darkTone: 14 } }];
if ('extraModes' in eff && eff.extraModes !== false && !Array.isArray(eff.extraModes)) fail(2, 'request: extraModes must be false or a list of modes');
const extra = eff.extraModes === false ? [] : Array.isArray(eff.extraModes) ? eff.extraModes : DEFAULT_EXTRA;
const MODES = [{ id: 'light', scheme: 'light' }, { id: 'dark', scheme: 'dark' }, ...extra];
const ids = new Set();
for (const m of MODES) {
  if (!m || typeof m.id !== 'string' || !/^[a-z][a-z0-9-]*$/.test(m.id)) fail(2, 'request: every mode needs an id of lowercase letters, digits and hyphens');
  if (ids.has(m.id)) fail(2, 'request: duplicate mode ' + m.id); ids.add(m.id);
  if (m.id === 'base' && eff.split) fail(2, 'request: a mode may not be called "base" with split (system.base.css is the shared file)');
  if (m.scheme !== 'light' && m.scheme !== 'dark') fail(2, 'request: mode ' + m.id + ' needs scheme "light" or "dark"');
  const bad = Object.keys(m).filter((k) => !['id', 'scheme', 'contrast', ...MODE_KEYS].includes(k)); if (bad.length) fail(2, 'request: mode ' + m.id + ' has unknown key(s) ' + bad.join(', '));
}
if (eff.modes != null && (typeof eff.modes !== 'object' || Array.isArray(eff.modes))) fail(2, 'request: modes must be an object of { "<mode id>": overrides }');
for (const [id, o] of Object.entries(eff.modes || {})) { if (!ids.has(id)) fail(2, 'request: modes.' + id + ' is not a mode (have ' + [...ids].join(', ') + ')'); const bad = Object.keys(o).filter((k) => !MODE_KEYS.includes(k)); if (bad.length) fail(2, 'request: modes.' + id + ' has unknown key(s) ' + bad.join(', ')); }
const selectors = eff.selectors ?? 'class';
if (!['class', 'attribute'].includes(selectors)) fail(2, 'request: selectors must be "class" or "attribute"');
const opt = { alpha: eff.alpha !== false, series: eff.series !== false, tonal: eff.tonal !== false, primes: !!eff.primes, diverging: !!eff.diverging, tailwind: !!eff.tailwind, figma: !!eff.figma, dtcg: eff.dtcg !== false, lightDark: !!eff.lightDark, split: !!eff.split, tonalRoles: !!eff.tonalRoles, showcase: !!eff.showcase };
// The showcase mounts every mode on its own panel, so the scope must be a selector an element can be given: classes and attributes.
if (opt.showcase && eff.scope != null && !(typeof eff.scope === 'string' && mountable(eff.scope))) fail(2, 'request: showcase needs scope to be classes and/or attributes (.brand, [data-theme=brand]), so each mode panel can carry it');
// ── APCA thresholds ───────────────────────────────────────────────────────────────────────────────────────
// |Lc| floors, the most lenient level APCA gives each use. Contrast modes add APCA_CONTRAST_STEP to each, unless the
// request's apca.contrast names its own. Overridable per key: { apca: { solid, text, hint, ui, series, contrast: { … } } }.
const APCA_DEFAULTS = {
  solid: 45,  // label text on a solid (button, chip text): Lc 45, APCA's floor for large or bold text
  text: 45,   // text pairs in the matrix (fg on surfaces, role fg): Lc 45, the same large/bold-text floor
  hint: 30,   // hint, placeholder and subtle text: Lc 30, APCA's absolute minimum for any text
  ui: 15,     // non-text (control border, focus ring, dividers): Lc 15, APCA's floor for a perceivable non-text edge
  series: 30, // data marks against the chart surface: Lc 30, APCA's minimum for large solid non-text marks
};
const APCA_CONTRAST_STEP = 15;
const SOLVE_MARGIN = 0.5; // every solve aims this far over its floor (chroma clamping, 8-bit rounding of what ships)
const APCA_KEYS = Object.keys(APCA_DEFAULTS);
const apcaNum = (v, where) => { if (typeof v !== 'number' || !Number.isFinite(v) || v < 0 || v > 108) fail(2, `request: ${where} must be a number from 0 to 108 (APCA |Lc|)`); return v; };
function apcaOf(a) {
  if (a == null) a = {};
  if (typeof a !== 'object' || Array.isArray(a)) fail(2, 'request: apca must be an object of { ' + APCA_KEYS.join(', ') + ', contrast }');
  const bad = Object.keys(a).filter((k) => ![...APCA_KEYS, 'contrast'].includes(k)); if (bad.length) fail(2, 'request: apca has unknown key(s) ' + bad.join(', ') + ' (allowed: ' + [...APCA_KEYS, 'contrast'].join(', ') + ')');
  const normal = Object.fromEntries(APCA_KEYS.map((k) => [k, k in a ? apcaNum(a[k], 'apca.' + k) : APCA_DEFAULTS[k]]));
  const c = a.contrast;
  if (c != null && (typeof c !== 'object' || Array.isArray(c))) fail(2, 'request: apca.contrast must be an object of { ' + APCA_KEYS.join(', ') + ' }');
  if (c) { const badC = Object.keys(c).filter((k) => !APCA_KEYS.includes(k)); if (badC.length) fail(2, 'request: apca.contrast has unknown key(s) ' + badC.join(', ')); }
  const contrast = Object.fromEntries(APCA_KEYS.map((k) => [k, c && k in c ? apcaNum(c[k], 'apca.contrast.' + k) : Math.min(108, normal[k] + APCA_CONTRAST_STEP)]));
  return { normal, contrast };
}
const APCA = apcaOf(eff.apca);
// Bright hues, as in Radix: an accent whose step-9 OKLCH hue lies in this window (degrees, inclusive; from > to wraps through
// 0°) always takes the dark label with its solid at the hue's gamut cusp, in every mode, whether or not white would pass —
// yellow, amber and lime read as lemon, gold and chartreuse, not mustard and olive. Request key: brightHues [from, to] or false.
const BRIGHT_HUES = [70, 125];
let brightHues = BRIGHT_HUES;
if ('brightHues' in eff) {
  const b = eff.brightHues;
  if (b === false) brightHues = null;
  else if (Array.isArray(b) && b.length === 2 && b.every((x) => typeof x === 'number' && Number.isFinite(x) && x >= 0 && x <= 360)) brightHues = b;
  else fail(2, 'request: brightHues must be false or [from, to], two OKLCH hues in degrees from 0 to 360 (from > to wraps through 0°)');
}
// Neutrals split (opt-in): three neutral families instead of one — ground (the page), surface (the material on it: cards,
// panels, controls, borders) and ink (text) — each a Radix grey { from } or a generated tinted neutral { tint, neutralFrom, hue }.
// cross swaps the ground and surface sources in dark schemes. Without the key the system is exactly the one-neutral system.
const GRAY_NAMES = ['Gray', 'Mauve', 'Slate', 'Sage', 'Olive', 'Sand'];
const NEUTRAL_ROLES_SPLIT = ['ground', 'surface', 'ink'];
let neutrals = null;
if ('neutrals' in eff) {
  const n = eff.neutrals, where = 'request: neutrals';
  if (!n || typeof n !== 'object' || Array.isArray(n)) fail(2, where + ' must be an object { ground?, surface?, ink?, cross? }');
  const bad = Object.keys(n).filter((k) => ![...NEUTRAL_ROLES_SPLIT, 'cross'].includes(k)); if (bad.length) fail(2, `${where} has unknown key(s) ${bad.join(', ')} (allowed: ground, surface, ink, cross)`);
  if ('cross' in n && typeof n.cross !== 'boolean') fail(2, where + '.cross must be true or false');
  const spec = (k) => {
    if (!(k in n)) return null;
    const v = n[k], w = `${where}.${k}`;
    if (!v || typeof v !== 'object' || Array.isArray(v)) fail(2, `${w} must be { from: "${GRAY_NAMES.join('" | "')}" } or a generated neutral { tint?, neutralFrom?, hue? }`);
    if ('from' in v) {
      const extra = Object.keys(v).filter((x) => x !== 'from'); if (extra.length) fail(2, `${w}: from takes no other key (${extra.join(', ')})`);
      if (!GRAY_NAMES.includes(v.from)) fail(2, `${w}.from must be one of ${GRAY_NAMES.join(', ')}`);
      return { from: v.from };
    }
    const extra = Object.keys(v).filter((x) => !['tint', 'neutralFrom', 'hue'].includes(x)); if (extra.length) fail(2, `${w} has unknown key(s) ${extra.join(', ')} (allowed: from, or tint, neutralFrom, hue)`);
    if ('tint' in v && !(Number.isInteger(v.tint) && v.tint >= 0 && v.tint <= 100)) fail(2, `${w}.tint must be an integer from 0 to 100`);
    if ('neutralFrom' in v && !(Number.isInteger(v.neutralFrom) && v.neutralFrom >= 0 && v.neutralFrom <= 11)) fail(2, `${w}.neutralFrom must be an integer from 0 to 11 (the accent index)`);
    if ('hue' in v && !(typeof v.hue === 'number' && Number.isFinite(v.hue) && v.hue >= 0 && v.hue <= 360)) fail(2, `${w}.hue must be an HCT hue from 0 to 360`);
    if ('hue' in v && 'neutralFrom' in v) fail(2, `${w}: give hue or neutralFrom, not both`);
    return { ...v };
  };
  neutrals = { ground: spec('ground'), surface: spec('surface'), ink: spec('ink'), cross: !!n.cross };
}
const inBright = (H) => { if (!brightHues) return false; const h = ((H % 360) + 360) % 360, [a, b] = brightHues; return a <= b ? h >= a && h <= b : h >= a || h <= b; };
const TONAL_KEYS = ['toneMin', 'toneMax', 'step', 'base', 'prime', 'falloff', 'hueBalance'];
if (eff.tonal != null && typeof eff.tonal !== 'boolean' && (typeof eff.tonal !== 'object' || Array.isArray(eff.tonal))) fail(2, 'request: tonal must be true, false or an object');
if (typeof eff.tonal === 'object' && eff.tonal) { const bad = Object.keys(eff.tonal).filter((k) => !TONAL_KEYS.includes(k)); if (bad.length) fail(2, 'request: tonal has unknown key(s) ' + bad.join(', ')); }
// hueBalance false by default: the seed is a 12-step solid the engine has already hue-balanced, and a second pass in the
// source-palette recipe drifts dark yellows and oranges by up to ~11° away from the ramps (references/system-notice.md).
const tonalOpt = { toneMin: 10, toneMax: 98, step: 50, hueBalance: false, ...(typeof eff.tonal === 'object' && eff.tonal ? eff.tonal : {}) };
if (opt.tonalRoles && !opt.tonal) fail(2, 'request: tonalRoles needs the tonal layer (tonal is false)');

// Hue and hue set rename HCT families, so the default names reject a mode that changes them; index names don't.
const HUE_KEYS = ['hue', 'hueSet', 'quadStart'];
const topSettings = eff.settings || {};
for (const m of MODES) {
  const o = (eff.modes || {})[m.id] || {}, merged = { ...topSettings, ...(m.settings || {}), ...(o.settings || {}) };
  const moved = HUE_KEYS.filter((k) => JSON.stringify(merged[k]) !== JSON.stringify(topSettings[k]));
  if (moved.length && familyNames !== 'index') fail(2, 'request: mode ' + m.id + ' changes ' + moved.join(', ') + ' — family names follow the hues, so set ' + moved.join(', ') + ' at the top level, or add "familyNames": "index" to name families hue-1…hue-N in every mode');
}

// Anchor colours: #rrggbb, a CSS colour string (oklch(), oklab(), color(srgb | display-p3 …)) or a tagged colour
// { colorSpace: oklch | oklab | srgb | display-p3, components: [3 numbers], alpha: 1 }. All become a CSS string the engine reads.
const TAGGED = { oklch: (c) => `oklch(${c[0]} ${c[1]} ${c[2]})`, oklab: (c) => `oklab(${c[0]} ${c[1]} ${c[2]})`, srgb: (c) => `color(srgb ${c.join(' ')})`, 'display-p3': (c) => `color(display-p3 ${c.join(' ')})` };
function anchorColor(v, where) {
  if (typeof v === 'string') {
    const s = v.trim(), a = /\/\s*([\d.]+%?)\s*\)$/.exec(s);
    if (a && (a[1].endsWith('%') ? parseFloat(a[1]) / 100 : parseFloat(a[1])) !== 1) fail(2, `request: ${where} must be opaque (alpha 1)`);
    if (!parseAnchorColor(s)) fail(2, `request: ${where} is not a readable colour: ${v} (use #rrggbb, oklch(…), oklab(…), color(display-p3 …) or a tagged colour)`);
    return s;
  }
  if (v && typeof v === 'object' && !Array.isArray(v)) {
    const bad = Object.keys(v).filter((k) => !['colorSpace', 'components', 'alpha'].includes(k)); if (bad.length) fail(2, `request: ${where} has unknown key(s) ${bad.join(', ')}`);
    if (!(v.colorSpace in TAGGED)) fail(2, `request: ${where}.colorSpace must be one of ${Object.keys(TAGGED).join(', ')}`);
    if (!Array.isArray(v.components) || v.components.length !== 3 || !v.components.every((x) => typeof x === 'number' && Number.isFinite(x))) fail(2, `request: ${where}.components must be three numbers`);
    if ((v.alpha ?? 1) !== 1) fail(2, `request: ${where}.alpha must be 1`);
    const s = TAGGED[v.colorSpace](v.components); if (!parseAnchorColor(s)) fail(2, `request: ${where} is not a readable colour`);
    return s;
  }
  fail(2, `request: ${where} must be #rrggbb, a CSS colour string or { colorSpace, components, alpha: 1 }`);
}
const ANCHOR_KEYS = ['role', 'value', 'dark', 'step', 'darkStep', 'reach', 'name'];
function anchorList(list, where) {
  if (list == null) return list;
  if (!Array.isArray(list)) fail(2, `request: ${where} must be a list`);
  return list.map((a, i) => {
    const w = `${where}[${i}]`;
    if (!a || typeof a !== 'object' || typeof a.role !== 'string') fail(2, `request: ${w} needs a role`);
    const bad = Object.keys(a).filter((k) => !ANCHOR_KEYS.includes(k)); if (bad.length) fail(2, `request: ${w} has unknown key(s) ${bad.join(', ')}`);
    if (a.value == null) fail(2, `request: ${w} needs a value`);
    return { ...a, value: anchorColor(a.value, w + '.value'), ...(a.dark != null ? { dark: anchorColor(a.dark, w + '.dark') } : {}), source: { value: a.value, ...(a.dark != null ? { dark: a.dark } : {}) } };
  });
}
const anchorsTop = anchorList(eff.anchors, 'anchors');
for (const m of MODES) m.anchors = anchorList(m.anchors, `mode ${m.id}.anchors`);
const modeOverrides = Object.fromEntries(Object.entries(eff.modes || {}).map(([id, o]) => [id, { ...o, anchors: anchorList(o.anchors, `modes.${id}.anchors`) }]));
// The surface anchor pins the surface family (neutrals only); a neutral anchor shapes the run's own neutral, which is the ink
// only while neutrals.ink is left to it; roles.neutral would move the page roles the split owns.
for (const [w, list] of [['anchors', anchorsTop], ...MODES.map((m) => [`mode ${m.id}.anchors`, m.anchors]), ...Object.entries(modeOverrides).map(([id, o]) => [`modes.${id}.anchors`, o.anchors])]) for (const a of list || []) {
  if (a.role === 'surface' && !neutrals) fail(2, `request: ${w}: a surface anchor needs the neutrals key (it pins the surface family)`);
  if (a.role === 'surface') { const k = ['step', 'darkStep', 'reach'].filter((x) => x in a); if (k.length) fail(2, `request: ${w}: a surface anchor pins step 1; ${k.join(', ')} not allowed`); }
  if (a.role === 'neutral' && neutrals?.ink) fail(2, `request: ${w}: a neutral anchor shapes the default neutral, but neutrals.ink replaces it; anchor ground/ink instead`);
}
if (neutrals) for (const [w, r] of [['roles', eff.roles], ...MODES.map((m) => [`mode ${m.id}.roles`, m.roles]), ...Object.entries(eff.modes || {}).map(([id, o]) => [`modes.${id}.roles`, o.roles])]) if (r && 'neutral' in r) fail(2, `request: ${w}.neutral is not allowed with neutrals (the split names the ground, surface and ink families)`);

// ── Colour helpers ────────────────────────────────────────────────────────────────────────────────────────
const toLin = ([L, C, H], gamut = 'srgb') => { const a = C * Math.cos(H * Math.PI / 180), b = C * Math.sin(H * Math.PI / 180);
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3;
  const rgb = [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s];
  return gamut === 'display-p3' ? [0.8224621 * rgb[0] + 0.177538 * rgb[1], 0.0331941 * rgb[0] + 0.9668058 * rgb[1], 0.0170827 * rgb[0] + 0.0723974 * rgb[1] + 0.9105199 * rgb[2]] : rgb; };
const clamp01 = (v) => Math.min(1, Math.max(0, v));
const Y = (c) => { const v = toLin(c).map(clamp01); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
const enc = (v) => (v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055);
const dec = (v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
const rgbOf = (c, gamut = 'srgb') => toLin(c, gamut).map((v) => enc(clamp01(v)));
const hex = (c) => '#' + rgbOf(c).map((v) => Math.round(v * 255).toString(16).padStart(2, '0')).join('');
const hexRgb = (rgb) => '#' + rgb.map((v) => Math.round(clamp01(v) * 255).toString(16).padStart(2, '0')).join('');
const toneOf = (c) => { const y = Y(c); return y > 0.008856 ? 116 * Math.cbrt(y) - 16 : 903.3 * y; };
const okCss = ([L, C, H]) => 'oklch(' + +L.toFixed(4) + ' ' + +C.toFixed(4) + ' ' + +(((H % 360) + 360) % 360).toFixed(2) + ')';
const parseOk = (s) => { const m = /oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)/.exec(s || ''); return m ? [+m[1], +m[2], +m[3]] : null; };
const toSrgbCss = (s) => s.replace(/oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)/g, (_, L, C, H) => okCss([+L, clampChroma(+L, +C, +H, 'srgb'), +H]));
const okLab = ([L, C, H]) => [L, C * Math.cos(H * Math.PI / 180), C * Math.sin(H * Math.PI / 180)];
const dE = (p, q) => { const a = okLab(p), b = okLab(q); return 100 * Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]); };
const labOfLinear = (rgb) => { const lms = [0.4122214708 * rgb[0] + 0.5363325363 * rgb[1] + 0.0514459929 * rgb[2], 0.2119034982 * rgb[0] + 0.6806995451 * rgb[1] + 0.1073969566 * rgb[2], 0.0883024619 * rgb[0] + 0.2817188376 * rgb[1] + 0.6299787005 * rgb[2]].map(Math.cbrt);
  return [0.2104542553 * lms[0] + 0.793617785 * lms[1] - 0.0040720468 * lms[2], 1.9779984951 * lms[0] - 2.428592205 * lms[1] + 0.4505937099 * lms[2], 0.0259040371 * lms[0] + 0.7827717662 * lms[1] - 0.808675766 * lms[2]]; };
const inGamut = ([L, C, H], gamut) => clampChroma(L, C, H, gamut) >= C - 1e-9;
const r2 = (x) => Math.round(x * 100) / 100, r1 = (x) => Math.round(x * 10) / 10;

// ── Generate every mode ───────────────────────────────────────────────────────────────────────────────────
const merge = (a, b) => ({ ...(a || {}), ...(b || {}) });
const scaleTargets = (t, k) => { const out = []; let prev = 0; for (const v of t) { const n = Math.min(108, Math.max(v * k, prev + 0.5)); out.push(+n.toFixed(2)); prev = n; } return out; };
// familyNames "index": accents become hue-1…hue-N in hue order from the first hue (neutrals keep their names), so a mode
// may change hue or hue set and still share every family name with the others.
const indexMap = (g) => { const f = families(g), map = {}; f.accents.forEach((a, i) => { map[a] = 'hue-' + (i + 1); }); f.neutrals.forEach((n) => { map[n] = n; }); return map; };
function renameData(d, map) {
  const rk = (o) => Object.fromEntries(Object.entries(o).map(([k, v]) => [map[k] ?? k, v])), rn = (x) => map[x] ?? x;
  for (const s of ['light', 'dark']) {
    if (d.schemes?.[s]) d.schemes[s] = rk(d.schemes[s]);
    if (d.checks?.[s]?.rows) d.checks[s].rows = rk(d.checks[s].rows);
    const md = d.metadata?.[s]; if (!md) continue;
    if (md.accents) md.accents = md.accents.map(rn); if (md.neutrals) md.neutrals = md.neutrals.map(rn);
    if (md.pairs) md.pairs = Object.fromEntries(Object.entries(md.pairs).map(([k, v]) => [rn(k), v && typeof v === 'object' ? Object.fromEntries(Object.entries(v).map(([a, b]) => [a, typeof b === 'string' ? rn(b) : b])) : v]));
  }
}
// An anchor colour outside the output gamut is clipped into it (chroma only, at its OKLCH lightness and hue) before the
// engine sees it, so solids are solved on what will be shown. A Display P3 colour with target display-p3 stays exact.
function gamutAnchors(list, target) {
  if (!list) return { list, clips: new Map() };
  const clips = new Map();
  const one = (s) => { const p = parseAnchorColor(s), [L, C, H] = p.oklch, inSrgb = inGamut(p.oklch, 'srgb');
    if (inGamut(p.oklch, target)) { clips.set(s, { target, inTarget: true, inSrgb }); return s; }
    const c = clampChroma(L, C, H, target), v = `oklch(${L} ${c} ${H})`; clips.set(v, { target, inTarget: false, inSrgb, requested: s, clipDE: r2(dE(p.oklch, [L, c, H])) }); return v; };
  return { list: list.map((a) => ({ ...a, value: one(a.value), ...(a.dark ? { dark: one(a.dark) } : {}) })), clips };
}
const cache = new Map();
// The engine's anchoredSpectrum (system/index.js) without its last step, solveSolids, which darkens every step 9 until a fixed
// light label reaches 4.6:1 (WCAG 2). The ramps come back as generated; solveSolidLabels below solves solids per family (APCA).
function prepare(g, roles, anchors) {
  if (!anchors.length) return { data: shapeKeys(g), roles, report: [], solidSteps: { light: {}, dark: {} }, pins: { light: {}, dark: {} } };
  const targets = { light: g.settings.targetsLight ?? [...DEFAULT_TARGETS.light], dark: g.settings.targetsDark ?? [...DEFAULT_TARGETS.dark] };
  const r = applyAnchors(g, roles, anchors, targets), SK = deriveKeys(shapeKeys(r.data, r.pins), r.pins);
  const data = anchors.some((a) => a.role === 'ground' || a.role === 'ink') && !anchors.some((a) => a.role === 'neutral') ? deriveNeutral(SK, r.roles.neutral) : SK;
  return { data, roles: r.roles, report: r.report, solidSteps: r.solidSteps, pins: r.pins }; // pins: anchored steps 9–12 per scheme and family
}
function run(settings, roles, anchors) {
  const key = JSON.stringify([settings, roles, anchors]); if (cache.has(key)) return cache.get(key);
  const s = normalizeSpectrum(settings), g = generateSpectrum(spectrumOverrides(s));
  let map = null, wanted = roles || {};
  if (familyNames === 'index') { map = indexMap(g); const inv = Object.fromEntries(Object.entries(map).map(([a, b]) => [b, a])); wanted = Object.fromEntries(Object.entries(wanted).map(([r, f]) => [r, inv[f] ?? f])); }
  const engineAnchors = (anchors || []).map(({ source: _s, ...a }) => a);
  const r = prepare(g, resolveRoles(g, wanted), engineAnchors);
  if (r.data === g) r.data = structuredClone(g); // shapeKeys passes unshaped data through; keep the cached generation untouched
  if (map) { renameData(r.data, map); r.roles = Object.fromEntries(Object.entries(r.roles).map(([k, f]) => [k, map[f] ?? f])); for (const x of r.report) x.family = map[x.family] ?? x.family; for (const sc of ['light', 'dark']) r.pins[sc] = Object.fromEntries(Object.entries(r.pins[sc] || {}).map(([f, st]) => [map[f] ?? f, st])); }
  const v = { settings: s, generated: g, ...r }; cache.set(key, v); return v;
}
// ── Neutrals split: ground / surface / ink ────────────────────────────────────────────────────────────────
// Each family is the neutral of one engine run at the mode's own settings (contrast targets and page tones included): a Radix
// grey is that run with the grey added to settings.grays, a generated neutral is that run with mat tinted and its tint and
// neutralFrom (hue: the accent nearest that HCT hue). The engine makes one tinted neutral per run, so every distinct spec is
// its own run (cached). The surface family is generated against a page lifted by SURFACE_LIFT (CIE L* tone): lighter than
// the page in light schemes (paper cards on a toned page; darker when the page has no headroom) and lighter in dark schemes
// (material lifts toward the light), so a card separates from the page by lightness, not only by hue. cross swaps which
// source fills ground and surface in dark schemes; the roles keep their families.
const SURFACE_LIFT = { light: 2.5, dark: 4 };
// Separation: surface step 1 against ground step 1, OKLab ΔE × 100. 2 is one just-noticeable difference (CSS Color 4 gamut
// mapping's JND, ΔEOK 0.02): under it a card can't be told from the page without its border. APCA Lc is reported beside it
// (informational), since a warm page and a cool card can separate at almost no Lc.
const SEPARATION_MIN = 2;
const SPLIT_ANCHORS = ['ground', 'ink', 'surface'];
function liftTones(s) {
  const up = Math.min(100, s.toneMax + SURFACE_LIFT.light), dn = Math.min(20, s.darkTone + SURFACE_LIFT.dark);
  return { toneMax: up - s.toneMax >= 1.5 ? up : s.toneMax - SURFACE_LIFT.light, darkTone: dn - s.darkTone >= 2 ? dn : s.darkTone - SURFACE_LIFT.dark };
}
const hueGap = (a, b) => { const d = Math.abs(a - b) % 360; return Math.min(d, 360 - d); };
function specSettings(spec, s, gen) {
  if (!spec) return {};
  if (spec.from) return { grays: [...new Set([...(s.grays || []), spec.from])] };
  let nf = spec.neutralFrom ?? s.neutralFrom;
  if (spec.hue != null) { const acc = families(gen).accents.slice(0, 12), h = (f) => gen.schemes.light[f][8].hct?.[0] ?? gen.schemes.light[f][8].oklch[2];
    nf = acc.reduce((b, f, i) => (hueGap(h(f), spec.hue) < hueGap(h(acc[b]), spec.hue) ? i : b), 0); }
  return { mat: 'tinted', tint: spec.tint ?? s.tint, neutralFrom: nf };
}
const specText = (spec, s, gen) => { if (!spec) return 'the run\'s neutral'; if (spec.from) return 'Radix ' + spec.from; const x = specSettings(spec, s, gen); return `tinted ${x.tint}% from ${families(gen).accents[x.neutralFrom]} (neutralFrom ${x.neutralFrom})`; };
function rampFor(spec, lift, sc, ctx) {
  if (!spec && !lift) return structuredClone(ctx.data.schemes[sc].neutral); // the run's own neutral, neutral anchors included
  const r = run({ ...ctx.s, ...specSettings(spec, ctx.s, ctx.gen), ...(lift ? liftTones(ctx.s) : {}) }, ctx.roles, []);
  const key = spec?.from ? (spec.from === 'Gray' ? 'gray-base' : spec.from.toLowerCase()) : 'neutral', ramp = r.data.schemes[sc][key];
  if (!ramp) throw new Error('neutrals: the engine made no ' + key + ' family');
  return structuredClone(ramp);
}
// Pins one neutral anchor end with the engine's own ground/ink pin (applyAnchors on a one-family stand-in): `ground` pins the
// stand-in's light step 1 and dark step 12, `ink` its light step 12 and dark step 1, easing the neighbours as for the neutral.
const pinEnds = (data, anchor, light, dark) => { const r = applyAnchors({ settings: data.settings, schemes: { light: { neutral: light }, dark: { neutral: dark } } }, { neutral: 'neutral' }, [anchor], { light: [], dark: [] });
  return { light: r.data.schemes.light.neutral, dark: r.data.schemes.dark.neutral, report: r.report[0] }; };
function splitNeutrals(data, s, gen, roles, anchors) {
  const N = neutrals, ctx = { data, s, gen, roles }, built = {}, sources = {}, lifted = liftTones(s);
  for (const sc of ['light', 'dark']) {
    const cross = N.cross && sc === 'dark', gSpec = cross ? N.surface : N.ground, sSpec = cross ? N.ground : N.surface;
    built[sc] = { ground: rampFor(gSpec, false, sc, ctx), surface: rampFor(sSpec, true, sc, ctx), ink: N.ink ? rampFor(N.ink, false, sc, ctx) : data.schemes[sc].neutral };
    const pageTone = sc === 'light' ? s.toneMax : s.darkTone, cardTone = sc === 'light' ? lifted.toneMax : lifted.darkTone;
    sources[sc] = { ground: { spec: cross ? 'surface' : 'ground', source: specText(gSpec, s, gen), pageTone }, surface: { spec: cross ? 'ground' : 'surface', source: specText(sSpec, s, gen), pageTone: cardTone }, ink: { spec: 'ink', source: specText(N.ink, s, gen), pageTone } };
  }
  for (const sc of ['light', 'dark']) { const S = data.schemes[sc]; S.neutral = built[sc].ink; S.ground = built[sc].ground; S.surface = built[sc].surface;
    const md = data.metadata?.[sc]; if (md?.neutrals) for (const f of ['ground', 'surface']) if (!md.neutrals.includes(f)) md.neutrals.push(f); }
  // Anchors: ground = the light page (ground 1) and dark text (ink 12); ink = light text (ink 12) and the dark page (ground 1);
  // surface = the light card (surface 1) and, with `dark`, the dark card exactly, else the anchor's hue and chroma at the dark card's lightness.
  const report = [], strongInk = {}, L = data.schemes.light, D = data.schemes.dark;
  for (const a of anchors) {
    if (a.role === 'ground') { const p = pinEnds(data, a, L.ground, D.neutral); L.ground = p.light; D.neutral = p.dark; strongInk.dark = true; report.push({ ...p.report, family: 'ground', dark: { ...p.report.dark, family: 'ink' } }); }
    else if (a.role === 'ink') { const p = pinEnds(data, a, L.neutral, D.ground); L.neutral = p.light; D.ground = p.dark; strongInk.light = true; report.push({ ...p.report, family: 'ink', dark: { ...p.report.dark, family: 'ground' } }); }
    else if (a.role === 'surface') {
      const want = parseAnchorColor(a.value).oklch, d1 = D.surface[0].oklch, before = dE(want, L.surface[0].oklch);
      const dv = a.dark ?? `oklch(${d1[0]} ${clampChroma(d1[0], want[1], want[2], s.target)} ${want[2]})`;
      L.surface = pinEnds(data, { role: 'ground', value: a.value, dark: a.value }, L.surface, structuredClone(D.surface)).light;
      D.surface = pinEnds(data, { role: 'ink', value: dv, dark: dv }, structuredClone(L.surface), D.surface).dark;
      const lcOnPage = (c, page) => r1(Math.abs(apcaLc(toneOf(c), toneOf(page))));
      report.push({ role: 'surface', family: 'surface', value: a.value, step: 1, lc: lcOnPage(want, L.ground[0].oklch), target: 0, below: 0, above: Infinity, inOrder: true, inRange: true, dE: r1(before),
        dark: { value: dv, step: 1, lc: lcOnPage(parseAnchorColor(dv).oklch, D.ground[0].oklch), target: 0, inOrder: true, family: 'surface', ...(a.dark ? {} : { derived: 'hue and chroma of value at the dark card lightness' }) } });
    }
  }
  if (Object.keys(strongInk).length) data.strongInk = strongInk;
  return { report, sources };
}
// ── Solids, their labels and the key run 9–12 (APCA) ──────────────────────────────────────────────────────
// Two labels, the same in every mode: light = light neutral step 1 (the light page), dark = light neutral step 12 (the ink),
// also in dark modes, where it reads as dark text on a bright solid. Contrast is |Lc| with the label as text and the solid as
// background; the floor is apca.solid (+ SOLVE_MARGIN when solving). Per family, scheme and solid step (9, or an anchored
// role's step), white first, as in Radix: the light label whenever the solid reaches the floor against it; otherwise the dark
// label if the solid reaches it; otherwise the solid's lightness moves just far enough to reach one of them (darker for the
// light label, lighter for the dark one), its chroma clamped to the gamut at each tested lightness, so the Lc tested is the
// Lc shipped: toward the light label when both moves keep about the same chroma (within CHROMA_EDGE), else the move that
// keeps more chroma. A solid that already passes (an anchored one included) is kept exactly. Steps 10–11 follow (respace).
const CHROMA_EDGE = 0.05; // a move must keep 5% more of the generated chroma than the other to beat white on chroma
const setSw = (sw, c) => { sw.oklch = c; sw.css = okCss(c); };
const lcOn = (fg, bg) => apcaLc(toneOf(fg), toneOf(bg)); // |Lc|: fg as text, bg as background
// Bisection on [a, b] where ok(a) holds and ok(b) does not: the point nearest b that still holds.
const edge = (a, b, ok) => { for (let i = 0; i < 40; i++) { const m = (a + b) / 2; if (ok(m)) a = m; else b = m; } return a; };
// Cusp: a dark-label step 9 (an accent, not anchored) goes up to its hue's gamut cusp — the lightness where the in-gamut
// chroma at the generated hue is greatest, capped at CUSP_MAX_L — with the full chroma there, when that is brighter than
// where the floor left it and still clears the dark-label floor; it keeps at least apca.ui against the page (lowered
// toward the floor-solved lightness until it does) and leaves the key run room: at least KEY_RUN_MIN Lc on the page short of
// step 12 (in a dark scheme a bright cusp can sit beyond step 12, which would collapse 9–12 into one colour). Yellow becomes
// lemon, not mustard. Light-label solids never move here.
const CUSP_MAX_L = 0.95, KEY_RUN_MIN = 15; // 15 Lc from 9 to 12: 5 per step, a hover and two text steps that stay distinct
function cuspOf(H, gamut) {
  let best = 0, bL = 0; for (let L = 0.3; L <= 1; L += 0.002) { const c = clampChroma(L, 0.5, H, gamut); if (c > best) { best = c; bL = L; } }
  for (let L = bL - 0.002; L <= bL + 0.002; L += 0.0001) { const c = clampChroma(L, 0.5, H, gamut); if (c > best) { best = c; bL = L; } }
  return Math.min(bL, CUSP_MAX_L);
}
function solveSolid(ramp, st, floor, labels, gamut, only, cusp) {
  const s = ramp[st - 1], p = [...s.oklch], F = floor + SOLVE_MARGIN;
  const at = (L) => [L, clampChroma(L, p[1], p[2], gamut), p[2]];
  const passL = (L) => lcOn(labels.light, at(L)) >= F, passD = (L) => lcOn(labels.dark, at(L)) >= F;
  let label, c = p, unreachable;
  if (only !== 'dark' && lcOn(labels.light, p) >= F) label = 'light';
  else if (lcOn(labels.dark, p) >= F) label = 'dark';
  else {
    const toLight = only !== 'dark' && passL(0) ? edge(0, p[0], passL) : null, toDark = passD(1) ? edge(1, p[0], passD) : null;
    const k = (L) => (L == null ? -1 : at(L)[1] / Math.max(p[1], 1e-9)), kL = k(toLight), kD = k(toDark);
    if (toLight == null && toDark == null) { label = lcOn(labels.light, at(0)) >= lcOn(labels.dark, at(1)) ? 'light' : 'dark'; c = at(label === 'light' ? 0 : 1); unreachable = true; }
    else { label = toLight == null ? 'dark' : toDark == null ? 'light' : kD - kL > CHROMA_EDGE ? 'dark' : 'light'; c = at(label === 'dark' ? toDark : toLight); }
    setSw(s, c);
  }
  let atCusp; const moved = +(c[0] - p[0]).toFixed(4); // the label solve's ΔL (0 when kept); the cusp move is cuspAt
  if (cusp && label === 'dark') {
    const H = p[2], full = (L) => [L, clampChroma(L, 0.5, H, gamut), H], pageLc = (L) => lcOn(full(L), ramp[0].oklch);
    const visible = (L) => pageLc(L) >= cusp.ui + SOLVE_MARGIN && pageLc(L) <= lcOn(ramp[11].oklch, ramp[0].oklch) - KEY_RUN_MIN;
    let L = cuspOf(H, gamut); if (!visible(L) && visible(c[0])) L = edge(c[0], L, visible);
    const k = full(L);
    if (L > c[0] + 1e-4 && visible(L) && lcOn(labels.dark, k) >= F) { atCusp = { cuspL: +cuspOf(H, gamut).toFixed(4), L: +L.toFixed(4), floorL: +c[0].toFixed(4) }; c = k; setSw(s, c); }
  }
  return { label, lc: r1(lcOn(labels[label], c)), floor, ...(atCusp ? { cusp: true, cuspAt: atCusp } : {}), moved, generated: p.map((x) => +x.toFixed(6)), ...(unreachable ? { unreachable } : {}) };
}
// The key run: steps 10 and 11 rebuilt between the solid (9) and step 12, evenly in APCA Lc against the page
// (Lc10 = Lc9 + (Lc12 − Lc9)/3, Lc11 = Lc9 + 2(Lc12 − Lc9)/3); each step's lightness is solved for its Lc, its hue taken
// along the shorter arc weighted by chroma (a near-grey end barely pulls the hue, so a lime run stays lime toward a pale step
// 12) and its chroma eased in (t², held near the solid, falling into 12), clamped to the gamut. Anchored steps 10–12 are fixed
// points: the run is spaced evenly on each side of them. Step 10 is the hover: it must clear the solid floor against step
// 9's label. When the run heads toward the label (dark text in a light scheme, light text in a dark one) and step 10 would
// not, step 9 moves toward the page just far enough that it does (hoverRoom); an anchored step 9 stays exact and step 10
// moves toward 9 to the floor instead (a recorded deviation). Steps 11 and 12 are text: each clears apca.text on the page
// and on step 3 (where a role's -fg sits on its -subtle fill).
// Step 12 stays as generated unless it is needed for order. Every deviation from even spacing is recorded with its reason.
const ease = (t) => t * t;
const hueLerp = (a, b, t) => (((a + (((((b - a) % 360) + 540) % 360) - 180) * t) % 360) + 360) % 360;
function respace(ramp, { entry, floor, text, labels, gamut, pinned, nineFixed }) {
  const page = toneOf(ramp[0].oklch), lcP = (c) => apcaLc(toneOf(c), page), dir = toneOf(ramp[11].oklch) < page ? -1 : 1;
  const lab = labels[entry.label], F = floor + SOLVE_MARGIN, dev = [], pL = ramp[0].oklch[0];
  // The colour at a page Lc, for a requested chroma and hue: Lc rises away from the page (darker on light, lighter on dark).
  const atLc = (lc, C, H) => { const f = (L) => lcP([L, clampChroma(L, C, H, gamut), H]) <= lc; const L = dir < 0 ? edge(pL, 0, f) : edge(pL, 1, f); return [L, clampChroma(L, C, H, gamut), H]; };
  const build = (c9, extra = {}) => {
    const pts = { 9: c9, 12: [...ramp[11].oklch], ...Object.fromEntries(pinned.map((st) => [st, [...ramp[st - 1].oklch]])), ...extra };
    const fixed = Object.keys(pts).map(Number).sort((x, y) => x - y), out = { ...pts };
    for (let i = 0; i + 1 < fixed.length; i++) { const a = fixed[i], b = fixed[i + 1], A = pts[a], B = pts[b], la = lcP(A), lb = lcP(B);
      for (let st = a + 1; st < b; st++) { const t = (st - a) / (b - a), th = (t * B[1]) / Math.max(1e-9, t * B[1] + (1 - t) * A[1]), H = hueLerp(A[2], B[2], th); out[st] = atLc(la + (lb - la) * t, A[1] + (B[1] - A[1]) * ease(t), H); } }
    return out;
  };
  const extra = {};
  // Order: step 12 at least 3 Lc beyond step 9 (1 per step), unless anchored.
  if (!pinned.includes(12) && lcP(ramp[11].oklch) < lcP(ramp[8].oklch) + 3) { const z = ramp[11].oklch; extra[12] = atLc(Math.min(108, lcP(ramp[8].oklch) + 3), z[1], z[2]); dev.push({ step: 12, reason: 'order' }); }
  let c9 = [...ramp[8].oklch], run = build(c9, extra), room = false;
  const hoverOk = (r) => lcOn(lab, r[10]) >= F;
  if (!hoverOk(run)) {
    const toward = (entry.label === 'dark' && dir < 0) || (entry.label === 'light' && dir > 0);
    if (pinned.includes(10)) dev.push({ step: 10, reason: 'anchored-hover-floor' });
    else {
      // Room first (step 9 toward the page); when no step 9 gives an even run a passing hover (a dark label in a light scheme
      // whose step 12 is near black: the hover a third of the way is always too dark), step 10 goes to the floor instead.
      const g = entry.generated, C9 = entry.cusp ? 0.5 : g[1], ok = (lc) => hoverOk(build(atLc(lc, C9, g[2]), extra)); // a cusp solid keeps the gamut's full chroma
      if (!nineFixed && toward && ok(0.5)) { c9 = atLc(edge(0.5, lcP(c9), ok), C9, g[2]); run = build(c9, extra); room = true; }
    }
    if (!pinned.includes(10) && !hoverOk(run)) {
      // Step 9 stays: step 10 moves toward it, to the highest Lc that still clears the floor, and 11 re-spaces between 10 and 12.
      const l9 = lcP(c9), even = l9 + (lcP(run[12]) - l9) / 3, h = run[10], try10 = (lc) => atLc(lc, h[1], h[2]), ok = (lc) => lcOn(lab, try10(lc)) >= F;
      if (ok(l9 + 1)) { extra[10] = try10(edge(l9 + 1, even, ok)); run = build(c9, extra); dev.push({ step: 10, reason: 'hover-floor' }); }
      else dev.push({ step: 10, reason: 'hover-floor-unreachable' });
    }
  }
  // Text steps: 11 (a role's -fg) and 12 clear apca.text against the page and against step 3 (the role's -subtle fill).
  const s3 = ramp[2].oklch, textLc = (c) => Math.min(lcP(c), lcOn(c, s3));
  for (const st of [11, 12]) if (textLc(run[st]) < text && !pinned.includes(st)) { const z = run[st], at = (x) => atLc(x, z[1], z[2]), ok = (x) => textLc(at(x)) < text + SOLVE_MARGIN;
    extra[st] = at(edge(lcP(z), 108, ok) + 0.01); run = build(c9, extra); dev.push({ step: st, reason: 'text-floor' }); }
  for (let st = 9; st < 12; st++) if ((run[st + 1][0] - run[st][0]) * dir <= 0) dev.push({ step: st + 1, reason: 'order' });
  const fixedSteps = new Set(pinned), L9before = ramp[8].oklch[0];
  for (let st = 9; st <= 12; st++) if (!fixedSteps.has(st) && (st !== 12 || extra[12]) && (st !== 9 || room)) setSw(ramp[st - 1], run[st]);
  if (room) { entry.hoverRoom = true; entry.roomMoved = +(c9[0] - L9before).toFixed(4); entry.lc = r1(lcOn(lab, c9)); }
  entry.hoverLc = r1(lcOn(lab, ramp[9].oklch));
  const at = (st) => ramp[st - 1].oklch;
  return { lc: [9, 10, 11, 12].map((st) => r1(lcP(at(st)))), L: [9, 10, 11, 12].map((st) => +at(st)[0].toFixed(4)), C: [9, 10, 11, 12].map((st) => +at(st)[1].toFixed(4)), H: [9, 10, 11, 12].map((st) => +at(st)[2].toFixed(2)), pinned: [...pinned].sort(), deviations: dev };
}
// Solids and the key run of every family in both schemes of a mode's data, then the control border (neutral step 8, a
// control's only edge) held at |Lc| ≥ apca.ui on steps 1 and 2. Returns labels { light, dark } (per family token name, the
// step-9 entry plus `anchored` entries for an anchored role's other solid step) and keyRun { light, dark }.
function solveSolidLabels(data, { T, solidSteps, pins, roles, labels, gamut }) {
  // fg-subtle reads neutral step 10 as text; keep its generated value before the key run moves it.
  data.subtle = data.subtle || { light: data.schemes.light.neutral?.[9]?.css, dark: data.schemes.dark.neutral?.[9]?.css };
  const out = { light: {}, dark: {} }, runs = { light: {}, dark: {} }, neutrals = new Set(families(data).neutrals);
  for (const scheme of ['light', 'dark']) for (const [f, ramp] of Object.entries(data.schemes[scheme])) {
    const name = rampName(f), pin = pins?.[scheme]?.[f], extra = [...new Set(Object.entries(solidSteps?.[scheme] || {}).filter(([role, st]) => roles[role] === f && st !== 9).map(([, st]) => st))];
    const snap = ramp.map((x) => ({ ...x, oklch: [...x.oklch] })), pinned = [...new Set([pin, ...extra])].filter((st) => st >= 10 && st <= 12);
    const cusp = pin !== 9 && !neutrals.has(f) ? { ui: T.ui } : null, bright = !!cusp && inBright(ramp[8].oklch[2]);
    let e = solveSolid(ramp, 9, T.solid, labels, gamut, bright ? 'dark' : undefined, cusp);
    if (bright) e.brightHue = true;
    let kr = respace(ramp, { entry: e, floor: T.solid, text: T.text, labels, gamut, pinned, nineFixed: pin === 9 && e.moved === 0 });
    // Visibility guard: white first, unless keeping white (with the hover room it needs) would leave the solid under apca.ui
    // against the page, where it no longer reads as a solid. Then the family takes the dark label instead.
    if (e.label === 'light' && pin !== 9 && kr.lc[0] < T.ui) {
      const rejected = { lc9OnPage: kr.lc[0], floor: T.ui };
      ramp.forEach((x, i) => setSw(x, snap[i].oklch));
      e = solveSolid(ramp, 9, T.solid, labels, gamut, 'dark', cusp); e.whiteRejected = rejected;
      kr = respace(ramp, { entry: e, floor: T.solid, text: T.text, labels, gamut, pinned, nineFixed: false });
    }
    out[scheme][name] = e; runs[scheme][name] = kr;
    for (const st of extra) (e.anchored ??= {})[st] = solveSolid(ramp, st, T.solid, labels, gamut);
    for (const st of extra) { const a = e.anchored[st], hv = st === 12 ? 11 : st + 1; a.hoverLc = r1(lcOn(labels[a.label], ramp[hv - 1].oklch)); if (a.hoverLc < T.solid) kr.deviations.push({ step: hv, reason: 'anchored-hover-floor' }); }
  }
  // The engine can leave a lightness like 7e-9 (an anchored ramp's black step 12): write every step's CSS in fixed notation.
  for (const scheme of ['light', 'dark']) for (const ramp of Object.values(data.schemes[scheme])) for (const x of ramp) if (/\de-\d/.test(x.css)) setSw(x, x.oklch.map((v) => (Math.abs(v) < 1e-6 ? 0 : v)));
  for (const scheme of ['light', 'dark']) { const n = data.schemes[scheme].neutral; if (!n) continue; const e = n[7].oklch, g1 = n[0].oklch, g2 = n[1].oklch, dir = scheme === 'light' ? -1 : 1;
    const ok = (L) => Math.min(lcOn([L, e[1], e[2]], g1), lcOn([L, e[1], e[2]], g2)) >= T.ui + SOLVE_MARGIN; if (ok(e[0])) continue;
    let L = e[0]; for (let i = 0; i < 200 && !ok(L) && L > 0 && L < 1; i++) L += dir * 0.005; setSw(n[7], [clamp01(L), e[1], e[2]]); }
  // Neutrals split: the control border is surface step 8, on the page (ground 1–2) and on the material (surface 1–2).
  for (const scheme of ['light', 'dark']) { const S = data.schemes[scheme].surface, G = data.schemes[scheme].ground; if (!S || !G) continue; const e = S[7].oklch, dir = scheme === 'light' ? -1 : 1, under = [G[0], G[1], S[0], S[1]].map((x) => x.oklch);
    const ok = (L) => Math.min(...under.map((b) => lcOn([L, e[1], e[2]], b))) >= T.ui + SOLVE_MARGIN; if (ok(e[0])) continue;
    let L = e[0]; for (let i = 0; i < 200 && !ok(L) && L > 0 && L < 1; i++) L += dir * 0.005; setSw(S[7], [clamp01(L), clampChroma(clamp01(L), e[1], e[2], gamut), e[2]]); }
  return { labels: out, keyRun: runs };
}
const modes = {};
let labels;
try {
  for (const m of MODES) {
    const o = modeOverrides[m.id] || {};
    const settings = merge(merge(eff.settings, m.settings), o.settings);
    const mTarget = normalizeSpectrum(settings).target;
    const roles = merge(merge(eff.roles, m.roles), o.roles), endpoints = o.endpoints ?? m.endpoints ?? eff.endpoints;
    const { list: anchors, clips } = gamutAnchors(o.anchors ?? m.anchors ?? anchorsTop ?? [], mTarget);
    if (neutrals && normalizeSpectrum(settings).generator === 'oklch' && NEUTRAL_ROLES_SPLIT.some((k) => neutrals[k]?.from)) fail(2, `request: mode ${m.id}: neutrals { from } needs the HCT generator (the OKLCH generator makes no Radix greys)`);
    // With neutrals, ground, ink and surface anchors pin the split families (splitNeutrals), not the engine's neutral.
    const engineAnchors = neutrals ? anchors.filter((a) => !SPLIT_ANCHORS.includes(a.role)) : anchors;
    let r, lifted = null;
    if (m.contrast) { // the highest lift up to +18% that the scheme's page can still reach (a dark page tops out lower than a light one)
      const base = normalizeSpectrum(settings), key = m.scheme === 'light' ? 'targetsLight' : 'targetsDark', t0 = base[key] ?? DEFAULT_TARGETS[m.scheme];
      for (const k of [1.18, 1.15, 1.12, 1.1, 1.08, 1.06, 1.04, 1.02]) { try { r = run({ ...settings, [key]: scaleTargets(t0, k) }, roles, engineAnchors); lifted = k; break; } catch (e) { if (!/gamut/i.test(e.message)) throw e; } }
      if (!r) r = run(settings, roles, engineAnchors), lifted = 1;
    } else r = run(settings, roles, engineAnchors);
    const data = structuredClone(r.data); // solids are solved per mode (below), on a copy of the cached generation
    const split = neutrals ? splitNeutrals(data, r.settings, r.generated, roles, anchors.filter((a) => SPLIT_ANCHORS.includes(a.role))) : null;
    // Each anchor's gamut: whether it was inside the target, and what clipping cost it (ΔE OKLab × 100).
    const report = [...r.report, ...(split ? split.report : [])].map((x) => { const src = anchors.find((a) => a.role === x.role); const g = clips.get(x.value); const gd = x.dark && clips.get(x.dark.value);
      return { ...x, ...(src?.source ? { source: src.source } : {}), ...(g ? { gamut: g } : {}), ...(x.dark && gd ? { dark: { ...x.dark, gamut: gd } } : {}) }; });
    modes[m.id] = { ...m, apca: m.contrast ? APCA.contrast : APCA.normal, lift: lifted, settings: r.settings, target: mTarget, data, roles: r.roles, solidSteps: r.solidSteps, pins: r.pins, report, endpoints, generated: r.generated, ...(split ? { neutralSources: split.sources } : {}) };
  }
  // The two labels come from the light mode's light neutral (steps 1 and 12 are never moved by a solve), so every mode's
  // solids are solved against the same pair of colours. Neutrals split: the light page (ground 1) and the light ink (ink 12).
  const ln = modes.light.data.schemes.light.neutral, lp = neutrals ? modes.light.data.schemes.light.ground : ln;
  labels = { light: [...lp[0].oklch], dark: [...ln[11].oklch] };
  for (const m of MODES) { const M = modes[m.id];
    const sol = solveSolidLabels(M.data, { T: M.apca, solidSteps: M.solidSteps, pins: M.pins, roles: M.roles, labels, gamut: M.target }); M.solidLabels = sol.labels; M.keyRun = sol.keyRun; }
} catch (e) { fail(1, 'generation failed: ' + e.message); }
const labelCss = { light: okCss(labels.light), dark: okCss(labels.dark) };
// The label of a role's solid in a mode: its family's entry at the role's solid step.
const labelOf = (M, role) => { const e = M.solidLabels[M.scheme][rampName(M.roles[role])], st = M.solidSteps[M.scheme]?.[role] ?? 9; return st === 9 ? e : e.anchored?.[st] ?? e; };
const fam = families(modes.light.data);
for (const m of MODES) { const f = families(modes[m.id].data).all.join(','); if (f !== fam.all.join(',')) fail(2, 'request: mode ' + m.id + ' produces families ' + f + ', not ' + fam.all.join(',') + (familyNames === 'index' ? ' — with index names every mode still needs the same number of hues and the same neutrals (hueSet, grays)' : ' — change hue or hueSet for all modes at once (top-level settings), not per mode')); }
const target = modes.light.settings.target;
const sw = (M, f, step) => M.data.schemes[M.scheme][f][step - 1].oklch;

// ── Series under colour-vision deficiency ─────────────────────────────────────────────────────────────────
// Machado, Oliveira & Fernandes 2009, severity 1.0 (full dichromacy), applied to linear sRGB and clipped to 0–1, on the
// sRGB fallback of each series colour (chroma-clipped into sRGB). Distance: OKLab ΔE × 100. Below 10 two series are hard
// to tell apart at a glance (about five just-noticeable differences); the CLI warns.
const CVD = {
  protan: [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
  deutan: [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.01182, 0.04294, 0.968881]],
  tritan: [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.3039]],
};
const CVD_MIN = 10;
const srgbLinOf = ([L, C, H]) => toLin([L, clampChroma(L, C, H, 'srgb'), H]).map(clamp01);
// ── Series and diverging, per mode ────────────────────────────────────────────────────────────────────────
// Six series colours chosen for the worst case: among subsets of the accent hues that include the primary (data-1) and steps
// 9 or 11 per hue, the set whose smallest pairwise OKLab ΔE — over normal vision and protan, deutan and tritan simulation —
// is largest. Each candidate is first nudged in lightness to clear the chart-surface floor (|Lc| ≥ apca.series, the mark as
// text on the surface; Lc 30, 45 in contrast modes).
// Neighbours then alternate step 9 / 11 where the choice allows, so adjacent bars also differ in lightness.
function series(M) {
  const acc = fam.accents, p = Math.max(0, acc.indexOf(M.roles.primary)), surf = sw(M, neutrals ? 'ground' : 'neutral', 2), dir = M.scheme === 'light' ? -1 : 1, need = M.apca.series + SOLVE_MARGIN;
  const STEPS = [8, 9, 11, 12], cand = {};
  for (const f of acc) for (const st of STEPS) { let c = [...sw(M, f, st)]; for (let n = 0; n < 160 && lcOn(c, surf) < need; n++) c = [clamp01(c[0] + dir * 0.005), c[1], c[2]]; const lin = srgbLinOf(c); cand[f + '|' + st] = { family: f, step: st, oklch: c, labs: ['normal', 'protan', 'deutan', 'tritan'].map((k) => labOfLinear(k === 'normal' ? lin : CVD[k].map((r) => clamp01(r[0] * lin[0] + r[1] * lin[1] + r[2] * lin[2])))) }; }
  const keys = Object.keys(cand), dist = {}; const d = (a, b) => { const k = a < b ? a + '/' + b : b + '/' + a; if (dist[k] == null) { let m = Infinity; for (let t = 0; t < 4; t++) { const x = cand[a].labs[t], y = cand[b].labs[t]; m = Math.min(m, 100 * Math.hypot(x[0] - y[0], x[1] - y[1], x[2] - y[2])); } dist[k] = m; } return dist[k]; };
  // Search at most 12 hues: with a larger set (the Radix 25) the candidates are the 12 spaced evenly around the hue circle from the
  // primary, which keeps the search the size of the default set's (C(11,5) subsets × 4^6 step choices) instead of growing combinatorially.
  const pool = acc.length > 12 ? [...new Set(Array.from({ length: 12 }, (_, k) => acc[(p + Math.round(k * acc.length / 12)) % acc.length]))] : acc;
  const others = pool.filter((f) => f !== acc[p]), n = Math.min(6, acc.length); let best = null, bestScore = -1;
  const choose = (start, picked) => { if (picked.length === n - 1) { const fams = [acc[p], ...picked]; const B = STEPS.length, total = B ** n; for (let mask = 0; mask < total; mask++) { const set = fams.map((f, i) => f + '|' + STEPS[Math.floor(mask / B ** i) % B]); let sc = Infinity; for (let a = 0; a < n && sc > bestScore; a++) for (let b = a + 1; b < n; b++) { const v = d(set[a], set[b]); if (v < sc) sc = v; if (sc <= bestScore) break; } if (sc > bestScore) { bestScore = sc; best = set; } } return; } for (let i = start; i < others.length; i++) choose(i + 1, [...picked, others[i]]); };
  choose(0, []);
  const hueOrder = (k) => (acc.indexOf(cand[k].family) - p + acc.length) % acc.length;
  const chosen = best.sort((a, b) => hueOrder(a) - hueOrder(b));
  const s = chosen.map((k) => { const c = cand[k]; return { family: rampName(c.family), step: c.step, oklch: c.oklch, css: okCss(c.oklch), lcOnSurface: r1(lcOn(c.oklch, surf)) }; });
  const seq = [3, 4, 5, 7, 8, 9, 11].map((st) => { const c = sw(M, acc[p], st); return { family: rampName(acc[p]), step: st, oklch: c, css: okCss(c) }; });
  return { series: s, sequential: seq, seriesSearch: { worstCaseDE: +bestScore.toFixed(2), candidates: keys.length } };
}
function diverging(M) {
  const acc = fam.accents, p = Math.max(0, acc.indexOf(M.roles.primary)), a = acc[(p + acc.length / 2) % acc.length], b = acc[p];
  const pts = [[a, 11], [a, 10], [a, 9], [a, 7], [a, 5], ['neutral', 3], [b, 5], [b, 7], [b, 9], [b, 10], [b, 11]];
  return pts.map(([f, st]) => { const c = sw(M, f, st); return { family: rampName(f), step: st, oklch: c, css: okCss(c) }; });
}
for (const id of ids) { const M = modes[id]; if (opt.series) Object.assign(M, series(M)); if (opt.diverging) M.diverging = diverging(M); if (opt.alpha) M.alpha = (neutrals ? alphaRamps(M.data, 'ground') : alphaRamps(M.data))[M.scheme]; }

function seriesCvd(M) {
  const base = M.series.map((x) => srgbLinOf(x.oklch)), out = { method: 'Machado 2009, severity 1.0, linear sRGB; OKLab ΔE × 100 on the sRGB fallback', threshold: CVD_MIN };
  for (const kind of ['normal', 'protan', 'deutan', 'tritan']) {
    const sim = base.map((rgb) => (kind === 'normal' ? rgb : CVD[kind].map((r) => clamp01(r[0] * rgb[0] + r[1] * rgb[1] + r[2] * rgb[2]))));
    const lab = sim.map(labOfLinear); let min = Infinity, pair = null;
    for (let i = 0; i < lab.length; i++) for (let j = i + 1; j < lab.length; j++) { const d = 100 * Math.hypot(lab[i][0] - lab[j][0], lab[i][1] - lab[j][1], lab[i][2] - lab[j][2]); if (d < min) { min = d; pair = [i + 1, j + 1]; } }
    out[kind] = { minDE: r2(min), pair, hex: sim.map((rgb) => hexRgb(rgb.map(enc))) };
  }
  out.ok = ['normal', 'protan', 'deutan', 'tritan'].every((k) => out[k].minDE >= CVD_MIN);
  out.weakest = ['normal', 'protan', 'deutan', 'tritan'].reduce((a, b) => (out[b].minDE < out[a].minDE ? b : a), 'normal');
  return out;
}
if (opt.series) for (const id of ids) modes[id].seriesCvd = seriesCvd(modes[id]);

// ── Tonal 050–950 (and Primes): the bundled source-palette generator, seeded with each family's light solid ──
const here = fileURLToPath(new URL('.', import.meta.url));
let tonal = null;
if (opt.tonal || opt.primes) {
  tonal = {}; const work = values.out + '/.tonal'; mkdirSync(work, { recursive: true });
  try {
    for (const f of fam.all) {
      const seed = sw(modes.light, f, 9), dir = work + '/' + rampName(f), rq = work + '/' + rampName(f) + '.json';
      writeFileSync(rq, JSON.stringify({ source: { colorSpace: 'oklch', components: seed, alpha: 1 }, output: opt.primes ? 'base-primes' : 'base', step: tonalOpt.step, toneMin: tonalOpt.toneMin, toneMax: tonalOpt.toneMax, target, hueBalance: !!tonalOpt.hueBalance, ...Object.fromEntries(['base', 'prime', 'falloff'].filter((k) => tonalOpt[k] != null).map((k) => [k, tonalOpt[k]])) }));
      execFileSync(process.execPath, [here + 'generate.cjs', '--request', rq, '--out', dir], { stdio: ['ignore', 'ignore', 'pipe'] });
      const d = JSON.parse(readFileSync(dir + '/palettes.json', 'utf8')), p = d.palettes[d.order[0]];
      const pick = (x) => ({ oklch: x.resolved.components, css: okCss(x.resolved.components), target: x.css, hex: hex(x.resolved.components) });
      tonal[rampName(f)] = { stops: (p.stops || []).map((x) => ({ stop: String(x.stop).padStart(3, '0'), ...pick(x) })), primes: opt.primes ? (p.prime || []).map((x) => ({ name: x.name, ...pick(x) })) : undefined };
    }
  } catch (e) { fail(1, 'tonal layer failed: ' + (e.stderr ? String(e.stderr) : e.message)); }
  rmSync(work, { recursive: true, force: true });
}

// ── Tonal ↔ 12-step: agreement (diagnostics) and the nearest stop per role step (tonalMap) ──────────────────
// Agreement: for each family and step, the tonal stop nearest the step's tone (CIE L*), compared in hue and chroma only
// (ΔE OKLab × 100 without the lightness term, since stops sit up to ~2.5 tone apart): this isolates hue/chroma disagreement
// between the two HCT bundles. tonalMap: per role and step, the nearest stop by full OKLab ΔE.
const chromaDE = (p, q) => { const dh = ((((q[2] - p[2]) % 360) + 540) % 360) - 180, dH = 2 * Math.sqrt(p[1] * q[1]) * Math.sin(dh * Math.PI / 360); return 100 * Math.hypot(q[1] - p[1], dH); };
const stats = (xs) => { const s = [...xs].sort((a, b) => a - b); return s.length ? { mean: r2(s.reduce((a, b) => a + b, 0) / s.length), p95: r2(s[Math.min(s.length - 1, Math.floor(s.length * 0.95))]), max: r2(s.at(-1)) } : null; };
let tonalAgreement = null;
if (tonal) {
  tonalAgreement = { method: 'per family and step: the tonal stop nearest the step tone; ΔE OKLab × 100 on hue and chroma only (lightness excluded); hue in OKLCH degrees where both chromas exceed 0.03', seed: 'light step 9 (solved solid), target ' + target + ', tonal hueBalance ' + !!tonalOpt.hueBalance + ', base ' + (tonalOpt.base ?? 60) + '%', modes: {} };
  for (const id of ids) {
    const M = modes[id], all = [], hues = [], byFamily = {};
    for (const f of fam.all) {
      const t = tonal[rampName(f)]; if (!t) continue; const tones = t.stops.map((x) => toneOf(x.oklch)), fs = [];
      for (const s of M.data.schemes[M.scheme][f]) { const tn = toneOf(s.oklch); let bi = 0; tones.forEach((x, i) => { if (Math.abs(x - tn) < Math.abs(tones[bi] - tn)) bi = i; });
        const q = t.stops[bi].oklch, d = chromaDE(s.oklch, q); fs.push(d); all.push(d); if (s.oklch[1] > 0.03 && q[1] > 0.03) hues.push(Math.abs(((((q[2] - s.oklch[2]) % 360) + 540) % 360) - 180)); }
      byFamily[rampName(f)] = stats(fs);
    }
    tonalAgreement.modes[id] = { chromaHueDE: stats(all), hueDeg: stats(hues), families: byFamily };
  }
  for (const id of ids) {
    const M = modes[id], map = {};
    for (const role of SCALE_ROLES) { const f = M.roles[role], t = tonal[rampName(f)]; if (!t) continue;
      map[role] = { family: rampName(f), steps: M.data.schemes[M.scheme][f].map((s, i) => { let best = null; for (const x of t.stops) { const d = dE(s.oklch, x.oklch); if (!best || d < best.dE) best = { stop: x.stop, dE: d }; } return { step: i + 1, stop: best.stop, dE: r2(best.dE) }; }) };
      map[role].solid = map[role].steps[(M.solidSteps[M.scheme]?.[role] ?? 9) - 1].stop; }
    M.tonalMap = map;
  }
}

// ── Variables per mode ────────────────────────────────────────────────────────────────────────────────────
const BACKDROP_ALPHA = 0.8;
function varsOf(M) {
  const v = {};
  for (const [name, steps] of Object.entries(rampsOf(M.data, M.scheme))) steps.forEach((c, i) => { v[rampVar(name, i + 1)] = c; });
  Object.assign(v, roleVariables(M.data, M.roles, M.scheme, M.solidSteps[M.scheme] || {}));
  // Text on each role's solid is the label its family's solid was solved against (|Lc| ≥ apca.solid): the light
  // label (light neutral 1) or the dark label (light neutral 12, in every mode). fg-on-solid is the primary's, for compatibility.
  for (const role of SCALE_ROLES) v['--colors-' + role + '-on-solid'] = labelCss[labelOf(M, role).label];
  v['--colors-fg-on-solid'] = 'var(--colors-primary-on-solid)';
  if (M.endpoints) Object.assign(v, endpointVars(M.data, M.roles, M.endpoints));
  if (M.alpha) for (const [f, steps] of Object.entries(M.alpha)) steps.forEach((x, i) => { v[rampVar(f, 'a' + (i + 1))] = x.css; });
  if (M.series) { M.series.forEach((x, i) => { v['--colors-data-' + (i + 1)] = x.css; }); M.sequential.forEach((x, i) => { v['--colors-data-seq-' + (i + 1)] = x.css; }); }
  if (M.diverging) M.diverging.forEach((x, i) => { v['--colors-data-div-' + (i + 1)] = x.css; });
  if (opt.tonalRoles && M.tonalMap) for (const [role, t] of Object.entries(M.tonalMap)) { v['--palette-role-' + role] = `var(--palette-${t.family}-${t.solid})`; t.steps.forEach((x) => { v[`--palette-role-${role}-${x.step}`] = `var(--palette-${t.family}-${x.stop})`; }); }
  if (neutrals) splitVars(v, M);
  // Backdrop behind dialogs and sheets: pure black at 80% in every mode (denser than the engine's 40% light / 70% dark
  // neutral veil, so the dialog reads as the only layer). Pure, not the tinted --colors-black, whatever `endpoints.black` is.
  v['--colors-bg-backdrop'] = `rgb(0 0 0 / ${BACKDROP_ALPHA})`;
  return v;
}
// Neutrals split: the ink ramp is declared under its own name and gray (the neutral's family name) becomes its alias, then
// the neutral-based roles move onto the three families (SPLIT_ROLES; references/system.md › Neutrals).
const SPLIT_ROLES = {
  'bg': ['ground', 1], 'bg-subtle': ['ground', 2],
  'bg-backdrop': ['ground', 12, ROLE_STEPS['bg-backdrop'][2]], 'shadow': ['ground', 12, ROLE_STEPS.shadow[2]],
  'surface': ['surface', 1], 'surface-subtle': ['surface', 2], 'surface-muted': ['surface', 3],
  'bg-muted': ['surface', 3], 'bg-muted-hover': ['surface', 4], 'bg-muted-active': ['surface', 5],
  'bg-control': ['surface', 12, ROLE_STEPS['bg-control'][2]], 'bg-control-hover': ['surface', 12, ROLE_STEPS['bg-control-hover'][2]], 'bg-control-active': ['surface', 12, ROLE_STEPS['bg-control-active'][2]],
  'bg-overlay': ['surface', 1, { dark: 2 }], // floating layers: the card tone in light, one step up in dark, where shadows barely read
  'border': ['surface', 6], 'border-strong': ['surface', 7], 'control-border': ['surface', 8],
  'fg': ['ink', 12], 'fg-muted': ['ink', 11], 'bg-inverse': ['ink', 12], 'fg-inverse': ['ground', 1],
};
function splitVars(v, M) {
  const kinds = [...Array(12)].map((_, i) => String(i + 1)).concat(M.alpha ? [...Array(12)].map((_, i) => 'a' + (i + 1)) : []);
  for (const k of kinds) { v['--colors-ink-' + k] = v['--colors-gray-' + k]; v['--colors-gray-' + k] = `var(--colors-ink-${k})`; }
  for (const [role, entry] of Object.entries(SPLIT_ROLES)) { const { family, step, alpha } = roleStep(entry, M.scheme); v['--colors-' + role] = withAlpha(`var(--colors-${family}-${step})`, alpha); }
  if (v['--colors-fg-strong'] === 'var(--colors-gray-12)') v['--colors-fg-strong'] = 'var(--colors-ink-12)';
  // Selection fills sit on the material, so the balanced fill can't be its own step 1 (the one-neutral system's choice, a
  // raised row on a bg-subtle panel): quiet surface 3, balanced surface 4, loud primary 3 in light; surface 4 → the primary
  // solid in dark; text ink 12.
  const SEL = { 'neutral-3': 'surface-3', 'neutral-1': 'surface-4', 'neutral-4': 'surface-4', 'neutral-12': 'ink-12' };
  const ref = (r) => `var(--colors-${SEL[r] ?? r})`;
  for (const [k, x] of Object.entries(selectionVars(M.scheme, ref))) v['--colors-' + k] = x;
}
const V = Object.fromEntries([...ids].map((id) => [id, varsOf(modes[id])]));
const tonalVars = {}; if (tonal) for (const [f, t] of Object.entries(tonal)) { t.stops.forEach((x) => { tonalVars['--palette-' + f + '-' + x.stop] = x.css; }); (t.primes || []).forEach((x) => { tonalVars['--palette-' + f + '-' + x.name] = x.css; }); }

// ── Resolving a variable to a colour (contrast, Figma) ────────────────────────────────────────────────────
function resolveRGBA(M, val, depth = 0) {
  if (depth > 4 || val == null) return null; const look = (k) => V[M.id][k] ?? tonalVars[k];
  let m = /^var\((--[\w-]+)\)$/.exec(val); if (m) return look(m[1]) != null ? resolveRGBA(M, look(m[1]), depth + 1) : null;
  m = /^color-mix\(in oklch, var\((--[\w-]+)\) ([\d.]+)%, transparent\)$/.exec(val); if (m) { const c = resolveRGBA(M, look(m[1]) || '', depth + 1); return c && { ...c, a: +(c.a * +m[2] / 100).toFixed(4) }; }
  const ok = parseOk(val); if (ok) { const [r, g, b] = rgbOf(ok); return { r: +r.toFixed(5), g: +g.toFixed(5), b: +b.toFixed(5), a: 1 }; }
  m = /^color\(srgb ([\d.]+) ([\d.]+) ([\d.]+) \/ ([\d.]+)\)$/.exec(val); if (m) return { r: +m[1], g: +m[2], b: +m[3], a: +m[4] };
  m = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(val); if (m) { const h = m[1].length === 3 ? m[1].split('').map((c) => c + c).join('') : m[1]; return { r: parseInt(h.slice(0, 2), 16) / 255, g: parseInt(h.slice(2, 4), 16) / 255, b: parseInt(h.slice(4, 6), 16) / 255, a: 1 }; }
  return null;
}

// ── Contrast matrix, per mode ─────────────────────────────────────────────────────────────────────────────
// APCA only: |Lc| from the vendored apcaLc (system/contrast.js), the pair's foreground as text and its background as
// background, on the sRGB values (channels clipped) turned into CIE L* tones. A translucent colour is composited over its
// pair's background (and that over the page). Pass/fail by intent against the mode's APCA thresholds (apca.text, .hint, .ui,
// and apca.solid for a label on its solid). `ratio` (WCAG 2) is informational only: it drives no decision and no flag.
// Reported only — no colour moves to pass.
const wcagY = ([r, g, b]) => 0.2126 * dec(r) + 0.7152 * dec(g) + 0.0722 * dec(b);
const toneOfY = (y) => (y > 0.008856 ? 116 * Math.cbrt(y) - 16 : 903.3 * y);
const INTENT = { text: 'text (apca.text)', hint: 'placeholder / hint / subtle text (apca.hint)', ui: 'non-text edge: control border, divider (apca.ui)', label: 'label text on a solid (apca.solid)' };
const thresholdOf = (T, intent) => (intent === 'label' ? T.solid : T[intent]);
function contrastPairs() {
  const p = [];
  // Neutrals split: ink text on the page (ground 1, 2) and on the material (surface 1–3); the control border on both.
  for (const f of ['fg', 'fg-muted', 'fg-subtle']) for (const b of neutrals ? ['bg', 'bg-subtle', 'surface', 'surface-subtle', 'surface-muted'] : ['bg', 'bg-subtle', 'bg-muted']) p.push([f, b, f === 'fg-subtle' ? 'hint' : 'text']);
  for (const r of SCALE_ROLES) p.push([r + '-fg', r + '-subtle', 'text'], [r + '-fg', 'bg', 'text']);
  for (const r of SCALE_ROLES) p.push([r + '-on-solid', r + '-solid', 'label'], [r + '-on-solid', r + '-solid-hover', 'label']);
  p.push(['border-strong', 'bg', 'ui'], ...(neutrals ? ['bg', 'bg-subtle', 'surface', 'surface-subtle'] : ['bg']).map((b) => ['control-border', b, 'ui']), ['focus-ring', 'bg', 'ui']);
  return p;
}
function contrastOf(M) {
  const rows = [];
  for (const [fg, bg, intent] of contrastPairs()) {
    const B = resolveRGBA(M, V[M.id]['--colors-' + bg]), F = resolveRGBA(M, V[M.id]['--colors-' + fg]); if (!B || !F) continue;
    const page = resolveRGBA(M, V[M.id]['--colors-bg']) || { r: 1, g: 1, b: 1 };
    const bgc = [B.r, B.g, B.b].map((v, i) => v * B.a + [page.r, page.g, page.b][i] * (1 - B.a)), fgc = [F.r, F.g, F.b].map((v, i) => v * F.a + bgc[i] * (1 - F.a));
    const yf = wcagY(fgc), yb = wcagY(bgc), lc = apcaLc(toneOfY(yf), toneOfY(yb)), threshold = thresholdOf(M.apca, intent);
    rows.push({ fg, bg, intent, lc: r1(lc), threshold, pass: lc >= threshold, ratio: r2((Math.max(yf, yb) + 0.05) / (Math.min(yf, yb) + 0.05)) });
  }
  const fails = rows.filter((x) => !x.pass);
  return { method: 'APCA |Lc| (vendored apcaLc: foreground as text, background as background) on sRGB (channels clipped), CIE L* tones; pass at the mode\'s APCA threshold per intent; ratio is WCAG 2, informational only', thresholds: M.apca, intents: INTENT, pairs: rows,
    summary: { pairs: rows.length, fail: fails.length, failures: fails.map((x) => `${x.fg} on ${x.bg} Lc ${x.lc} (${x.intent}, needs ${x.threshold})`) } };
}
for (const id of ids) modes[id].contrastMatrix = contrastOf(modes[id]);
// Separation (neutrals split): surface step 1 against ground step 1 in each mode, OKLab ΔE × 100 (the gate) and APCA |Lc|.
if (neutrals) for (const id of ids) { const M = modes[id], g = sw(M, 'ground', 1), s = sw(M, 'surface', 1), d = dE(s, g);
  M.separation = { dE: r2(d), lc: r1(Math.abs(apcaLc(toneOf(s), toneOf(g)))), threshold: SEPARATION_MIN, pass: d >= SEPARATION_MIN, groundTone: r2(toneOf(g)), surfaceTone: r2(toneOf(s)), method: 'surface 1 vs ground 1: OKLab ΔE × 100 ≥ threshold (one CSS Color 4 JND); lc is APCA |Lc|, informational' }; }

// ── Selectors ─────────────────────────────────────────────────────────────────────────────────────────────
const R = eff.scope || ':where(:root)', on = (s) => (eff.scope ? eff.scope + s : s);
const forced = (id) => selectors === 'attribute' ? (id.endsWith('-contrast') ? on(`[data-color-mode=${id.replace(/-contrast$/, '')}][data-contrast=more]`) : on(`[data-color-mode=${id}]`)) : (id.endsWith('-contrast') ? on(`.${id.replace(/-contrast$/, '')}.contrast-more`) : on(`.${id}`));
const notForced = () => selectors === 'attribute' ? `:not([data-color-mode])` : `:not(.light):not(.dark)${[...ids].filter((x) => !['light', 'dark'].includes(x) && !x.endsWith('-contrast')).map((x) => `:not(.${x})`).join('')}`;
function rulesFor(id, vars) {
  const M = modes[id], decl = { 'color-scheme': M.scheme, ...vars }, out = [];
  if (id === 'light') out.push({ sel: `${R}` }, { sel: forced('light') });
  else if (id === 'dark') out.push({ media: '(prefers-color-scheme: dark)', sel: R + notForced() }, { sel: forced('dark') });
  // A contrast mode follows its own scheme's preference, so a light contrast mode never repaints a dark-preferring page.
  else if (M.contrast) out.push({ media: `(prefers-color-scheme: ${M.scheme}) and (prefers-contrast: more)`, sel: R + notForced() }, { sel: forced(id) });
  else out.push({ sel: forced(id) });
  return out.map((r) => ({ ...r, decl }));
}
const block = (sel, decl) => `${sel} {\n${Object.entries(decl).map(([k, v]) => `  ${k}: ${v};`).join('\n')}\n}`;
const emit = (rules) => rules.map((r) => (r.media ? `@media ${r.media} {\n${block(r.sel, r.decl)}\n}` : block(r.sel, r.decl))).join('\n');
// Literal values every mode shares (no var(), so they don't re-resolve per mode): declared once in system.base.css when split.
const SHARED = new Set(Object.keys(V.light).filter((k) => [...ids].every((id) => V[id][k] === V.light[k]) && !/var\(/.test(V.light[k])));
// One pass of the stylesheet as parts: valueOf maps a value (sRGB fallback or as-is); onlyChanged keeps what differs in P3.
function parts(valueOf, onlyChanged, strip) {
  const keep = (x) => !onlyChanged || toSrgbCss(x) !== x;
  const vv = Object.fromEntries(Object.entries(V).map(([id, vars]) => [id, Object.fromEntries(Object.entries(vars).filter(([k, x]) => keep(x) && !(strip && strip.has(k))).map(([k, x]) => [k, valueOf(x)]))]));
  const out = { ld: '', modes: {}, tonal: '', shared: '' };
  if (opt.lightDark) {
    // Every key that changes in either scheme (P3 pass: a light-only P3 colour still needs its light-dark() pair).
    const keys = [...new Set([...Object.keys(vv.light), ...Object.keys(vv.dark)])].filter((k) => k in V.light && k in V.dark), ld = onlyChanged ? {} : { 'color-scheme': 'light dark' };
    for (const k of keys) { const a = valueOf(V.light[k]), b = valueOf(V.dark[k]); ld[k] = a === b ? a : `light-dark(${a}, ${b})`; }
    out.ld = [Object.keys(ld).length ? block(R, ld) : '', onlyChanged ? '' : block(forced('light'), { 'color-scheme': 'light' }) + '\n' + block(forced('dark'), { 'color-scheme': 'dark' })].filter(Boolean).join('\n');
  }
  for (const id of ids) if (!(opt.lightDark && (id === 'light' || id === 'dark'))) out.modes[id] = emit(rulesFor(id, vv[id]));
  const tv = Object.entries(tonalVars).filter(([, x]) => keep(x)); if (tv.length) out.tonal = block(R, Object.fromEntries(tv.map(([k, x]) => [k, valueOf(x)])));
  if (strip) { const sv = [...strip].filter((k) => keep(V.light[k])); if (sv.length) out.shared = block(R, Object.fromEntries(sv.map((k) => [k, valueOf(V.light[k])]))); }
  return out;
}
const p3 = target === 'display-p3' && eff.p3Fallback !== false;
const join = (xs) => xs.filter(Boolean).join('\n');
const wrapP3 = (s) => (s ? '\n@media (color-gamut: p3) {\n' + s + '\n}' : '');
const header = (what) => '/* Generated colour system (' + (what ? what + '; ' : '') + 'modes: ' + [...ids].join(', ') + '; selectors: ' + selectors + (opt.lightDark ? ', light-dark()' : '') + (p3 ? '; sRGB values with a Display P3 upgrade' : '') + '). Do not edit; regenerate from request.json. */\n';
const whole = (P) => join([P.ld, ...[...ids].map((id) => P.modes[id]), P.tonal]);
let css;
{ const S = p3 ? parts(toSrgbCss, false) : parts((x) => x, false), P = p3 ? parts((x) => x, true) : null; css = header('') + whole(S) + (P ? wrapP3(whole(P)) : '') + '\n'; }
// split: system.base.css (shared literals, light-dark() block, tonal) + system.<mode>.css, each with its own P3 upgrade.
const splitFiles = {};
if (opt.split) {
  const S = p3 ? parts(toSrgbCss, false, SHARED) : parts((x) => x, false, SHARED), P = p3 ? parts((x) => x, true, SHARED) : null;
  splitFiles['system.base.css'] = header('shared values' + (opt.lightDark ? ', light and dark' : '') + ', tonal; load first') + join([S.shared, S.ld, S.tonal]) + (P ? wrapP3(join([P.shared, P.ld, P.tonal])) : '') + '\n';
  for (const id of Object.keys(S.modes)) splitFiles['system.' + id + '.css'] = header('mode ' + id + '; load after system.base.css') + S.modes[id] + (P ? wrapP3(P.modes[id]) : '') + '\n';
}

// ── JSON, DTCG, Tailwind, Figma ───────────────────────────────────────────────────────────────────────────
const labelOfFam = (M, f) => labels[M.solidLabels[M.scheme][rampName(f)].label];
const roleText = (e) => { const l = roleStep(e, 'light'), d = roleStep(e, 'dark'), t = (x) => `${x.family} ${x.step}${x.alpha === 1 ? '' : ' @' + Math.round(x.alpha * 100) + '%'}`; return t(l) === t(d) ? t(l) : `${t(l)} · dark ${t(d)}`; };
const neutralsJson = () => ({ request: eff.neutrals, cross: neutrals.cross, families: { ground: 'ground', surface: 'surface', ink: 'ink' },
  rampKeys: { ground: 'ground', surface: 'surface', ink: 'gray' }, alias: '--colors-gray-* (and gray-a*) = var(--colors-ink-*): the ink ramp under the neutral family name, for compatibility',
  surfaceLift: SURFACE_LIFT, separationMin: SEPARATION_MIN, roles: Object.fromEntries(Object.entries(SPLIT_ROLES).map(([r, e]) => [r, roleText(e)])),
  extraRoles: { 'fg-subtle': 'ink 10 (as generated)', 'fg-strong': 'black / white, or ink 12 with an ink (light) or ground (dark) anchor', 'bg-selected': 'surface 3 → surface 4 → primary 3 by --ui-emphasis (light), surface 4 → primary solid (dark)', 'fg-selected': 'ink 12', 'neutral-*': 'ink (via gray)', 'white / black': 'ink 3 (endpoints)', labels: 'light label ground 1 (light), dark label ink 12 (light)' } });
const modeJson = (M) => ({ scheme: M.scheme, contrastMode: !!M.contrast, targetLift: M.lift ?? undefined, settings: M.settings, roles: M.roles, solidSteps: M.solidSteps[M.scheme], anchorReport: M.report, ...(neutrals ? { neutralSources: M.neutralSources[M.scheme], separation: M.separation } : {}),
  ramps: Object.fromEntries(fam.all.map((f) => [rampName(f), M.data.schemes[M.scheme][f].map((s, i) => ({ step: i + 1, css: s.css, oklch: s.oklch.map((x) => +x.toFixed(6)), hex: hex(s.oklch), tone: +toneOf(s.oklch).toFixed(2), apcaOnPage: +apcaLc(toneOf(s.oklch), toneOf(M.data.schemes[M.scheme][f][0].oklch)).toFixed(1) }))])),
  alpha: M.alpha && Object.fromEntries(Object.entries(M.alpha).map(([f, s]) => [rampName(f), s.map((x) => x.css)])), series: M.series, sequential: M.sequential, diverging: M.diverging, seriesCvd: M.seriesCvd,
  apca: M.apca, solidLabels: M.solidLabels[M.scheme], solidLabelContrast: Object.fromEntries(fam.all.map((f) => [rampName(f), r1(lcOn(labelOfFam(M, f), sw(M, f, 9)))])), keyRun: M.keyRun[M.scheme], contrast: M.contrastMatrix, tonalMap: M.tonalMap, variables: V[M.id] });
const json = { generator: 'spectrum-system@2', request: R0, ...(R0.preset ? { resolvedRequest: eff } : {}), target, selectors, familyNames, brightHues: brightHues ?? false, families: { all: fam.all.map(rampName), accents: fam.accents.map(rampName), neutrals: fam.neutrals.map(rampName) }, labelColors: { light: { css: labelCss.light, oklch: labels.light.map((x) => +x.toFixed(6)), from: neutrals ? 'light ground 1' : 'light gray 1' }, dark: { css: labelCss.dark, oklch: labels.dark.map((x) => +x.toFixed(6)), from: neutrals ? 'light ink 12' : 'light gray 12' } }, ...(neutrals ? { neutrals: neutralsJson() } : {}), diagnostics: { ...spectrumDiagnostics(modes.light.data, modes.light.roles), tonalAgreement }, modes: Object.fromEntries([...ids].map((id) => [id, modeJson(modes[id])])), tonal };
const okVal = (c) => ({ colorSpace: 'oklch', components: c.map((x) => +x.toFixed(6)), hex: hex(c) });
const dtcg = { $description: 'Colour system. Modes: ' + [...ids].join(', ') + '. OKLCH components; hex is an sRGB fallback.' };
for (const id of ids) { const M = modes[id], t = (dtcg[id] = {}); for (const f of fam.all) { const g = { $type: 'color' }; M.data.schemes[M.scheme][f].forEach((s, i) => { g[i + 1] = { $value: okVal(s.oklch) }; }); if (M.alpha) M.alpha[f].forEach((x, i) => { g['a' + (i + 1)] = { $value: { colorSpace: 'srgb', components: x.rgb.map((v) => +v.toFixed(6)), alpha: x.alpha } }; }); t[rampName(f)] = g; } if (neutrals) { t.ink = t.gray; t.gray = Object.fromEntries(Object.keys(t.ink).map((k) => [k, k === '$type' ? 'color' : { $value: `{${id}.ink.${k}}` }])); } }
if (tonal) { dtcg.palette = {}; for (const [f, t] of Object.entries(tonal)) { const g = (dtcg.palette[f] = { $type: 'color' }); t.stops.forEach((x) => { g[x.stop] = { $value: okVal(x.oklch) }; }); (t.primes || []).forEach((x) => { g[x.name] = { $value: okVal(x.oklch) }; }); } }
const twName = (k) => (k.startsWith('--palette-') ? '--color-' + k.slice('--palette-'.length) : '--color-' + k.replace(/^--colors-/, ''));
let tailwind = null;
if (opt.tailwind) { const lines = ['@import "./system.css";', '', '@theme inline {']; for (const k of Object.keys(V.light)) lines.push(`  ${twName(k)}: var(${k});`); for (const k of Object.keys(tonalVars)) lines.push(`  ${twName(k)}: var(${k});`); lines.push('}', ''); tailwind = lines.join('\n'); }
// Figma variables: a "Color" collection with a column per mode and a single-mode "Palette" collection. A role that points at a
// ramp step (directly or through other roles) is a VARIABLE_ALIAS to that step's variable id; translucent roles
// (color-mix … transparent) stay resolved, with alpha. resolvedValuesByMode always holds plain RGBA for tools without aliases.
let figma = null;
if (opt.figma) {
  const nameOf = (k) => (k.startsWith('--palette-role-') ? 'tonal-role/' + k.slice('--palette-role-'.length).replace(/-(\d+)$/, '/$1') : k.startsWith('--palette-') ? k.replace(/^--palette-/, '').replace(/-([\w]+)$/, '/$1') : k.replace(/^--colors-/, '').replace(/-(\d+|a\d+)$/, '/$1'));
  const idOf = (k) => (k.startsWith('--palette-') && !k.startsWith('--palette-role-') ? 'Palette:' : 'Color:') + nameOf(k);
  const isLiteral = (x) => x != null && !/^var\(/.test(x) && !/^color-mix\(/.test(x);
  const aliasTarget = (id, k) => { let cur = k; for (let d = 0; d < 6; d++) { const val = V[id][cur] ?? tonalVars[cur], m = /^var\((--[\w-]+)\)$/.exec(val || ''); if (!m) return cur === k ? null : isLiteral(val) ? cur : null; cur = m[1]; } return null; };
  const vars = [];
  for (const k of Object.keys(V.light)) {
    const valuesByMode = {}, resolvedValuesByMode = {}; let ok = true;
    for (const id of ids) { const c = resolveRGBA(modes[id], V[id][k]); if (!c) { ok = false; break; } resolvedValuesByMode[id] = c; const t = aliasTarget(id, k); valuesByMode[id] = t && (t in V[id] || (t in tonalVars)) ? { type: 'VARIABLE_ALIAS', id: idOf(t) } : c; }
    if (ok) vars.push({ id: idOf(k), name: nameOf(k), type: 'COLOR', valuesByMode, resolvedValuesByMode });
  }
  const pal = Object.entries(tonalVars).map(([k, x]) => { const [r, g, b] = rgbOf(parseOk(x)), c = { r: +r.toFixed(5), g: +g.toFixed(5), b: +b.toFixed(5), a: 1 }; return { id: idOf(k), name: nameOf(k), type: 'COLOR', valuesByMode: { default: c }, resolvedValuesByMode: { default: c } }; });
  figma = { $description: 'Figma variables (sRGB 0–1). valuesByMode holds RGBA or { type: "VARIABLE_ALIAS", id } pointing at another variable\'s id (ids are stable: "Color:<name>", "Palette:<name>"); resolvedValuesByMode is the same colour resolved, for importers without alias support. Import with a variables plugin or the Variables REST API.', collections: [{ name: 'Color', modes: [...ids], variables: vars }, ...(pal.length ? [{ name: 'Palette', modes: ['default'], variables: pal }] : [])] };
}

// ── Preview ───────────────────────────────────────────────────────────────────────────────────────────────
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const pageSel = (id) => forced(id).replace(eff.scope || '', '').trim();
const scopeCls = eff.scope && /^\.[\w-]+$/.test(eff.scope) ? eff.scope.slice(1) : '';
const attrsFor = (id) => { const s = pageSel(id); if (selectors === 'attribute') return (scopeCls ? `class="${scopeCls}" ` : '') + [...s.matchAll(/\[([\w-]+)=([\w-]+)\]/g)].map((m) => `${m[1]}="${m[2]}"`).join(' '); return 'class="' + (scopeCls ? scopeCls + ' ' : '') + s.split('.').filter(Boolean).join(' ') + '"'; };
const strip = () => fam.all.map((f) => `<div class="row"><code>${esc(rampName(f))}</code>${[...Array(12)].map((_, i) => `<span class="sw" style="background:var(${rampVar(f, i + 1)})"></span>`).join('')}</div>`).join('');
const rolesDemo = ['primary', 'secondary', 'critical', 'warning', 'success', 'info'].map((r) => `<span class="btn" style="background:var(--colors-${r}-solid);color:var(--colors-${r}-on-solid)">${r}</span><span class="chip" style="background:var(--colors-${r}-subtle);color:var(--colors-${r}-fg);box-shadow:inset 0 0 0 1px var(--colors-${r}-border)">${r} subtle</span>`).join('');
const bars = (n, pre, h) => `<div class="bars${h ? '' : ' seq'}">${[...Array(n)].map((_, i) => `<span style="${h ? `height:${40 + i * 9}px;` : ''}background:var(--colors-${pre}${i + 1})"></span>`).join('')}</div>`;
const contrastTable = (M) => { const c = M.contrastMatrix, rows = (xs) => xs.map((x) => `<tr class="${x.pass ? '' : 'miss'}"><td>${esc(x.fg)}</td><td>${esc(x.bg)}</td><td>${esc(x.intent)}</td><td><span class="pair" style="background:var(--colors-${x.bg});color:var(--colors-${x.fg})">Aa</span></td><td>Lc ${x.lc}</td><td>${x.threshold}</td><td>${x.pass ? '✓' : '✗'}</td><td>${x.ratio}:1</td></tr>`).join('');
  const head = '<tr><th>Foreground</th><th>Background</th><th>Intent</th><th></th><th>APCA</th><th>Needs</th><th>Pass</th><th>WCAG 2 (info)</th></tr>', miss = c.pairs.filter((x) => !x.pass);
  return `<h3>Contrast (APCA) · ${c.summary.fail} of ${c.summary.pairs} pairs under their threshold</h3>${miss.length ? `<table class="ct">${head}${rows(miss)}</table>` : '<p class="ok">Every pair meets its APCA threshold.</p>'}<details><summary>All ${c.summary.pairs} pairs</summary><table class="ct">${head}${rows(c.pairs)}</table></details>`; };
const cvdTable = (M) => { const c = M.seriesCvd; if (!c) return ''; return `<h3>Data series under colour-vision deficiency · min ΔE ${['normal', 'protan', 'deutan', 'tritan'].map((k) => `${k} ${c[k].minDE}`).join(', ')}${c.ok ? '' : ` · below ${c.threshold} under ${c.weakest}`}</h3><table class="ct cvd">${['normal', 'protan', 'deutan', 'tritan'].map((k) => `<tr class="${c[k].minDE < c.threshold ? 'miss' : ''}"><td>${k}</td><td>${c[k].hex.map((h) => `<span class="sw" style="background:${h}"></span>`).join('')}</td><td>min ΔE ${c[k].minDE} (series ${c[k].pair.join(' and ')})</td></tr>`).join('')}</table>`; };
// Neutrals split: the three families (ink under its own name) and a card on the page, per mode.
const neutralsDemo = (id) => { if (!neutrals) return ''; const S = modes[id].separation, row = (f) => `<div class="row"><code>${f}</code>${[...Array(12)].map((_, i) => `<span class="sw" style="background:var(--colors-${f}-${i + 1})"></span>`).join('')}</div>`;
  return `<h3>Neutrals · ground / surface / ink${neutrals.cross ? ' · cross (dark swaps the ground and surface sources)' : ''}</h3>${['ground', 'surface', 'ink'].map(row).join('')}<div class="page"><div class="card"><b>Card on the page</b><span>surface 1 on ground 1 · separation ΔE ${S.dE} (needs ${S.threshold}) ${S.pass ? '✓' : '✗'} · Lc ${S.lc}</span><span class="muted">fg-muted on surface</span><span class="well">bg-muted</span></div></div>`; };
const panel = (id) => `<section ${attrsFor(id)} style="background:var(--colors-bg);color:var(--colors-fg)"><h2>${esc(id)}</h2>${strip()}${neutralsDemo(id)}<h3>Roles</h3><div class="roles">${rolesDemo}</div>${opt.series ? '<h3>Data series · sequential</h3>' + bars(6, 'data-', true) + bars(7, 'data-seq-', false) : ''}${opt.diverging ? '<h3>Diverging</h3>' + bars(11, 'data-div-', false) : ''}${contrastTable(modes[id])}${cvdTable(modes[id])}</section>`;
const tonalPanel = tonal ? `<section ${scopeCls ? `class="${scopeCls}" ` : ''}style="background:#fff;color:#111"><h2>Tonal 050–950${opt.primes ? ' · Primes' : ''} (mode-independent)</h2>${Object.entries(tonal).map(([f, t]) => `<div class="row"><code>${esc(f)}</code>${t.stops.map((x) => `<span class="sw" title="${x.stop}" style="background:var(--palette-${f}-${x.stop})"></span>`).join('')}${(t.primes || []).map((x) => `<span class="sw prime" title="${x.name}" style="background:var(--palette-${f}-${x.name})"></span>`).join('')}</div>`).join('')}</section>` : '';
const preview = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Colour system preview</title><style>${css}
body{margin:0;font:14px/1.4 system-ui,sans-serif} section{padding:24px;overflow-x:auto} h2{margin:0 0 12px} h3{margin:20px 0 8px;font-size:13px;color:var(--colors-fg-muted)}
.row{display:flex;align-items:center;gap:4px;margin:3px 0}.row code{width:80px;font-size:12px;opacity:.7}.sw{display:inline-block;width:30px;height:22px;border-radius:4px;vertical-align:middle;margin-right:2px}.sw.prime{border-radius:50%;width:22px;margin-left:4px}
.roles{display:flex;flex-wrap:wrap;gap:8px}.btn,.chip{padding:6px 12px;border-radius:8px}.bars{display:flex;align-items:flex-end;gap:6px;height:100px;padding:8px;background:var(--colors-bg-subtle);border-radius:8px}.bars span{width:36px;border-radius:4px 4px 0 0}
.bars.seq{height:auto;margin-top:8px}.bars.seq span{height:24px;border-radius:4px}
.ct{border-collapse:collapse;font-size:12px;margin:4px 0}.ct td,.ct th{padding:3px 8px;border-bottom:1px solid var(--colors-border);text-align:left}.ct tr.miss td{color:var(--colors-critical-fg);font-weight:600}.pair{display:inline-block;padding:0 6px;border-radius:4px;box-shadow:inset 0 0 0 1px var(--colors-border)}
details summary{cursor:pointer;font-size:12px;color:var(--colors-fg-muted);margin:6px 0}.ok{font-size:12px}${neutrals ? `
.page{background:var(--colors-bg);padding:16px;border-radius:8px;max-width:520px}.card{display:flex;flex-direction:column;gap:6px;background:var(--colors-surface);border:1px solid var(--colors-border);border-radius:8px;padding:12px}.card .muted{color:var(--colors-fg-muted)}.card .well{background:var(--colors-bg-muted);border-radius:6px;padding:4px 8px}` : ''}</style></head><body>${[...ids].map(panel).join('')}${tonalPanel}</body></html>`;

// ── Write ─────────────────────────────────────────────────────────────────────────────────────────────────
mkdirSync(values.out, { recursive: true });
writeFileSync(values.out + '/request.json', JSON.stringify(R0, null, 2) + '\n');
writeFileSync(values.out + '/system.css', css);
for (const [f, s] of Object.entries(splitFiles)) writeFileSync(values.out + '/' + f, s);
writeFileSync(values.out + '/system.json', JSON.stringify(json, null, 2) + '\n');
if (opt.dtcg) writeFileSync(values.out + '/tokens.dtcg.json', JSON.stringify(dtcg, null, 2) + '\n');
if (tailwind) writeFileSync(values.out + '/tailwind.css', tailwind);
if (figma) writeFileSync(values.out + '/figma-variables.json', JSON.stringify(figma, null, 2) + '\n');
writeFileSync(values.out + '/preview.html', preview);
if (opt.showcase) writeFileSync(values.out + '/showcase.html', showcaseHtml({ json, css, forced, p3 }));
const weak = (id) => Object.entries(json.modes[id].solidLabelContrast).sort((a, b) => a[1] - b[1])[0];
const lcLine = [...ids].map((id) => `${id} ${modes[id].contrastMatrix.summary.fail}`).join(', ');
const sepLine = neutrals ? '; separation surface 1 vs ground 1 (OKLab ΔE): ' + [...ids].map((id) => `${id} ${modes[id].separation.dE}`).join(', ') + ([...ids].some((id) => !modes[id].separation.pass) ? `; WARNING separation under ${SEPARATION_MIN} in ${[...ids].filter((id) => !modes[id].separation.pass).join(', ')}` : '') : '';
const cvdLow = opt.series ? [...ids].filter((id) => !modes[id].seriesCvd.ok) : [];
const cvdLine = opt.series ? '; series min ΔE (CVD): ' + [...ids].map((id) => { const c = modes[id].seriesCvd; return `${id} ${c[c.weakest].minDE} (${c.weakest})`; }).join(', ') + (cvdLow.length ? `; WARNING series under ${CVD_MIN} ΔE in ${cvdLow.join(', ')}` : '') : '';
console.log(`wrote ${values.out}: modes ${[...ids].join(', ')}; ${fam.accents.length} accents + ${fam.neutrals.length} neutral; ${tonal ? 'tonal 050–950' + (opt.primes ? ' + primes' : '') + '; ' : ''}target ${target}${p3 ? ' (sRGB + P3 upgrade)' : ''}${opt.split ? '; split CSS' : ''}${opt.showcase ? '; showcase.html' : ''}; weakest solid vs label (APCA): ` + [...ids].map((id) => `${id} Lc ${weak(id)[1]} (${weak(id)[0]}, floor ${modes[id].apca.solid})`).join(', ') + `; contrast pairs under their APCA threshold: ${lcLine} (system.json › modes.<id>.contrast)` + cvdLine + sepLine);
