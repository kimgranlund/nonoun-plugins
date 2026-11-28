#!/usr/bin/env node
// families.mjs — lay a color system out one family per file, light and dark resolved by color-scheme.
// Reads a system.mjs output folder (its system.json) and writes, into a new folder:
//   globals.css                        color-scheme only (:root follows the OS; .light / .dark and data-color-mode force one)
//   colors-p3/<family>.css|.json|.dtcg.json, semantic.css|.json|.dtcg.json, index.css   values in the system's target gamut
//   colors/…                           the same files with every value mapped into sRGB
//   manifest.json  README.md  USAGE.md registry and docs, generated from the same data
// A token that differs by scheme is written as three variables, --x-light, --x-dark and --x: light-dark(var(--x-light), var(--x-dark));
// a token equal in both schemes is written once. --from-p3 takes colors-p3/ from a second, P3-tuned run (anchors with "p3")
// and colors/ from --from. README.md and manifest.json say how much of P3 colors-p3/ uses. Contract: ../references/system.md › Family files.
// Usage: node families.mjs --from SYSTEM_OUTPUT_DIR [--from-p3 P3_SYSTEM_OUTPUT_DIR] --out NEW_DIR [--light light] [--dark dark]
// Exit codes: 0 written; 2 bad arguments or an input it cannot lay out.
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { parseArgs } from 'node:util';
import { clampChroma } from './system/anchors.js';
import { dtcgColor } from './system/dtcg.js';

const fail = (code, msg) => { console.error(msg); process.exit(code); };
const USAGE = 'usage: node families.mjs --from SYSTEM_OUTPUT_DIR [--from-p3 P3_SYSTEM_OUTPUT_DIR] --out NEW_DIR [--light <mode id>] [--dark <mode id>]';
let values; try { ({ values } = parseArgs({ options: { from: { type: 'string' }, 'from-p3': { type: 'string' }, out: { type: 'string' }, light: { type: 'string', default: 'light' }, dark: { type: 'string', default: 'dark' } } })); } catch (e) { fail(2, e.message + '\n' + USAGE); }
if (!values.from || !values.out) fail(2, USAGE);
if (existsSync(values.out) && readdirSync(values.out).length) fail(2, `--out ${values.out} must be a new or empty folder`);
const J = JSON.parse(readFileSync(join(values.from, 'system.json'), 'utf8'));
const L = J.modes?.[values.light], D = J.modes?.[values.dark];
if (!L || !D) fail(2, `system.json needs modes ${values.light} and ${values.dark} (have ${Object.keys(J.modes || {}).join(', ')})`);
if (L.scheme !== 'light' || D.scheme !== 'dark') fail(2, `--light must name a light-scheme mode and --dark a dark-scheme mode (light-dark() resolves by color-scheme)`);
const FAM = J.families.all, ACC = new Set(J.families.accents), GAMUT = J.target === 'display-p3' ? 'p3' : 'srgb';
// --from-p3: the P3-tuned run, which must target display-p3 and have the same families and the same two modes.
let JP = null;
if (values['from-p3']) {
  JP = JSON.parse(readFileSync(join(values['from-p3'], 'system.json'), 'utf8'));
  if (JP.target !== 'display-p3') fail(2, `--from-p3 ${values['from-p3']} targets ${JP.target}, not display-p3`);
  if (JP.families?.all?.join(',') !== FAM.join(',')) fail(2, `--from-p3 has families ${JP.families?.all?.join(', ')}, not ${FAM.join(', ')} (same hue set and neutrals in both runs)`);
  if (JP.modes?.[values.light]?.scheme !== 'light' || JP.modes?.[values.dark]?.scheme !== 'dark') fail(2, `--from-p3 needs a light-scheme mode ${values.light} and a dark-scheme mode ${values.dark}`);
}

// ── Colour maths (OKLCH ↔ linear RGB, OKLab ΔE): enough to print components and hex fallbacks ──────────────
const M3 = (M, v) => M.map((r) => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]);
const LMS2XYZ = [[1.2268798758459243, -0.5578149944602171, 0.2813910456659647], [-0.0405757452148008, 1.112286803280317, -0.0717110580655164], [-0.0763729366746601, -0.4214933324022432, 1.5869240198367816]];
const XYZ2SRGB = [[3.2409699419045226, -1.537383177570094, -0.4986107602930034], [-0.9692436362808796, 1.8759675015077202, 0.04155505740717559], [0.05563007969699366, -0.20397695888897652, 1.0569715142428786]];
const XYZ2P3 = [[2.4934969119414254, -0.9313836179191239, -0.40271078445071684], [-0.8294889695615747, 1.7626640603183463, 0.023624685841943577], [0.03584583024378447, -0.07617238926804182, 0.9568845240076872]];
const SRGB2XYZ = [[0.41239079926595934, 0.357584339383878, 0.1804807884018343], [0.21263900587151027, 0.715168678767756, 0.07219231536073371], [0.01933081871559182, 0.11919477979462598, 0.9505321522496607]];
const XYZ2LMS = [[0.819022437996703, 0.3619062600528904, -0.1288737815209879], [0.0329836539323885, 0.9292868615863434, 0.0361446663506424], [0.0481771893596242, 0.2642395317527308, 0.6335478284694309]];
const LMS2LAB = [[0.210454268309314, 0.7936177747023054, -0.0040720430116193], [1.9779985324311684, -2.42859224204858, 0.450593709617411], [0.0259040424655478, 0.7827717124575296, -0.808675754873059]];
const enc = (v) => Math.sign(v) * (Math.abs(v) <= 0.0031308 ? 12.92 * Math.abs(v) : 1.055 * Math.abs(v) ** (1 / 2.4) - 0.055);
const dec = (v) => Math.sign(v) * (Math.abs(v) <= 0.04045 ? Math.abs(v) / 12.92 : ((Math.abs(v) + 0.055) / 1.055) ** 2.4);
const xyzOfOklch = ([l0, c, h]) => { const a = c * Math.cos(h * Math.PI / 180), b = c * Math.sin(h * Math.PI / 180);
  const l = l0 + 0.3963377774 * a + 0.2158037573 * b, m = l0 - 0.1055613458 * a - 0.0638541728 * b, s = l0 - 0.0894841775 * a - 1.291485548 * b; return M3(LMS2XYZ, [l ** 3, m ** 3, s ** 3]); };
const oklchOfXyz = (x) => { const o = M3(LMS2LAB, M3(XYZ2LMS, x).map(Math.cbrt)), C = Math.hypot(o[1], o[2]); let H = Math.atan2(o[2], o[1]) * 180 / Math.PI; if (H < 0) H += 360; return [o[0], C, C < 1e-4 ? 0 : H]; };
const r4 = (x) => +(+x).toFixed(4) || 0;
const clip = (v) => Math.min(1, Math.max(0, v));
const hexOf = (rgb) => '#' + rgb.map((v) => Math.round(clip(v) * 255).toString(16).padStart(2, '0')).join('');

// A colour value of the system: oklch(L C H) or color(srgb r g b / a). Returns it in the folder's gamut plus its descriptions.
function parse(css) {
  const n = (css.match(/-?[\d.]+(?:e-?\d+)?/g) || []).map(Number);
  if (css.startsWith('oklch(')) return { oklch: n.slice(0, 3), alpha: css.includes('/') ? n[3] : 1 };
  if (css.startsWith('color(srgb ')) return { oklch: oklchOfXyz(M3(SRGB2XYZ, n.slice(0, 3).map(dec))), alpha: css.includes('/') ? n[3] : 1, srgbIn: n.slice(0, 3) };
  return null;
}
const isColor = (css) => /^(oklch\(|color\(srgb )/.test(css);
const tidy = (css) => css.replace(/-?\d+(?:\.\d+)?e-\d+/g, '0').replace(/(\d+\.\d{4})\d+/g, '$1');
function inGamut(css, g) { // the CSS value written into folder g
  const p = parse(css); if (!p) return tidy(css);
  if (p.srgbIn) return tidy(css); // alpha steps are sRGB already
  const [l, c, h] = p.oklch, cc = g === 'srgb' ? clampChroma(l, c, h, 'srgb') : c;
  return `oklch(${r4(l)} ${r4(cc)} ${+h.toFixed(g === 'srgb' ? 2 : 4)}${p.alpha < 1 ? ' / ' + r4(p.alpha) : ''})`;
}
function describe(css, g) {
  const p = parse(css), x = xyzOfOklch(p.oklch), srgb = M3(XYZ2SRGB, x).map(enc), p3 = M3(XYZ2P3, x).map(enc);
  return { css, oklch: p.oklch.map(r4), [g === 'p3' ? 'displayP3' : 'srgb']: (g === 'p3' ? p3 : srgb).map((v) => r4(clip(v))), alpha: r4(p.alpha), hex: hexOf(srgb) };
}
function dtcg(css, g) { const d = describe(css, g); return dtcgColor(g === 'p3' ? 'display-p3' : 'srgb', g === 'p3' ? d.displayP3 : d.srgb, d.alpha, d.hex); }
const trio = (name, l, d) => l === d ? [`  ${name}: ${l};`] : [`  ${name}-light: ${l};`, `  ${name}-dark: ${d};`, `  ${name}: light-dark(var(${name}-light), var(${name}-dark));`];

// ── Layout ─────────────────────────────────────────────────────────────────────────────────────────────────
const out = values.out, files = [];
const put = (rel, text) => { const p = join(out, rel); mkdirSync(join(p, '..'), { recursive: true }); writeFileSync(p, text); files.push(rel); };
const famRe = new RegExp(`^--colors-(${FAM.join('|')})-(a?\\d+)$`);
const gamuts = JP ? [['p3', 'colors-p3', JP], ['srgb', 'colors', J]] : GAMUT === 'p3' ? [['p3', 'colors-p3', J], ['srgb', 'colors', J]] : [['srgb', 'colors', J]];
const gamutName = { p3: 'display-p3', srgb: 'srgb' };
const head = (g, what) => `/* ${what} · ${g === 'p3' ? 'Display P3 (oklch inside the P3 gamut)' : 'sRGB (oklch mapped into sRGB)'} · light and dark generated separately. Needs ../globals.css. */\n`;
let tokens = 0;
for (const [g, dir, src] of gamuts) {
  const lv = src.modes[values.light].variables, dv = src.modes[values.dark].variables;
  for (const f of FAM) {
    const css = [head(g, `${f}: steps 1–12, alpha steps, tonal scale`) + ':root {'], json = { family: f, kind: ACC.has(f) ? 'accent' : 'neutral', gamut: gamutName[g], steps: {}, alpha: {}, tonal: {} }, dt = { colors: { [f]: { light: {}, dark: {}, alpha: { light: {}, dark: {} }, tonal: {} } } };
    for (const [prefix, group] of [['', 'steps'], ['a', 'alpha']]) for (let s = 1; s <= 12; s++) {
      const n = `--colors-${f}-${prefix}${s}`; if (lv[n] == null || dv[n] == null) continue;
      const l = inGamut(lv[n], g), d = inGamut(dv[n], g); css.push(...trio(n, l, d)); tokens += 2;
      json[group][prefix + s] = { light: describe(l, g), dark: describe(d, g) };
      const t = group === 'steps' ? dt.colors[f] : dt.colors[f].alpha; t.light[prefix + s] = dtcg(l, g); t.dark[prefix + s] = dtcg(d, g);
    }
    for (const st of src.tonal?.[f]?.stops || []) { const v = inGamut(`oklch(${st.oklch.join(' ')})`, g); css.push(`  --palette-${f}-${st.stop}: ${v};`); json.tonal[st.stop] = describe(v, g); dt.colors[f].tonal[st.stop] = dtcg(v, g); tokens++; }
    css.push('}', '');
    put(`${dir}/${f}.css`, css.join('\n')); put(`${dir}/${f}.json`, JSON.stringify(json, null, 2) + '\n'); put(`${dir}/${f}.dtcg.json`, JSON.stringify(dt, null, 2) + '\n');
  }
  const names = [...new Set([...Object.keys(lv), ...Object.keys(dv)])].filter((k) => !famRe.test(k) && !k.startsWith('--palette-') && lv[k] != null && dv[k] != null);
  const css = [head(g, 'semantic roles') + ':root {'], json = { gamut: gamutName[g], roles: {} }, dt = { colors: {} };
  const ref = (v, mode) => { const m = v.match(/^var\(--colors-([\w-]+)\)$/); if (!m) return null; const fm = ('--colors-' + m[1]).match(famRe);
    return fm ? (fm[2].startsWith('a') ? `{colors.${fm[1]}.alpha.${mode}.${fm[2]}}` : `{colors.${fm[1]}.${mode}.${fm[2]}}`) : `{colors.${m[1]}.${mode}}`; };
  for (const n of names) { const l = inGamut(lv[n], g), d = inGamut(dv[n], g); css.push(...trio(n, l, d)); tokens += 2;
    const id = n.replace(/^--colors-/, ''); json.roles[id] = { light: l, dark: d };
    const one = (v, mode) => { const r = ref(v, mode); return r ? { $type: 'color', $value: r } : isColor(v) ? dtcg(v, g) : { $value: v }; };
    dt.colors[id] = { light: one(l, 'light'), dark: one(d, 'dark') }; }
  css.push('}', '');
  put(`${dir}/semantic.css`, css.join('\n')); put(`${dir}/semantic.json`, JSON.stringify(json, null, 2) + '\n'); put(`${dir}/semantic.dtcg.json`, JSON.stringify(dt, null, 2) + '\n');
  put(`${dir}/index.css`, `/* Everything, in order: globals, every family, then the semantic roles. */\n@import "../globals.css";\n${FAM.map((f) => `@import "./${f}.css";`).join('\n')}\n@import "./semantic.css";\n`);
}
put('globals.css', `/* Which scheme light-dark() resolves to. No colours here.\n   :root follows the OS; .light / .dark (or data-color-mode) force a scheme on any subtree. */\n:root {\n  color-scheme: light dark;\n}\n.light,\n[data-color-mode="light"] {\n  color-scheme: light;\n}\n.dark,\n[data-color-mode="dark"] {\n  color-scheme: dark;\n}\n`);

// ── P3 usage: how much of Display P3 colors-p3/ uses (system.md › Family files) ───────────────────────────────
// Each ramp swatch of the colors-p3 run's two modes against its sRGB mapping (chroma clamped at its OKLCH lightness and hue),
// OKLab ΔE × 100: outside sRGB at P3_OUTSIDE or more, visibly over P3_VISIBLE. The counts system.mjs prints for that run; when
// one run fills both folders, this is how far colors-p3/ is from colors/.
const P3_OUTSIDE = 0.01, P3_VISIBLE = 2;
function usageOf(M) {
  const out = [];
  for (const [f, steps] of Object.entries(M.ramps)) for (const x of steps) { const [l, c, h] = x.oklch, d = 100 * (c - clampChroma(l, c, h, 'srgb')); if (d >= P3_OUTSIDE) out.push({ f, step: x.step, d }); }
  const n = Object.values(M.ramps).reduce((a, r) => a + r.length, 0), ds = out.map((x) => x.d).sort((a, b) => a - b), top = out.reduce((a, x) => (!a || x.d > a.d ? x : a), null), r = (x, k) => +x.toFixed(k);
  const median = ds.length ? (ds.length % 2 ? ds[ds.length >> 1] : (ds[ds.length / 2 - 1] + ds[ds.length / 2]) / 2) : 0, visible = out.filter((x) => x.d > P3_VISIBLE).length;
  return { swatches: n, outsideSrgb: out.length, share: r(100 * out.length / n, 1), visible, visibleShare: r(100 * visible / n, 1), maxDE: r(top?.d ?? 0, 2), medianDE: r(median, 2), largest: top ? `${top.f} ${top.step}` : null };
}
const p3Src = gamuts.find(([g]) => g === 'p3')?.[2];
const p3Usage = p3Src && { method: `ramp swatches of the colors-p3 run against their sRGB mapping, OKLab ΔE × 100; outside sRGB at ${P3_OUTSIDE} or more, visibly over ${P3_VISIBLE}; ΔE over the swatches outside sRGB`, ...Object.fromEntries([values.light, values.dark].map((id) => [id, usageOf(p3Src.modes[id])])) };
const usageLine = (id) => { const u = p3Usage[id]; return `${u.outsideSrgb} of ${u.swatches} ${id} ramp swatches (${u.share}%; ${u.visible} visibly, ${u.visibleShare}%, over ΔE ${P3_VISIBLE}; largest ΔE ${u.maxDE}${u.largest ? ', ' + u.largest : ''})`; };
const usageText = !p3Usage ? '' : (JP ? `\`colors-p3/\` is laid out from a P3-tuned run (\`manifest.json › generator.p3Request\`), \`colors/\` from the sRGB run. The P3 run leaves sRGB in ` : `\`colors-p3/\` differs from \`colors/\` in `)
  + `${usageLine(values.light)} and ${usageLine(values.dark)} (\`manifest.json › p3Usage\`). Under 5% outside sRGB, the two folders look the same on a wide-gamut screen: anchor with \`"p3": "edge"\` or raise \`keyIntensity\`${JP ? '' : ', or lay out a P3-tuned run with `--from-p3`'}.\n\n`;

// ── Docs, generated from the same data so they can't drift from the values ──────────────────────────────────
const dir0 = gamuts[0][1], sem = JSON.parse(readFileSync(join(out, dir0, 'semantic.json'), 'utf8')).roles;
const labelsBy = (M, lbl) => FAM.filter((f) => M.solidLabels?.[f]?.label === lbl);
const darkBoth = labelsBy(L, 'dark').filter((f) => labelsBy(D, 'dark').includes(f)), darkOnlyDark = labelsBy(D, 'dark').filter((f) => !darkBoth.includes(f)), darkOnlyLight = labelsBy(L, 'dark').filter((f) => !darkBoth.includes(f));
const list = (a) => a.length ? a.join(', ') : 'none';
const roleStep = (id) => { const v = sem[id]?.light ?? ''; const m = v.match(/^var\(--colors-([a-z]+)-(a?\d+)\)$/); return m ? `${m[1]} ${m[2]}` : 'own value'; };
// One entry per group: id, name, its steps, the group's use, and each step's own use (same order as the steps).
const STEPS = [['backgrounds', 'Backgrounds', [1, 2], 'The page (1) and quiet areas on it (2)', ['The page', 'Quiet areas on the page']],
  ['interactive', 'Interactive components', [3, 4, 5], 'A component\'s fill at rest (3), on hover (4), pressed or selected (5)', ['A component\'s fill at rest', 'A component\'s fill on hover', 'A component\'s fill pressed or selected']],
  ['borders', 'Borders and separators', [6, 7, 8], 'Separators (6), a control\'s border and the focus ring (7), its hover border (8)', ['Separators', 'A control\'s border and the focus ring', 'A control\'s border on hover']],
  ['solid', 'Solid colors', [9, 10], 'The purest colour (9) and its hover (10)', ['The purest colour', 'The purest colour on hover']],
  ['text', 'Accessible text', [11, 12], 'Low-contrast (11) and high-contrast (12) text', ['Low-contrast text', 'High-contrast text']]];
// The pairing rules: manifest.json › pairings, and the "Pairing:" line and hover sentence of USAGE.md are written from these.
const PAIRINGS = [
  { id: 'text-on-step', text: [11, 12], on: [1, 5], rule: 'text 11–12 on steps 1–5' },
  { id: 'component-border', component: [3, 5], border: 7, hoverBorder: 8, rule: 'a component on 3–5 takes border 7, then 8 on hover' },
  { id: 'on-solid', solid: [9, 10], token: '-on-solid', rule: 'text on a solid (9–10) is the role\'s `-on-solid`, never a step picked by eye' },
  { id: 'hover', within: 'group', up: 1, pairs: [[3, 4], [7, 8], [9, 10]], rule: 'Hover is one step up within its group (3→4, 7→8, 9→10)' }];
const pairingLine = PAIRINGS.filter((p) => p.id !== 'hover').map((p) => p.rule).join('; '), hoverRule = PAIRINGS.find((p) => p.id === 'hover').rule;
const anchored = (M) => (M.anchorReport || []).map((x) => ({ family: x.family, role: x.role, value: x.source?.value ?? x.value }));
put('USAGE.md', `# Using the colors

Generated by \`ui-colors/scripts/families.mjs\` from the system's own data. File layout and naming: [README.md](README.md).

## The 12 steps

| Steps | Group | For |
|---|---|---|
${STEPS.map(([, n, s, u]) => `| ${s[0]}–${s.at(-1)} | **${n}** | ${u} |`).join('\n')}

Steps are spaced by APCA contrast against step 1, so a step means the same in every family and in both schemes${anchored(L).length ? ', except where a family is anchored (below)' : ''}. ${hoverRule}.

Pairing: ${pairingLine}.

## Text on solids

- Dark text in both schemes: ${list(darkBoth)}.
- Dark text in dark only: ${list(darkOnlyDark)}.
- Dark text in light only: ${list(darkOnlyLight)}.
- Every other family takes light text. \`manifest.json › families[].solidLabel\` has each family per scheme.
${anchored(L).length ? `\n## Anchored families\n\nThese families have a pinned colour; the rest of each ramp is generated around it, and the pinned step may sit off the contrast spacing (\`manifest.json › anchors\`).\n\n| Family | Pinned | By |\n|---|---|---|\n${anchored(L).map((a) => `| ${a.family} | \`${a.value}\` | ${a.role.startsWith('family:') ? 'family anchor' : a.role + ' anchor'} |`).join('\n')}\n` : ''}
## Alpha steps

\`a1\`–\`a12\` match steps 1–12 when composited over neutral step 1 (the page). Use them over images, varied surfaces and in overlays; over any other background they differ from the solid steps and their contrast figures don't apply.

## Roles or steps

Use a role when the colour means something (page, text, primary action, error), a step when the hue is the content (a tag, a category, a legend).

| Role | Light value |
|---|---|
${['bg', 'bg-subtle', 'bg-muted', 'border', 'border-strong', 'control-border', 'fg', 'fg-muted', 'primary-subtle', 'primary-border', 'primary-solid', 'primary-solid-hover', 'primary-fg', 'focus-ring', 'bg-inverse', 'bg-disabled', 'fg-disabled'].filter((r) => sem[r]).map((r) => `| \`${r}\` | ${roleStep(r)} |`).join('\n')}

Roles as resolved: ${Object.entries(L.roles).filter(([r]) => !/^data/.test(r)).map(([r, f]) => `${r} ${f === 'neutral' ? 'gray' : f}`).join(', ')}. Every role with both values: \`manifest.json › roles\`.
`);
put('README.md', `# Color tokens

${FAM.length} families (${J.families.accents.length} accents, ${J.families.neutrals.length} neutrals), 12 steps and 12 alpha steps each${J.tonal ? ', plus a tonal scale 050–950' : ''}, and semantic roles. Light and dark were generated separately; how to use them: [USAGE.md](USAGE.md). Registry: \`manifest.json\`.

## Files

\`\`\`
globals.css            color-scheme only
${gamuts.map(([g, d]) => `${d}/${' '.repeat(Math.max(1, 14 - d.length))}${g === 'p3' ? 'Display P3 values' : 'values mapped into sRGB'}: <family>.css|.json|.dtcg.json, semantic.*, index.css`).join('\n')}
manifest.json  README.md  USAGE.md
\`\`\`

${gamuts.length > 1 ? 'Pick one of `colors-p3/` (wide-gamut screens get the P3 colour; others map it) or `colors/` (identical everywhere: email, print, sRGB-only tools). ' : ''}Import \`index.css\`, or \`../globals.css\`, the families you use and \`semantic.css\` (it needs every family its roles name).

${usageText}## Light and dark

\`\`\`css
--colors-${FAM[0]}-1-light: …;
--colors-${FAM[0]}-1-dark:  …;
--colors-${FAM[0]}-1: light-dark(var(--colors-${FAM[0]}-1-light), var(--colors-${FAM[0]}-1-dark));
\`\`\`

Use the plain name. \`light-dark()\` resolves from \`color-scheme\`: \`:root\` follows the OS, \`.light\` / \`.dark\` (or \`data-color-mode\`) force it on any element. A token equal in both schemes has only the plain name. Needs Chrome 123, Safari 17.5, Firefox 120 or later.

## Naming

| Token | CSS | DTCG |
|---|---|---|
| Step | \`--colors-<family>-<1…12>\` | \`colors.<family>.<light\\|dark>.<n>\` |
| Alpha step | \`--colors-<family>-a<1…12>\` | \`colors.<family>.alpha.<light\\|dark>.a<n>\` |
| Tonal stop | \`--palette-<family>-<050…950>\` | \`colors.<family>.tonal.<stop>\` |
| Role | \`--colors-<role>\` | \`colors.<role>.<light\\|dark>\` (aliases) |

Regenerate with the request in \`manifest.json › generator.request\` and \`families.mjs\`; hand edits don't survive.
`);
const sha = (rel) => { const b = readFileSync(join(out, rel)); return { path: rel, bytes: b.length, sha256: createHash('sha256').update(b).digest('hex') }; };
const manifest = {
  name: 'color-tokens', generated: new Date().toISOString().replace(/\.\d+Z$/, 'Z'), generator: { system: J.generator, request: J.request, from: { light: values.light, dark: values.dark }, ...(JP ? { p3Request: JP.request } : {}) }, target: J.target,
  conventions: { step: '--colors-<family>-<1…12>', alpha: '--colors-<family>-a<1…12>', tonal: '--palette-<family>-<050…950>', role: '--colors-<role>', modes: '<name>-light, <name>-dark, <name>: light-dark(var(<name>-light), var(<name>-dark)); one variable when equal' },
  stepGroups: STEPS.map(([id, name, steps]) => ({ id, name, steps })),
  steps: STEPS.flatMap(([group, , steps, , uses]) => steps.map((step, i) => ({ step, group, use: uses[i] }))),
  pairings: PAIRINGS,
  families: FAM.map((f) => ({ id: f, kind: ACC.has(f) ? 'accent' : 'neutral', solidLabel: { light: L.solidLabels?.[f]?.label ?? null, dark: D.solidLabels?.[f]?.label ?? null } })),
  anchors: anchored(L), roles: Object.fromEntries(Object.entries(sem).map(([id, v]) => [id, { light: v.light, dark: v.dark, modeDependent: v.light !== v.dark }])),
  contrast: Object.fromEntries([[values.light, L], [values.dark, D]].map(([id, M]) => [id, { apca: M.apca, pairsUnderThreshold: M.contrast?.summary?.fail ?? M.contrast?.summary?.failures?.length ?? null, hoverUnderThreshold: M.hover?.summary?.failures ?? [] }])),
  ...(p3Usage ? { p3Usage } : {}),
  files: files.filter((f) => f !== 'manifest.json').map(sha),
};
put('manifest.json', JSON.stringify(manifest, null, 2) + '\n');
console.log(`wrote ${out}: ${FAM.length} families × ${gamuts.length} gamut(s), ${files.length} files (globals, families, semantic, index, manifest, README, USAGE)`);
