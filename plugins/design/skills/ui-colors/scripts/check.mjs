#!/usr/bin/env node
// check.mjs — regression check for scripts/system.mjs (contract: ../references/system.md › Checks).
// Runs system.mjs on {}, a light-dark/split/Figma request, two showcase requests and an APCA-override anchored request in a temporary directory, verifies the outputs, then runs
// negative controls: each mutates a copy of the output (or the fixture) and must make its check fail.
// Usage: node check.mjs [--keep]   (--keep leaves the temporary directory and prints its path)
// Exit codes: 0 all checks pass and every negative control bites; 1 otherwise.
import { readFileSync, writeFileSync, mkdtempSync, existsSync, rmSync, cpSync, unlinkSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { apcaLc, generateSpectrum, normalizeSpectrum, spectrumOverrides } from './system/index.js';
import { clampChroma, shapeKeys } from './system/anchors.js';

const here = fileURLToPath(new URL('.', import.meta.url));
const keep = process.argv.includes('--keep');
const tmp = mkdtempSync(join(tmpdir(), 'hct-check-'));
const results = [];
const record = (name, failures) => { results.push({ name, failures }); console.log(`${failures.length ? 'FAIL' : 'pass'}  ${name}${failures.length ? '\n      ' + failures.slice(0, 5).join('\n      ') + (failures.length > 5 ? `\n      … ${failures.length - 5} more` : '') : ''}`); };

// ── Independent colour maths (not imported from system.mjs, so a bug there can't hide here) ───────────────
const lin = ([L, C, H]) => { const a = C * Math.cos(H * Math.PI / 180), b = C * Math.sin(H * Math.PI / 180);
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3;
  return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s].map((v) => Math.min(1, Math.max(0, v))); };
const lumOk = (c) => { const v = lin(c); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
const wcag = (y1, y2) => (Math.max(y1, y2) + 0.05) / (Math.min(y1, y2) + 0.05);
const ratioOk = (a, b) => wcag(lumOk(a), lumOk(b));
const toneOk = (c) => { const y = lumOk(c); return y > 0.008856 ? 116 * Math.cbrt(y) - 16 : 903.3 * y; };
const lab = ([L, C, H]) => [L, C * Math.cos(H * Math.PI / 180), C * Math.sin(H * Math.PI / 180)];
const dE = (p, q) => { const a = lab(p), b = lab(q); return 100 * Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]); };
const nums = (s) => (s.match(/-?[\d.]+/g) || []).map(Number);
const readJson = (p) => JSON.parse(readFileSync(p, 'utf8'));

function runSystem(request, out) {
  const rq = out + '.request.json'; writeFileSync(rq, JSON.stringify(request));
  return execFileSync(process.execPath, [here + 'system.mjs', '--request', rq, '--out', out], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
}

// ── Checks: each returns a list of failures ─────────────────────────────────────────────────────────────
// 1. Fixture. fixtures/hct-default.json records the raw engine ramps (before solids are solved and the control border is held)
// at the APCA targets it was made with — light 7.3…85.7, dark 3.4…77.1, older than today's defaults. So the check measures those
// targets from the fixture's own neutral, regenerates the raw engine ramps at them and compares all 12 steps of every family.
function checkFixture(fx) {
  const f = [], measure = (mode) => { const n = fx[mode].neutral.map(nums); return n.slice(1).map((c) => Math.round(apcaLc(toneOk(c), toneOk(n[0])) * 10) / 10); };
  const g = generateSpectrum(spectrumOverrides(normalizeSpectrum({ targetsLight: measure('light'), targetsDark: measure('dark') })));
  for (const mode of ['light', 'dark']) for (const [fam, steps] of Object.entries(fx[mode])) {
    const ramp = g.schemes[mode][fam]; if (!ramp) { f.push(`${mode} ${fam}: family missing from the engine`); continue; }
    steps.forEach((s, i) => { const d = dE(nums(s), ramp[i].oklch); if (d > 0.1) f.push(`${mode} ${fam} step ${i + 1}: ΔE ${d.toFixed(3)} > 0.1`); });
  }
  return f;
}
// 2. Placement. The default output's steps that nothing post-solves sit at their APCA target against the page: every family's
// steps 2–7 within 1.5 Lc, accents' step 12 within 2.5 (steps 8–11 are moved by the border solve and the key run).
function checkPlacement(j) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) { if (M.contrastMode) continue; const t = M.scheme === 'light' ? M.settings.targetsLight : M.settings.targetsDark;
    for (const [fam, ramp] of Object.entries(M.ramps)) { const page = toneOk(ramp[0].oklch);
      ramp.forEach((s, i) => { const step = i + 1, accent = j.families.accents.includes(fam); const tol = step <= 7 ? 1.5 : accent && step === 12 ? 2.5 : null; if (step === 1 || tol === null) return;
        const lc = apcaLc(toneOk(s.oklch), page); if (Math.abs(lc - t[step - 2]) > tol) f.push(`${id} ${fam} step ${step}: Lc ${lc.toFixed(1)} vs target ${t[step - 2]} (±${tol})`); }); } }
  return f;
}
// 3. Floors, recomputed from the ramps with APCA (|Lc| from the vendored apcaLc, text first, background second) at the
// thresholds this check derives from the request on its own (defaults solid 45, text 45, hint 30, ui 15, series 30; contrast
// modes +15 unless apca.contrast names its own): every family's solid and its hover against its own label (the light mode's
// gray 1 or gray 12, as solidLabels names it) and the reported Lc; each scale role's <role>-on-solid is that label; control
// border on steps 1–2 ≥ ui; series on the chart surface ≥ series. A 0.05 Lc allowance covers 6-decimal JSON rounding.
const APCA_DEF = { solid: 45, text: 45, hint: 30, ui: 15, series: 30 }, APCA_UP = 15, MARGIN = 0.5;
const thrOf = (j, M) => { const a = (j.resolvedRequest || j.request).apca || {}, n = Object.fromEntries(Object.keys(APCA_DEF).map((k) => [k, a[k] ?? APCA_DEF[k]]));
  return M.contrastMode ? Object.fromEntries(Object.keys(APCA_DEF).map((k) => [k, a.contrast?.[k] ?? Math.min(108, n[k] + APCA_UP)])) : n; };
const lcOk = (fg, bg) => apcaLc(toneOk(fg), toneOk(bg));
// What a Display P3 screen shows: each colour clipped to P3, luminance by P3's own weights. A system with a P3 upgrade is
// solved on the worse of the two renderings, so its floors are recomputed the same way (lcShown).
const linRaw = ([L, C, H]) => { const a = C * Math.cos(H * Math.PI / 180), b = C * Math.sin(H * Math.PI / 180);
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3;
  return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s]; };
const toneP3 = (c) => { const [r, g, b] = linRaw(c), v = [0.8224621 * r + 0.177538 * g, 0.0331941 * r + 0.9668058 * g, 0.0170827 * r + 0.0723974 * g + 0.9105199 * b].map((x) => Math.min(1, Math.max(0, x)));
  const y = 0.2289746 * v[0] + 0.6917385 * v[1] + 0.0792869 * v[2]; return y > 0.008856 ? 116 * Math.cbrt(y) - 16 : 903.3 * y; };
const lcShown = (j) => (j.target === 'display-p3' ? (fg, bg) => Math.min(lcOk(fg, bg), apcaLc(toneP3(fg), toneP3(bg))) : lcOk);
// Bright hues: the window from the request (default 70°–125°, inclusive, from > to wraps; false: none), read here on its own.
const brightOf = (j) => { const b = (j.resolvedRequest || j.request).brightHues; const w = b === false ? null : b ?? [70, 125];
  return (H) => { if (!w) return false; const h = ((H % 360) + 360) % 360; return w[0] <= w[1] ? h >= w[0] && h <= w[1] : h >= w[0] || h <= w[1]; }; };
// With neutrals the light label is the light page (ground 1); the dark label is always the light ink (gray 12 = ink 12).
const splitOf = (j) => (j.resolvedRequest || j.request).neutrals ?? null;
const labelsOf = (j) => ({ light: (splitOf(j) ? j.modes.light.ramps.ground : j.modes.light.ramps.gray)[0].oklch, dark: j.modes.light.ramps.gray[11].oklch });
function checkFloors(j) {
  const lcS = lcShown(j);
  const f = [], labels = labelsOf(j), eps = 0.05, near = (a, b) => a && b && dE(a, b) < 0.05;
  for (const [id, M] of Object.entries(j.modes)) {
    const T = thrOf(j, M); if (JSON.stringify(M.apca) !== JSON.stringify(T)) f.push(`${id}: system.json apca ${JSON.stringify(M.apca)} ≠ ${JSON.stringify(T)} from the request`);
    for (const fam of j.families.all) { const e = M.solidLabels?.[fam]; if (!e || !labels[e.label]) { f.push(`${id} ${fam}: no solid label`); continue; }
      const v = lcS(labels[e.label], M.ramps[fam][8].oklch); if (v < T.solid - eps) f.push(`${id} ${fam} solid Lc ${v.toFixed(2)} < ${T.solid} against its ${e.label} label`);
      if (Math.abs(v - e.lc) > 0.1) f.push(`${id} ${fam}: solidLabels lc ${e.lc}, recomputed ${v.toFixed(2)}`);
      if (Math.abs(v - M.solidLabelContrast?.[fam]) > 0.1) f.push(`${id} ${fam}: solidLabelContrast ${M.solidLabelContrast?.[fam]}, recomputed ${v.toFixed(2)}`);
      const excused = (M.keyRun?.[fam]?.deviations || []).some((d) => d.step === 10 && /unreachable|anchored/.test(d.reason)), h = lcS(labels[e.label], M.ramps[fam][9].oklch);
      if (h < T.solid - eps && !excused) f.push(`${id} ${fam} hover Lc ${h.toFixed(2)} < ${T.solid} against its ${e.label} label`); }
    for (const [role, fam0] of Object.entries(M.roles)) { const v = M.variables['--colors-' + role + '-on-solid']; if (v == null) continue; const fam = fam0 === 'neutral' ? 'gray' : fam0, st = M.solidSteps?.[role] ?? 9, e = M.solidLabels?.[fam], want = st === 9 ? e?.label : (e?.anchored?.[st] ?? e)?.label;
      if (!near(nums(v).length === 3 ? nums(v) : null, labels[want])) f.push(`${id} --colors-${role}-on-solid is ${v}, not the ${want} label of ${fam} ${st}`); }
    const g = M.ramps.gray; if (!splitOf(j)) for (const k of [0, 1]) { const v = lcS(g[7].oklch, g[k].oklch); if (v < T.ui - eps) f.push(`${id} control border on step ${k + 1} Lc ${v.toFixed(2)} < ${T.ui}`); }
    // Neutrals split: the control border is surface 8, on the page (ground 1–2) and on the material (surface 1–2); series sit on bg-subtle (ground 2).
    if (splitOf(j)) for (const [fam, k] of [['ground', 0], ['ground', 1], ['surface', 0], ['surface', 1]]) { const v = lcS(M.ramps.surface[7].oklch, M.ramps[fam][k].oklch); if (v < T.ui - eps) f.push(`${id} control border (surface 8) on ${fam} ${k + 1} Lc ${v.toFixed(2)} < ${T.ui}`); }
    const chart = splitOf(j) ? M.ramps.ground : g;
    for (const [i, s] of (M.series || []).entries()) { const v = lcS(s.oklch, chart[1].oklch); if (v < T.series - eps) f.push(`${id} series ${i + 1} Lc ${v.toFixed(2)} < ${T.series}`); if (Math.abs(v - s.lcOnSurface) > 0.1) f.push(`${id} series ${i + 1}: lcOnSurface ${s.lcOnSurface}, recomputed ${v.toFixed(2)}`); }
  }
  return f;
}
// 3b. White first, kept solids and every later move, re-derived: each mode's ramps regenerated before the solid solve (the
// engine at the mode's settings, keys shaped), independently of system.mjs. With F = solid floor + 0.5 (the solver's margin):
// a generated step 9 with white Lc ≥ F takes the light label — unless keeping white would put step 9 under apca.ui on the page
// (dark schemes: the hover, a third of the way to step 12 in page Lc, must keep white ≥ F; APCA reads tones only, so the
// lightest hover tone and the step 9 it implies, (3·Lc10 − Lc12)/2, are exact), and then it takes the dark label with
// whiteRejected; else one with dark Lc ≥ F takes the dark label; a label it passes keeps it unmoved (moved 0); one that passes
// neither is moved. After the label solve, step 9 changes only for a recorded reason: hoverRoom (minimal: the hover lands
// at F ± 0.3, step 9 nearer the page) or cusp (checkCusp). Runs without anchors only (anchors re-shape ramps before the solve).
const preCache = new Map();
function preSolve(settings) { const k = JSON.stringify(settings); if (!preCache.has(k)) preCache.set(k, shapeKeys(generateSpectrum(spectrumOverrides(normalizeSpectrum(settings))))); return preCache.get(k); }
function checkKeep(j) {
  const lcS = lcShown(j);
  const f = [], labels = labelsOf(j), W = toneOk(labels.light), bright = brightOf(j), neutral = new Set(j.families.neutrals); let kept = 0, moved = 0, rejected = 0, brights = 0;
  for (const [id, M] of Object.entries(j.modes)) { if (M.anchorReport?.length || j.familyNames === 'index') continue; const T = thrOf(j, M), F = T.solid + MARGIN, g = preSolve(M.settings).schemes[M.scheme];
    for (const fam of j.families.all) { const e = M.solidLabels?.[fam], gen = g[fam === 'gray' ? 'neutral' : fam]?.[8]?.oklch, r = M.ramps[fam]; if (!e || !gen) { f.push(`${id} ${fam}: no solid label or generated step`); continue; }
      if (dE(gen, e.generated) > 0.1) { f.push(`${id} ${fam}: recorded generated step 9 is ΔE ${dE(gen, e.generated).toFixed(2)} from the engine's`); continue; }
      const page = toneOk(r[0].oklch), lL = lcS(labels.light, gen), lD = lcS(labels.dark, gen), isBright = !neutral.has(fam) && bright(gen[2]);
      if (isBright !== !!e.brightHue) f.push(`${id} ${fam}: hue ${gen[2].toFixed(1)}° is ${isBright ? '' : 'not '}in the bright-hue window, but brightHue is ${!!e.brightHue}`);
      if (isBright) { brights++; if (e.label !== 'dark') f.push(`${id} ${fam}: bright hue (${gen[2].toFixed(1)}°) on the ${e.label} label`); if ((lD >= F) !== (e.moved === 0) && Math.abs(lD - F) >= 0.2) f.push(`${id} ${fam}: bright hue ${e.moved === 0 ? 'kept although it fails' : 'moved although it passes'} the dark label (${lD.toFixed(1)})`); continue; }
      if (Math.abs(lL - F) < 0.2 || Math.abs(lD - F) < 0.2) continue; // too close to call
      // The white run: step 9 where white keeps F (the generated solid, or the tone where white just reaches F), and in a dark
      // scheme no further from the page than its hover allows. tF: the lightest tone white still reaches F on.
      let lo = 0, hi = 100; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (apcaLc(W, m) >= F) lo = m; else hi = m; }
      let lc9 = lL >= F ? apcaLc(toneOk(gen), page) : apcaLc(lo, page);
      if (M.scheme === 'dark') lc9 = Math.min(lc9, (3 * apcaLc(lo, page) - apcaLc(toneOk(r[11].oklch), page)) / 2);
      if (Math.abs(lc9 - T.ui) < 0.3) continue;
      const whiteOut = lc9 < T.ui, want = lL >= F ? (whiteOut ? 'dark' : 'light') : lD >= F ? 'dark' : null;
      if (want && e.label !== want) f.push(`${id} ${fam}: takes the ${e.label} label; white first wants ${want} (generated white Lc ${lL.toFixed(1)}, dark ${lD.toFixed(1)}; white-run step 9 at page Lc ${lc9.toFixed(1)})`);
      if (e.whiteRejected && !whiteOut) f.push(`${id} ${fam}: whiteRejected, but the white run keeps step 9 at page Lc ${lc9.toFixed(1)} ≥ ui ${T.ui}`);
      if (lL >= F && whiteOut && !e.whiteRejected) f.push(`${id} ${fam}: the white run puts step 9 at page Lc ${lc9.toFixed(1)} < ui ${T.ui}, but whiteRejected is not recorded`);
      if (e.label === 'light' && whiteOut) f.push(`${id} ${fam}: light label although its white run puts step 9 at page Lc ${lc9.toFixed(1)} < ui ${T.ui}`);
      if (e.whiteRejected) rejected++;
      const passes = (e.label === 'light' && lL >= F) || (e.label === 'dark' && lD >= F);
      if (passes) { kept++; if (e.moved !== 0) f.push(`${id} ${fam}: generated solid passes its ${e.label} label but the label solve moved it (ΔL ${e.moved})`); }
      else { moved++; if (e.moved === 0) f.push(`${id} ${fam}: generated solid fails its ${e.label} label (${(e.label === 'light' ? lL : lD).toFixed(1)}) but was kept`); }
      const fin = r[8].oklch;
      if (!e.hoverRoom && !e.cusp && e.moved === 0 && dE(fin, gen) > 0.05) f.push(`${id} ${fam}: step 9 moved ΔE ${dE(fin, gen).toFixed(2)} from the generated solid with no recorded reason`);
      if (e.hoverRoom) { const h = lcS(labels[e.label], r[9].oklch); if (Math.abs(h - F) > 0.3) f.push(`${id} ${fam}: hover room is not minimal (hover Lc ${h.toFixed(2)}, floor ${F})`);
        if (e.moved === 0 && !e.cusp && apcaLc(toneOk(fin), page) >= apcaLc(toneOk(gen), page)) f.push(`${id} ${fam}: hover room moved step 9 away from the page`); } } }
  if (!kept || !moved) f.push(`no ${!kept ? 'kept' : 'moved'} solid to check (kept ${kept}, moved ${moved}, white rejected ${rejected}, bright ${brights})`);
  return f;
}
// 3c. Cusp: a dark-label accent solid that is not anchored sits at its hue's gamut cusp (the lightness of greatest in-gamut
// chroma at the generated hue, capped at L 0.95, found here by its own scan) with the full chroma there, whenever that is
// brighter than where the label solve left it — lowered only as far as keeping apca.ui on the page needs; no hue rotation.
// Light-label solids never carry the cusp mark.
function cuspL(H, gamut) { let best = 0, bL = 0; for (let L = 0.3; L <= 1; L += 0.001) { const c = clampChroma(L, 0.5, H, gamut); if (c > best) { best = c; bL = L; } } return Math.min(bL, 0.95); }
function checkCusp(j) {
  const lcS = lcShown(j);
  const f = [], neutral = new Set(j.families.neutrals); let n = 0;
  for (const [id, M] of Object.entries(j.modes)) { const T = thrOf(j, M), gamut = M.settings.target, pinned9 = new Set(M.anchorReport.filter((a) => (M.scheme === 'light' ? a.step : a.dark?.step) === 9).map((a) => (a.family === 'neutral' ? 'gray' : a.family)));
    for (const fam of j.families.accents) { const e = M.solidLabels?.[fam], r = M.ramps[fam]; if (!e) continue;
      if (e.label !== 'dark' || neutral.has(fam) || pinned9.has(fam)) { if (e.cusp) f.push(`${id} ${fam}: cusp on a ${e.label}-label or anchored solid`); continue; }
      if (e.hoverRoom) continue;
      const H = e.generated[2], cl = cuspL(H, gamut), floorL = e.generated[0] + e.moved, fin = r[8].oklch;
      if (cl > floorL + 0.003) { n++;
        if (!e.cusp) { f.push(`${id} ${fam}: dark-label solid at L ${fin[0].toFixed(3)}, its cusp is brighter (L ${cl.toFixed(3)})`); continue; }
        if (fin[0] > cl + 0.003) f.push(`${id} ${fam}: step 9 L ${fin[0].toFixed(3)} above the cusp ${cl.toFixed(3)}`);
        // Below the cusp only as far as the page needs (apca.ui) or the key run needs (15 Lc short of step 12 on the page).
        const p9 = lcS(fin, r[0].oklch), room = lcS(r[11].oklch, r[0].oklch) - 15;
        if (fin[0] < cl - 0.003 && Math.abs(p9 - (T.ui + MARGIN)) > 0.3 && Math.abs(p9 - room) > 0.3) f.push(`${id} ${fam}: step 9 L ${fin[0].toFixed(3)} below the cusp ${cl.toFixed(3)} without the page or the key run needing it`);
        if (p9 > room + 0.3) f.push(`${id} ${fam}: step 9 at page Lc ${p9.toFixed(1)} leaves the key run under 15 Lc to step 12`);
        if (fin[1] < clampChroma(fin[0], 0.5, H, gamut) - 0.002) f.push(`${id} ${fam}: step 9 chroma ${fin[1].toFixed(3)} under the gamut maximum there`);
        if (Math.abs((((fin[2] - H) % 360) + 540) % 360 - 180) > 0.05) f.push(`${id} ${fam}: step 9 hue ${fin[2]} rotated from ${H}`);
      } else if (e.cusp && Math.abs(cl - floorL) > 0.003) f.push(`${id} ${fam}: cusp recorded, but the cusp (L ${cl.toFixed(3)}) is not brighter than ${floorL.toFixed(3)}`); } }
  return { f, n };
}
// 3d. Key run 9–12, recomputed from the ramps: page Lc of each step equals keyRun.lc (±0.1); between fixed points (9, 12,
// anchored 10–12 from the anchor report, and each recorded deviation) every step sits at the even interpolation of page Lc
// within ±0.5 Lc — the solver bisects lightness to ~1e-9 and this check uses the same tone maths, so the only slack is JSON's
// 6-decimal rounding (< 0.01 Lc); 0.5 is a third of the 1.5 Lc of a just-visible step. OKLCH lightness is monotonic 9→12 in
// the ramp's direction; steps 11 and 12 clear apca.text on the page and on step 3. Every deviation is checked to be real and to hold at
// its own floor.
const KEYRUN_TOL = 0.5;
function checkKeyRun(j) {
  const lcS = lcShown(j);
  const f = [], labels = labelsOf(j); let worst = 0;
  for (const [id, M] of Object.entries(j.modes)) { const T = thrOf(j, M), F = T.solid + MARGIN;
    for (const fam of j.families.all) { const r = M.ramps[fam], kr = M.keyRun?.[fam], e = M.solidLabels?.[fam]; if (!kr || !e) { f.push(`${id} ${fam}: keyRun missing`); continue; }
      const page = toneOk(r[0].oklch), L = [8, 9, 10, 11].map((i) => apcaLc(toneOk(r[i].oklch), page)), at = (st) => L[st - 9], dir = toneOk(r[11].oklch) < page ? -1 : 1;
      kr.lc.forEach((v, i) => { if (Math.abs(v - L[i]) > 0.1) f.push(`${id} ${fam} step ${9 + i}: keyRun lc ${v}, recomputed ${L[i].toFixed(2)}`); });
      const anch = M.anchorReport.filter((a) => (a.family === 'neutral' ? 'gray' : a.family) === fam).map((a) => (M.scheme === 'light' ? a.step : a.dark?.step)).filter((st) => st >= 10 && st <= 12);
      const steps = [...new Set([9, 12, ...anch, ...kr.deviations.map((d) => d.step)])].sort((a, b) => a - b);
      for (let k = 0; k + 1 < steps.length; k++) { const a = steps[k], b = steps[k + 1]; for (let st = a + 1; st < b; st++) { const want = at(a) + (at(b) - at(a)) * (st - a) / (b - a), d = Math.abs(at(st) - want); worst = Math.max(worst, d); if (d > KEYRUN_TOL) f.push(`${id} ${fam} step ${st}: Lc ${at(st).toFixed(2)}, even spacing wants ${want.toFixed(2)} (±${KEYRUN_TOL})`); } }
      for (let st = 9; st < 12; st++) if ((r[st].oklch[0] - r[st - 1].oklch[0]) * dir <= 0 && !kr.deviations.some((d) => d.reason === 'order')) f.push(`${id} ${fam}: lightness reverses between steps ${st} and ${st + 1}`);
      const onS3 = (st) => Math.min(at(st), lcS(r[st - 1].oklch, r[2].oklch));
      for (const st of [11, 12]) if (onS3(st) < T.text - 0.05) f.push(`${id} ${fam} step ${st}: Lc ${onS3(st).toFixed(2)} on the page or step 3 < text ${T.text}`);
      for (const d of kr.deviations) { const even10 = at(9) + (at(12) - at(9)) / 3, h = lcS(labels[e.label], r[9].oklch);
        if (d.reason === 'hover-floor' && (Math.abs(h - F) > 0.3 || Math.abs(at(10) - even10) <= KEYRUN_TOL)) f.push(`${id} ${fam}: hover-floor deviation, but step 10 is ${Math.abs(h - F) > 0.3 ? 'not at the floor' : 'evenly spaced'}`);
        if (d.reason === 'text-floor' && Math.abs(onS3(d.step) - (T.text + MARGIN)) > 0.3) f.push(`${id} ${fam}: text-floor deviation, but step ${d.step} is not at the text floor`);
        if (/unreachable|anchored-hover/.test(d.reason) && lcS(labels[(e.anchored?.[d.step - 1] ?? e).label], r[d.step - 1].oklch) >= T.solid) f.push(`${id} ${fam}: ${d.reason} at step ${d.step}, but it clears the floor`); } } }
  return { f, worst };
}
// 4. Files.
const checkFiles = (dir, names) => names.filter((n) => !existsSync(join(dir, n))).map((n) => 'missing ' + n);
// 5. CSS parses: balanced braces outside comments, every declaration ends with ';', every var() without a fallback is declared.
function checkCss(text, label = 'css') {
  const f = [], body = text.replace(/\/\*[\s\S]*?\*\//g, '');
  let depth = 0; for (const ch of body) { if (ch === '{') depth++; else if (ch === '}') { depth--; if (depth < 0) { f.push(label + ': unbalanced }'); depth = 0; } } }
  if (depth) f.push(`${label}: ${depth} unclosed {`);
  const declared = new Set([...body.matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1]));
  const used = new Set([...body.matchAll(/var\((--[\w-]+)\s*\)/g)].map((m) => m[1]));
  for (const v of used) if (!declared.has(v)) f.push(`${label}: var(${v}) used but never declared`);
  body.split('\n').forEach((line, i) => { if (/^\s+[\w-]+\s*:/.test(line) && !/;\s*$/.test(line)) f.push(`${label} line ${i + 1}: declaration without ;`); if (/:\s*;/.test(line)) f.push(`${label} line ${i + 1}: empty value`); });
  return f;
}
// 6. Light-dark with extra modes: the root block is `light dark`, forced light/dark set their scheme, every extra mode's
// blocks set its own scheme, and the P3 upgrade re-declares every variable whose light or dark value leaves sRGB.
function blocksOf(text) { const out = []; const re = /([^{}]+)\{([^{}]*)\}/g; let m; while ((m = re.exec(text))) out.push({ sel: m[1].trim().split('\n').pop().trim(), body: m[2], at: m.index }); return out; }
function checkLightDark(css, j) {
  const f = [], p3At = css.indexOf('@media (color-gamut: p3)'), srgb = p3At < 0 ? css : css.slice(0, p3At), p3 = p3At < 0 ? '' : css.slice(p3At);
  const scheme = (b) => (/color-scheme:\s*([^;]+);/.exec(b.body) || [])[1];
  const bs = blocksOf(srgb), root = bs.find((b) => b.sel === ':where(:root)' && /light-dark\(/.test(b.body));
  if (!root) f.push('no :where(:root) block with light-dark() values'); else if (scheme(root) !== 'light dark') f.push(`root color-scheme is "${scheme(root)}", not "light dark"`);
  for (const [sel, want] of [['.light', 'light'], ['.dark', 'dark']]) { const b = bs.find((x) => x.sel === sel); if (!b) f.push('no forced ' + sel + ' block'); else if (scheme(b) !== want) f.push(`${sel} color-scheme "${scheme(b)}" ≠ ${want}`); }
  for (const [id, M] of Object.entries(j.modes)) { if (id === 'light' || id === 'dark') continue;
    const sel = id.endsWith('-contrast') ? `.${id.replace(/-contrast$/, '')}.contrast-more` : '.' + id, mine = bs.filter((b) => b.sel === sel || (M.contrastMode && b.sel.startsWith(':where(:root):not(') && new RegExp(`prefers-color-scheme: ${M.scheme}\\) and \\(prefers-contrast`).test(srgb.slice(Math.max(0, b.at - 80), b.at + 1))));
    if (!mine.length) f.push(`mode ${id}: no override block`);
    for (const b of mine) if (scheme(b) !== M.scheme) f.push(`mode ${id} (${b.sel}): color-scheme "${scheme(b)}" ≠ ${M.scheme}`); }
  if (p3At >= 0) { const p3root = blocksOf(p3).find((b) => b.sel === ':where(:root)' && /light-dark\(/.test(b.body)); const have = new Set(p3root ? [...p3root.body.matchAll(/(--[\w-]+):/g)].map((m) => m[1]) : []);
    const leaves = (v) => [...String(v).matchAll(/oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)/g)].some((m) => clampChroma(+m[1], +m[2], +m[3], 'srgb') < +m[2] - 1e-6);
    for (const k of Object.keys(j.modes.light.variables)) if ((leaves(j.modes.light.variables[k]) || leaves(j.modes.dark.variables[k])) && !have.has(k)) f.push(`P3 light-dark block lacks ${k}`); }
  return f;
}
// 7. Split files declare everything system.css declares, and parse as one stylesheet in load order.
function checkSplit(dir, j) {
  const f = [], files = ['system.base.css', ...Object.keys(j.modes).filter((id) => !(j.request.lightDark && (id === 'light' || id === 'dark'))).map((id) => `system.${id}.css`)];
  f.push(...checkFiles(dir, files)); if (f.length) return f;
  const all = files.map((n) => readFileSync(join(dir, n), 'utf8')).join('\n'), whole = readFileSync(join(dir, 'system.css'), 'utf8');
  const decl = (t) => new Set([...t.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1]));
  const a = decl(all); for (const k of decl(whole)) if (!a.has(k)) f.push('split files never declare ' + k);
  f.push(...checkCss(all, 'split'));
  // Each mode file re-declares every variable that resolves through var() (a shared value is only ever a literal).
  for (const id of Object.keys(j.modes)) { const n = `system.${id}.css`; if (!files.includes(n)) continue; const d = decl(readFileSync(join(dir, n), 'utf8'));
    for (const [k, v] of Object.entries(j.modes[id].variables)) if (/var\(/.test(v) && !d.has(k)) f.push(`${n} lacks ${k}, which resolves per mode`); }
  return f;
}
// 8. Figma: every alias points at a variable in the file, and resolves to the same colour as the alias's own resolved value.
function checkFigma(fg) {
  const f = [], byId = new Map(); for (const c of fg.collections) for (const v of c.variables) byId.set(v.id, { v, c });
  let aliases = 0;
  for (const c of fg.collections) for (const v of c.variables) for (const mode of c.modes) {
    const val = v.valuesByMode[mode], res = v.resolvedValuesByMode?.[mode]; if (!res) { f.push(`${v.name} [${mode}]: no resolved value`); continue; }
    if (val?.type !== 'VARIABLE_ALIAS') continue; aliases++;
    const t = byId.get(val.id); if (!t) { f.push(`${v.name} [${mode}]: alias to unknown id ${val.id}`); continue; }
    const tr = t.v.resolvedValuesByMode[t.c.modes.includes(mode) ? mode : t.c.modes[0]];
    if (['r', 'g', 'b', 'a'].some((k) => Math.abs(tr[k] - res[k]) > 1e-4)) f.push(`${v.name} [${mode}]: alias ${val.id} resolves to a different colour`);
  }
  if (!aliases) f.push('no VARIABLE_ALIAS values at all');
  return f;
}
// 9. Contrast matrix, recomputed for every pair whose two sides are opaque ramp steps (var() chains into modes.<id>.ramps):
// |Lc| (foreground as text) within 0.1, the threshold of its intent from the request (label → solid), pass = Lc ≥ threshold;
// the informational WCAG ratio within 0.02.
function checkContrast(j) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) {
    const c = M.contrast, T = thrOf(j, M); if (!c || !Array.isArray(c.pairs) || c.pairs.length < 40) { f.push(`${id}: contrast matrix missing or short`); continue; }
    const ramp = (k) => { const m = /^--colors-([\w-]+)-(\d+)$/.exec(k); return m && M.ramps[m[1]] ? M.ramps[m[1]][+m[2] - 1]?.oklch : null; };
    const resolve = (k, d = 0) => { const v = M.variables[k]; if (v == null || d > 5) return null; const m = /^var\((--[\w-]+)\)$/.exec(v); if (m) return resolve(m[1], d + 1); const lit = /^oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)$/.exec(v); return ramp(k) || (lit ? [+lit[1], +lit[2], +lit[3]] : /^#fff$/i.test(v) ? [1, 0, 0] : /^#000$/i.test(v) ? [0, 0, 0] : null); };
    let checked = 0;
    for (const p of c.pairs) { const need = p.intent === 'label' ? T.solid : T[p.intent]; if (p.threshold !== need) f.push(`${id} ${p.fg} on ${p.bg}: threshold ${p.threshold}, ${p.intent} needs ${need}`);
      if (p.pass !== p.lc >= p.threshold) f.push(`${id} ${p.fg} on ${p.bg}: pass ${p.pass} but Lc ${p.lc} vs ${p.threshold}`);
      const a = resolve('--colors-' + p.fg), b = resolve('--colors-' + p.bg); if (!a || !b) continue; checked++;
      const v = lcOk(a, b); if (Math.abs(v - p.lc) > 0.1) f.push(`${id} ${p.fg} on ${p.bg}: reported Lc ${p.lc}, recomputed ${v.toFixed(2)}`);
      if ((v >= need) !== p.pass && Math.abs(v - need) > 0.05) f.push(`${id} ${p.fg} on ${p.bg}: pass ${p.pass} but recomputed Lc ${v.toFixed(2)} vs ${need}`);
      const r = ratioOk(a, b); if (Math.abs(r - p.ratio) > 0.02) f.push(`${id} ${p.fg} on ${p.bg}: informational ratio ${p.ratio}, recomputed ${r.toFixed(2)}`); }
    if (checked < 30) f.push(`${id}: only ${checked} pairs could be recomputed`);
    if (c.summary.fail !== c.pairs.filter((p) => !p.pass).length) f.push(`${id}: summary.fail disagrees with the pairs`);
    // A system with a Display P3 upgrade measures every pair on the P3 values as well; one without carries no P3 field.
    const wide = j.target === 'display-p3';
    for (const p of c.pairs) { if (wide ? !(typeof p.lcP3 === 'number' && p.passP3 === (p.lcP3 >= p.threshold)) : 'lcP3' in p) f.push(`${id} ${p.fg} on ${p.bg}: Display P3 measurement ${wide ? 'missing or inconsistent' : 'present in an sRGB system'}`);
      // The two measurements may differ only where a colour lies outside sRGB.
      if (wide && Math.abs(p.lcP3 - p.lc) > 6) f.push(`${id} ${p.fg} on ${p.bg}: Lc ${p.lc} on sRGB and ${p.lcP3} on Display P3 differ by more than clipping can explain`); }
    if (wide && c.summary.failP3 !== c.pairs.filter((p) => !p.passP3).length) f.push(`${id}: summary.failP3 disagrees with the pairs`);
  }
  return f;
}
// 9b. The apca and brightHues request keys: each bad value exits 2 (and nothing else does).
const BAD_REQUESTS = [{ solid: 'x' }, { solid: -1 }, { text: 109 }, { tint: 30 }, { contrast: 5 }, { contrast: { hint: 200 } }, [], { contrast: { foo: 1 } }].map((apca) => ({ apca }))
  .concat([true, [70], [70, 'x'], [-5, 120], [70, 400], { from: 70, to: 125 }].map((brightHues) => ({ brightHues })))
  .concat([3, -0.5, 'loud', true].map((emphasis) => ({ emphasis })));
// Brand colours (system.md › Brand colours): generic page, card, text, dark-section, accent and low-chroma label colours.
// With brandExact every accent anchor is the step-9 solid in every mode; autoDark false writes no prefers-color-scheme block;
// series false writes no data role. Without brandExact (and without dark), an anchored family still never takes the cusp, and
// the low-chroma label family is never a bright hue.
const BRAND_ACCENTS = [{ role: 'primary', value: '#c8962a' }, { role: 'secondary', value: '#7d6f57' }];
const BRAND = { preset: 'minimal', familyNames: { indigo: 'mark' }, series: false, autoDark: false, brandExact: true, extraModes: [{ id: 'on-dark', scheme: 'dark' }], neutrals: { ground: { tint: 30 }, surface: { tint: 30 }, ink: { tint: 30 } },
  anchors: [{ role: 'ground', value: '#f4f1ea' }, { role: 'ink', value: '#221d18', dark: '#121010' }, { role: 'surface', value: '#ebe5dc' }, ...BRAND_ACCENTS] };
const BAD_BRAND = [{ roles: { primary: 'foo' } }, { roles: { primary: 'h400' } }, { roles: { primary: 'oklch:x' } }, { anchors: [{ role: 'ink', value: '#221d18', step: 11 }] }, { anchors: [{ role: 'primary', value: '#c8962a', step: 'nine' }] }, { autoDark: 'no' }, { autoDark: false, lightDark: true }, { familyNames: { foo: 'bar' } }, { familyNames: { amber: 'cyan' } }, { familyNames: { amber: 'ink' } }, { familyNames: { amber: 'x', orange: 'x' } }];
function checkBrand(j, css, jLoose) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) for (const a of BRAND_ACCENTS) {
    const x = M.anchorReport.find((r) => r.role === a.role); if (!x) { f.push(`${id}: no anchorReport entry for ${a.role}`); continue; }
    const got = M.ramps[x.family]?.[8]?.oklch; if (!got) { f.push(`${id}: no ${x.family} ramp`); continue; }
    const d = dE(hexOk(a.value), got); if (d > 0.5) f.push(`${id}: ${a.role} anchor ${a.value} is not the ${x.family} step 9 (ΔE ${d.toFixed(2)})`);
  }
  if (/prefers-color-scheme/.test(css)) f.push('autoDark false: system.css has a prefers-color-scheme block');
  if (/--colors-data-\d/.test(css)) f.push('series false: system.css has a --colors-data-N variable');
  if (!/--colors-mark-9:/.test(css) || /--colors-indigo-/.test(css) || j.modes.light.roles.primary !== 'mark') f.push('familyNames { indigo: mark }: the family is not emitted as mark, or indigo is still emitted');
  for (const [id, M] of Object.entries(jLoose.modes)) for (const x of M.anchorReport.filter((r) => BRAND_ACCENTS.some((a) => a.role === r.role))) {
    const e = M.solidLabels[x.family]; if (e?.cusp) f.push(`${id}: anchored ${x.family} solid at its cusp`); if (e?.brightHue) f.push(`${id}: anchored ${x.family} marked bright`);
  }
  return f;
}
// Family anchors: pin families by name (no role), exact at their step 9 in every scheme, the roles untouched, no internal
// family: role in any output; and role names outside the system's own exit 2 instead of being dropped.
const FAMILY_ANCHORS = { orange: { value: '#f76b15', dark: '#f76b15' }, teal: { value: '#12a594' } };
const FAMILY_REQ = { extraModes: false, tonal: false, alpha: false, series: false, dtcg: false, settings: { hueSet: 'radix' }, familyAnchors: FAMILY_ANCHORS, brandExact: true };
const BAD_FAMILY = [{ roles: { 'pin-orange': 'orange' } }, { anchors: [{ role: 'pin-orange', value: '#f76b15' }] }, { modes: { dark: { roles: { accent: 'orange' } } } },
  { familyAnchors: [] }, { familyAnchors: { orange: { value: '#f76b15', role: 'primary' } } }, { familyAnchors: { Orange: { value: '#f76b15' } } },
  { settings: { hueSet: 'radix' }, familyAnchors: { tealish: { value: '#12a594' } } }, { settings: { hueSet: 'radix' }, familyAnchors: { indigo: { value: '#3e63dd' } }, anchors: [{ role: 'primary', value: '#3e63dd' }] },
  { familyAnchors: { orange: { value: '#f76b15', step: 13 } } }];
// hoverMin: with the key set, every family's step 9 to step 10 (the solid to its hover) is at least hoverMin OKLab ΔE × 100 in
// every mode, recomputed from the ramps. Runs: the Radix hue set alone, and with every accent's Radix step 9 pinned (familyAnchors).
const RADIX_STEP9 = { gold: '#978365', bronze: '#a18072', brown: '#ad7f58', yellow: '#ffe629', amber: '#ffc53d', orange: '#f76b15', tomato: '#e54d2e', red: '#e5484d', ruby: '#e54666', crimson: '#e93d82', pink: '#d6409f', plum: '#ab4aba', purple: '#8e4ec6',
  violet: '#6e56cf', iris: '#5b5bd6', indigo: '#3e63dd', blue: '#0090ff', cyan: '#00a2c7', teal: '#12a594', jade: '#29a383', green: '#30a46c', grass: '#46a758', lime: '#bdee63', mint: '#86ead4', sky: '#7ce2fe' };
const HOVER_MIN_REQ = { settings: { hueSet: 'radix' }, hoverMin: 4 }, HOVER_MIN_FA = { ...HOVER_MIN_REQ, familyAnchors: Object.fromEntries(Object.entries(RADIX_STEP9).map(([f, value]) => [f, { value }])) };
const BAD_HOVER_MIN = [{ hoverMin: -1 }, { hoverMin: '4' }, { hoverMin: true }, { hoverMin: null }, { hoverMin: 101 }];
function checkHoverMin(j, min) {
  const f = []; let n = 0;
  for (const [id, M] of Object.entries(j.modes)) for (const [fam, r] of Object.entries(M.ramps)) { n++; const d = dE(r[8].oklch, r[9].oklch); if (!(d >= min)) f.push(`${id} ${fam}: step 9 to 10 ΔE ${d.toFixed(2)} < hoverMin ${min}`); }
  if (n < 30) f.push(`only ${n} family ramps checked`);
  return f;
}
function checkFamilyAnchors(j, css) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) {
    if (Object.keys(M.roles).some((r) => r.startsWith('family:'))) f.push(`${id}: an internal family: role leaked into roles`);
    for (const [fam, a] of Object.entries(FAMILY_ANCHORS)) {
      const x = M.anchorReport.find((r) => r.role === 'family:' + fam); if (!x) { f.push(`${id}: no anchorReport entry for family ${fam}`); continue; }
      if (x.family !== fam) f.push(`${id}: family anchor ${fam} landed on ${x.family}`);
      const want = M.scheme === 'dark' ? a.dark ?? a.value : a.value, got = M.ramps[fam]?.[8]?.oklch; // brandExact: the light value is the dark one too
      if (!got) { f.push(`${id}: no ${fam} ramp`); continue; }
      const d = dE(hexOk(want), got); if (d > 0.5) f.push(`${id}: ${fam} anchor ${want} is not ${fam} step 9 (ΔE ${d.toFixed(2)})`);
    }
    if (M.roles.primary !== 'indigo' || M.roles.info !== 'cyan') f.push(`${id}: family anchors moved a role (primary ${M.roles.primary}, info ${M.roles.info})`);
  }
  if (/family:/.test(css)) f.push('system.css carries an internal family: name');
  return f;
}
// P3 anchors: family anchors with "p3": "edge" (target display-p3) keep their OKLCH lightness and hue; a saturated one (chroma at
// least P3_MUTED_CK of the sRGB maximum there) is lifted to the larger of its chroma and P3_EDGE_CK of the P3 maximum, so it lies
// outside sRGB; a muted one is scaled by P3 max / sRGB max. anchorReport records the requested and the lifted value. Constants restated.
const P3_MUTED_CK = 0.7, P3_EDGE_CK = 0.95;
const P3_ANCHORS = { orange: { value: '#f76b15' }, red: { value: '#e5484d' }, blue: { value: '#0090ff' }, gold: { value: '#978365' } };
const P3_REQ = { ...FAMILY_REQ, familyAnchors: P3_ANCHORS, p3: 'edge' };
const BAD_P3 = [{ p3: 'bogus' }, { p3: true }, { anchors: [{ role: 'primary', value: '#0a4dff', p3: 'bogus' }] }, { settings: { hueSet: 'radix' }, familyAnchors: { orange: { value: '#f76b15', p3: 'wide' } } }];
const hueOff = (a, b) => Math.abs((((a - b) % 360) + 540) % 360 - 180);
function checkP3Anchors(j) {
  const f = [], kinds = new Set();
  for (const [id, M] of Object.entries(j.modes)) for (const [fam, a] of Object.entries(P3_ANCHORS)) {
    const [L, C, H] = hexOk(a.value), s = clampChroma(L, 0.5, H, 'srgb'), p = clampChroma(L, 0.5, H, 'display-p3'), sat = C / s >= P3_MUTED_CK, got = M.ramps[fam]?.[8]?.oklch;
    kinds.add(sat ? 'saturated' : 'muted');
    if (!got) { f.push(`${id}: no ${fam} ramp`); continue; }
    if (Math.abs(got[0] - L) > 0.001 || hueOff(got[2], H) > 0.1) f.push(`${id}: ${fam} 9 moved off the anchor's lightness or hue (L ${got[0]} vs ${L.toFixed(4)}, H ${got[2]} vs ${H.toFixed(2)})`);
    const want = Math.min(p, sat ? Math.max(C, P3_EDGE_CK * p) : C * p / s);
    if (Math.abs(got[1] - want) > 0.001) f.push(`${id}: ${fam} 9 chroma ${got[1]}, want ${want.toFixed(4)} (${sat ? 'saturated' : 'muted'})`);
    if (sat && clampChroma(got[0], got[1], got[2], 'srgb') > got[1] - 0.0001) f.push(`${id}: saturated ${fam} 9 lies inside sRGB`);
    const x = M.anchorReport.find((r) => r.role === 'family:' + fam), g = M.scheme === 'dark' ? x?.dark?.gamut : x?.gamut;
    if (g?.p3?.option !== 'edge') { f.push(`${id}: anchorReport has no p3 record for ${fam}`); continue; }
    if (dE(g.p3.requested, [L, C, H]) > 0.05 || dE(g.p3.lifted, got) > 0.05) f.push(`${id}: ${fam} anchorReport p3 requested/lifted is not the request / the step 9`);
  }
  if (kinds.size < 2) f.push('the run needs a saturated and a muted anchor');
  return f;
}
// P3 usage: each mode's p3Usage recounted from the ramps (swatches whose sRGB mapping moves them by ΔE 0.01 or more; visibly over
// 2; max and median over those outside); the CLI warning names exactly the modes under 5% outside sRGB (a low-chroma run has
// them); no p3Usage without a p3 key.
const P3_LOW = { extraModes: false, tonal: false, alpha: false, series: false, dtcg: false, settings: { keyIntensity: 60, base: 50 } };
function usageCount(M) {
  const ds = []; let n = 0;
  for (const r of Object.values(M.ramps)) for (const x of r) { n++; const [L, C, H] = x.oklch, d = 100 * (C - clampChroma(L, C, H, 'srgb')); if (d >= 0.01) ds.push(d); }
  ds.sort((a, b) => a - b); const vis = ds.filter((d) => d > 2).length;
  return { swatches: n, outsideSrgb: ds.length, share: 100 * ds.length / n, visible: vis, maxDE: ds.at(-1) ?? 0, medianDE: ds.length ? (ds[(ds.length - 1) >> 1] + ds[ds.length >> 1]) / 2 : 0 };
}
function checkP3Usage(j, line, reported) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) {
    const u = reported ? reported[id] : M.p3Usage, c = usageCount(M); if (!u) { f.push(`${id}: no P3 usage report`); continue; }
    for (const k of ['swatches', 'outsideSrgb', 'visible']) if (u[k] !== c[k]) f.push(`${id}: P3 usage ${k} ${u[k]}, the ramps give ${c[k]}`);
    for (const k of ['maxDE', 'medianDE']) if (Math.abs(u[k] - c[k]) > 0.01) f.push(`${id}: P3 usage ${k} ${u[k]}, the ramps give ${c[k].toFixed(2)}`);
  }
  if (line != null) { const want = Object.entries(j.modes).filter(([, M]) => usageCount(M).share < 5).map(([id]) => id).join(', '), got = /^WARNING effectively sRGB.*\[([^\]]*)\]$/m.exec(line)?.[1] ?? '';
    if (got !== want) f.push(`CLI warns effectively sRGB in [${got}], the ramps give [${want}]`); }
  return f;
}
const checkNoP3Usage = (j) => Object.entries(j.modes).filter(([, M]) => M.p3Usage).map(([id]) => `${id}: p3Usage without a p3 key`);
// families.mjs --from-p3: colors-p3/ step 9 from the P3 run (checkFamilyFiles), colors/ step 9 the sRGB run's mapped into sRGB,
// the P3 request and its usage in the manifest.
function checkFromP3(root, jS, jP) {
  const f = [], v = familyVars(join(root, 'colors')), man = readJson(join(root, 'manifest.json'));
  for (const fam of jS.families.all) for (const mode of ['light', 'dark']) {
    const got = v[`--colors-${fam}-9-${mode}`] ?? v[`--colors-${fam}-9`], [L, C, H] = jS.modes[mode].ramps[fam][8].oklch;
    if (!got) { f.push(`colors/: ${fam} 9 missing in ${mode}`); continue; }
    const e = dE(nums(got), [L, clampChroma(L, C, H, 'srgb'), H]); if (e > 0.05) f.push(`colors/: ${fam} 9 in ${mode} is ΔE ${e.toFixed(2)} from the sRGB run`);
  }
  if (JSON.stringify(man.generator?.p3Request) !== JSON.stringify(jP.request)) f.push('manifest.generator.p3Request is not the P3 run\'s request');
  f.push(...checkP3Usage(jP, null, man.p3Usage).map((x) => 'manifest: ' + x));
  return f;
}
// Family files (families.mjs): every variable of every folder resolves to a colour in both schemes through light-dark() and var(),
// with no missing reference; each family file is exact to the system's value; the manifest lists every file with its hash.
function familyVars(dir) { const v = {}; for (const f of readdirSync(dir).filter((x) => x.endsWith('.css') && x !== 'index.css')) for (const m of readFileSync(join(dir, f), 'utf8').matchAll(/^\s+(--[\w-]+): (.+);$/gm)) v[m[1]] = m[2]; return v; }
function checkFamilyFiles(root, j, vars) {
  const f = [], folders = j.target === 'display-p3' ? ['colors-p3', 'colors'] : ['colors'];
  for (const d of folders) { const v = vars?.[d] ?? familyVars(join(root, d)); let n = 0;
    const res = (x, mode, depth = 0) => { if (depth > 20) throw new Error('loop'); x = x.replace(/^light-dark\(var\((--[\w-]+)\), var\((--[\w-]+)\)\)$/, (_, a, b) => `var(${mode === 'light' ? a : b})`);
      const m = x.match(/^var\((--[\w-]+)\)$/); if (m) { if (!(m[1] in v)) throw new Error('missing ' + m[1]); return res(v[m[1]], mode, depth + 1); } return x; };
    for (const k of Object.keys(v)) for (const mode of ['light', 'dark']) { n++; try { const c = res(v[k], mode); if (!/^(oklch\(|color\(|#|transparent|rgba?\()/.test(c) && !/^\d/.test(c)) f.push(`${d}: ${k} in ${mode} resolves to ${c}`); } catch (e) { f.push(`${d}: ${k} in ${mode}: ${e.message}`); } }
    if (!n) f.push(`${d}: no variables`);
    if (d === 'colors-p3') for (const fam of j.families.all) for (const [mode, M] of Object.entries({ light: j.modes.light, dark: j.modes.dark })) {
      const want = M.variables[`--colors-${fam}-9`], got = (() => { try { return res(v[`--colors-${fam}-9`] ?? '', mode); } catch { return ''; } })();
      if (!want || !got.startsWith('oklch(')) { f.push(`${d}: ${fam} 9 missing in ${mode}`); continue; }
      const e = dE(nums(want), nums(got)); if (e > 0.05) f.push(`${d}: ${fam} 9 in ${mode} is ΔE ${e.toFixed(2)} from the system`); } }
  const man = readJson(join(root, 'manifest.json'));
  for (const x of man.files) { const p = join(root, x.path); if (!existsSync(p)) { f.push(`manifest lists ${x.path}, which is missing`); continue; } if (createHash('sha256').update(readFileSync(p)).digest('hex') !== x.sha256) f.push(`manifest hash of ${x.path} is stale`); }
  for (const doc of ['README.md', 'USAGE.md', 'globals.css']) if (!existsSync(join(root, doc))) f.push(`${doc} missing`);
  return f;
}
function checkBadRequests(list) {
  const f = [];
  list.forEach((rq, i) => { try { runSystem({ ...rq, extraModes: false, tonal: false, alpha: false, series: false, dtcg: false }, join(tmp, `bad-${i}-${Math.random().toString(36).slice(2, 8)}`)); f.push(`${JSON.stringify(rq)} was accepted`); } catch (e) { if (e.status !== 2) f.push(`${JSON.stringify(rq)} exited ${e.status}, not 2`); } });
  return f;
}
// 10. Series CVD: present for every mode, and the unsimulated minimum recomputed (OKLab ΔE × 100 on the sRGB fallback).
function checkCvd(j) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) { const c = M.seriesCvd; if (!c) { f.push(id + ': seriesCvd missing'); continue; }
    for (const k of ['normal', 'protan', 'deutan', 'tritan']) if (!(c[k]?.minDE >= 0)) f.push(`${id}: seriesCvd.${k} missing`);
    const s = M.series.map((x) => { const [L, C, H] = x.oklch; return [L, clampChroma(L, C, H, 'srgb'), H]; }); let min = Infinity;
    for (let a = 0; a < s.length; a++) for (let b = a + 1; b < s.length; b++) min = Math.min(min, dE(s[a], s[b]));
    if (Math.abs(min - c.normal.minDE) > 0.05) f.push(`${id}: normal minDE reported ${c.normal.minDE}, recomputed ${min.toFixed(2)}`);
    if (c.ok !== ['normal', 'protan', 'deutan', 'tritan'].every((k) => c[k].minDE >= c.threshold)) f.push(`${id}: seriesCvd.ok disagrees with its minima`); }
  return f;
}
// 11. Tonal agreement and map present and sane.
function checkTonal(j) {
  const f = [], a = j.diagnostics?.tonalAgreement; if (!a) return ['diagnostics.tonalAgreement missing'];
  for (const id of Object.keys(j.modes)) { const s = a.modes?.[id]?.chromaHueDE; if (!s || !(s.mean >= 0 && s.max >= s.mean)) f.push(`${id}: tonalAgreement stats missing`);
    const t = j.modes[id].tonalMap; if (!t || Object.keys(t).length !== 7 || Object.values(t).some((r) => r.steps.length !== 12)) f.push(`${id}: tonalMap needs 7 roles × 12 steps`); }
  return f;
}

// 12. Showcase (references/showcase.md), from the marks showcase.html emits: data-group, data-specimen, data-annot,
// data-flag, data-mode-panel. Everything expected is derived here from system.json, not from the showcase module.
const SHOWCASE = { ramps: ['ramps-light', 'ramps-dark', 'step-use'], modes: ['mode-light', 'mode-dark', 'mode-extra'], neutral: ['neutral-ramp', 'surface-ladder', 'control-fills'],
  roles: ['solids', 'status', 'focus'], transparency: ['alpha-page', 'alpha-surface', 'scrim'], scales: ['tonal', 'contrast', 'tonal-map'], brand: ['anchors', 'ground-ink', 'gamut'], data: ['series', 'series-cvd', 'data-ramps'] };
const attrsIn = (tag) => Object.fromEntries([...tag.matchAll(/([\w-]+)="([^"]*)"/g)].map((m) => [m[1], m[2]]));
// 12a. 24 specimens in 8 groups, three each, every id once.
function checkShowcaseShape(html) {
  const f = [], seen = {}; let cur = null;
  for (const m of html.matchAll(/data-group="([\w-]+)"|data-specimen="([\w-]+)"/g)) { if (m[1]) { if (seen[m[1]]) f.push('group twice: ' + m[1]); cur = m[1]; seen[cur] = []; } else if (!cur) f.push('specimen outside a group: ' + m[2]); else seen[cur].push(m[2]); }
  const groups = Object.keys(seen), specs = Object.values(seen).flat();
  if (groups.length !== 8) f.push(`${groups.length} groups, not 8`);
  if (specs.length !== 24) f.push(`${specs.length} specimens, not 24`);
  for (const [g, want] of Object.entries(SHOWCASE)) { if (!seen[g]) { f.push('missing group ' + g); continue; } if (seen[g].join() !== want.join()) f.push(`group ${g} has ${seen[g].join(', ')}, not ${want.join(', ')}`); }
  return f;
}
// 12b. The construction annotation: each primary step's Lc and target, the solid's APCA Lc against its label with the
// floor, and the key run 9–12 — equal to system.json (and, for the key run, to the Lc recomputed from the ramps) in the data
// attributes and in the text a reader sees.
function checkShowcaseAnnotation(html, j) {
  const f = [], M = j.modes.light, pf = M.roles.primary === 'neutral' ? 'gray' : M.roles.primary, t = M.settings.targetsLight, steps = new Set();
  for (const m of html.matchAll(/<span ([^>]*data-annot="lc"[^>]*)>([^<]*)</g)) { const a = attrsIn(m[1]), n = +a['data-step'], s = M.ramps[pf][n - 1]; steps.add(n);
    if (!s) { f.push('annotation for a missing step ' + n); continue; }
    if (+a['data-lc'] !== s.apcaOnPage) f.push(`step ${n}: Lc ${a['data-lc']} ≠ system.json ${s.apcaOnPage}`);
    if (!m[2].startsWith('Lc ' + s.apcaOnPage)) f.push(`step ${n}: text "${m[2]}" does not show Lc ${s.apcaOnPage}`);
    const want = n === 1 ? undefined : String(t[n - 2]); if (a['data-target'] !== want) f.push(`step ${n}: target ${a['data-target']} ≠ ${want}`); }
  if (steps.size !== 12) f.push(`${steps.size} annotated steps, not 12`);
  const pair = M.contrast.pairs.find((p) => p.fg === 'primary-on-solid' && p.bg === 'primary-solid'), m = /<p ([^>]*data-annot="solid-lc"[^>]*)>([\s\S]*?)<\/p>/.exec(html);
  if (!m) f.push('no solid-lc annotation'); else { const a = attrsIn(m[1]);
    if (+a['data-value'] !== pair.lc) f.push(`solid Lc ${a['data-value']} ≠ system.json ${pair.lc}`);
    if (+a['data-floor'] !== thrOf(j, M).solid) f.push(`solid floor ${a['data-floor']} ≠ ${thrOf(j, M).solid}`);
    if (+a['data-step'] !== (M.solidSteps?.primary ?? 9)) f.push(`solid step ${a['data-step']} ≠ ${M.solidSteps?.primary ?? 9}`);
    if (!m[2].includes('Lc ' + pair.lc + '</b>')) f.push(`solid annotation text does not show Lc ${pair.lc}`); }
  const k = /<span ([^>]*data-annot="keyrun"[^>]*)>([^<]*)</.exec(html), r = M.ramps[pf], page = toneOk(r[0].oklch);
  if (!k) f.push('no keyrun annotation'); else { const shown = attrsIn(k[1])['data-lc'].split(' ').map(Number);
    if (shown.join(' ') !== M.keyRun[pf].lc.join(' ')) f.push(`keyrun ${shown.join(' ')} ≠ system.json ${M.keyRun[pf].lc.join(' ')}`);
    shown.forEach((v, i) => { const lc = apcaLc(toneOk(r[8 + i].oklch), page); if (Math.abs(v - lc) > 0.1) f.push(`keyrun step ${9 + i}: shown ${v}, recomputed ${lc.toFixed(2)}`); });
    if (!k[2].includes(shown.join(' → '))) f.push(`keyrun text "${k[2]}" does not show ${shown.join(' → ')}`); }
  return f;
}
// 12c. Every failure system.json reports is flagged, and nothing else: APCA misses per mode (with the count), series under
// the CVD threshold per mode and simulation, key-run deviations (mode, family, step, reason), anchors out of order or range
// or clipped (per role, with the modes).
function checkShowcaseFlags(html, j) {
  const f = [], want = new Set(), have = new Set();
  for (const [id, M] of Object.entries(j.modes)) {
    const n = M.contrast.pairs.filter((p) => !p.pass).length; if (n) want.add(`lc-miss|${id}|${n}`);
    if (M.seriesCvd) for (const k of ['normal', 'protan', 'deutan', 'tritan']) if (M.seriesCvd[k].minDE < M.seriesCvd.threshold) want.add(`series-weak|${id}|${k}`);
    for (const [fam, r] of Object.entries(M.keyRun || {})) for (const d of r.deviations) want.add(`keyrun|${id}|${fam}|${d.step}|${d.reason}`);
    if (M.separation && !M.separation.pass) want.add(`separation|${id}`);
  }
  const roles = new Set(Object.values(j.modes).flatMap((M) => M.anchorReport.map((a) => a.role)));
  for (const role of roles) for (const [kind, bad] of [['anchor-order', (a) => a.inOrder === false], ['anchor-range', (a) => a.inRange === false], ['anchor-clip', (a) => a.gamut?.inTarget === false]]) {
    const ms = Object.entries(j.modes).filter(([, M]) => { const a = M.anchorReport.find((x) => x.role === role); return a && bad(a); }).map(([id]) => id).sort(); if (ms.length) want.add(`${kind}|${role}|${ms.join(' ')}`); }
  for (const m of html.matchAll(/<span class="sc-flag" ([^>]*)>/g)) { const a = attrsIn(m[1]), k = a['data-flag'];
    have.add(k === 'lc-miss' ? `${k}|${a['data-mode']}|${a['data-count']}` : k === 'series-weak' ? `${k}|${a['data-mode']}|${a['data-kind']}` : k === 'keyrun' ? `${k}|${a['data-mode']}|${a['data-family']}|${a['data-step']}|${a['data-reason']}` : k === 'separation' ? `${k}|${a['data-mode']}` : `${k}|${a['data-role']}|${(a['data-modes'] || '').split(' ').sort().join(' ')}`); }
  for (const k of want) if (!have.has(k)) f.push('not shown: ' + k);
  for (const k of have) if (!want.has(k)) f.push('flagged but not in system.json: ' + k);
  return f;
}
// 12d. Mode panels carry their mode's forced selector (scope included), so each takes that mode's variables; every colour
// is a variable system.css declares or a value from system.json (or a light step's sRGB fallback); the sheet's own CSS
// names no colour.
function checkShowcaseColours(html, j, css) {
  const f = [], req = j.resolvedRequest || j.request, scope = req.scope || '';
  const sel = (id) => { const c = id.endsWith('-contrast'), b = id.replace(/-contrast$/, ''); return scope + (j.selectors === 'attribute' ? (c ? `[data-color-mode=${b}][data-contrast=more]` : `[data-color-mode=${id}]`) : (c ? `.${b}.contrast-more` : `.${id}`)); };
  const panels = [...html.matchAll(/<(?:div|main) ([^>]*data-mode-panel="([\w-]+)"[^>]*)>/g)], ids = new Set(panels.map((m) => m[2]));
  for (const id of ['light', 'dark', ...Object.keys(j.modes).filter((x) => x !== 'light' && x !== 'dark').slice(0, 1)]) if (!ids.has(id)) f.push('no panel for mode ' + id);
  for (const [, tag, id] of panels) { if (!j.modes[id]) { f.push('panel for unknown mode ' + id); continue; } const a = attrsIn(tag), cls = (a.class || '').split(/\s+/), s = sel(id);
    for (const c of s.matchAll(/\.([\w-]+)/g)) if (!cls.includes(c[1])) { f.push(`panel ${id} lacks class ${c[1]} (${s})`); break; }
    for (const c of s.matchAll(/\[([\w-]+)(?:="?([\w-]+)"?)?\]/g)) if (a[c[1]] !== (c[2] ?? '')) { f.push(`panel ${id} lacks [${c[1]}=${c[2] ?? ''}] (${s})`); break; } }
  const at = html.indexOf('</head>'), styles = [...html.slice(0, at).matchAll(/<style>([\s\S]*?)<\/style>/g)].map((m) => m[1]), body = html.slice(at);
  if (styles.length !== 2 || styles[0] !== css) f.push('the first stylesheet is not system.css as written');
  const sheet = styles.at(-1) || '', lit = /#[0-9a-f]{3,8}\b|\b(?:oklch|oklab|rgba?|hsla?|color|lab|lch|hwb)\(|(?<![\w-])(?:white|black|red|blue|green|gray|grey)(?![\w-])/gi;
  for (const m of sheet.matchAll(lit)) f.push('sheet CSS names a colour: ' + m[0]);
  const declared = new Set([...css.matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1]));
  for (const m of (sheet + body).matchAll(/var\((--(?:colors|palette)-[\w-]+)\)/g)) if (!declared.has(m[1])) { f.push(`var(${m[1]}) is not declared by system.css`); break; }
  const jsonText = JSON.stringify(j), fallbacks = new Set(Object.values(j.modes.light.ramps).flat().map((s) => { const [L, C, H] = s.oklch; return `oklch(${+L.toFixed(4)} ${+clampChroma(L, C, H, 'srgb').toFixed(4)} ${+(((H % 360) + 360) % 360).toFixed(2)})`; }));
  for (const st of body.matchAll(/style="([^"]*)"/g)) for (const m of st[1].replace(/var\([^)]*\)/g, '').matchAll(/#[0-9a-f]{3,8}\b|(?:oklch|oklab|color|rgba?)\([^)]*\)/gi)) {
    const v = m[0]; if (!jsonText.includes(v.replace(/"/g, '\\"')) && !css.includes(v) && !fallbacks.has(v)) f.push('colour not from the run: ' + v); }
  return f;
}
const checkShowcase = (dir, j) => { const p = join(dir, 'showcase.html'); if (!existsSync(p)) return ['missing showcase.html']; const html = readFileSync(p, 'utf8'), css = readFileSync(join(dir, 'system.css'), 'utf8');
  return [...checkShowcaseShape(html), ...checkShowcaseAnnotation(html, j), ...checkShowcaseFlags(html, j), ...checkShowcaseColours(html, j, css)]; };

// 9b. Disabled roles: bg-disabled is the muted fill and fg-disabled the neutral (or ink) step 8, in every mode; both pairs are
// listed under contrast.unleveled with level "none", and no matrix pair holds a disabled role to a threshold.
function checkDisabled(j, split) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) { const V = M.variables, c = M.contrast;
    if (V['--colors-bg-disabled'] !== 'var(--colors-bg-muted)') f.push(`${id} --colors-bg-disabled is ${V['--colors-bg-disabled']}`);
    const want = `var(--colors-${split ? 'ink' : 'neutral'}-8)`; if (V['--colors-fg-disabled'] !== want) f.push(`${id} --colors-fg-disabled is ${V['--colors-fg-disabled']}, not ${want}`);
    for (const bg of ['bg-disabled', 'bg']) { const u = (c.unleveled || []).find((p) => p.fg === 'fg-disabled' && p.bg === bg); if (!u || u.level !== 'none' || !(u.lc > 0)) f.push(`${id}: fg-disabled on ${bg} is not reported as unleveled`); }
    for (const p of c.pairs) if (/-disabled$/.test(p.fg) || /-disabled$/.test(p.bg)) f.push(`${id}: ${p.fg} on ${p.bg} holds a disabled role to a threshold`); }
  return f;
}
// 9c. Quiet ink on a solid: each scale role's -on-solid-muted is the step of its own family that solidMuted names, is held to
// apca.hint against the role's solid in the matrix, and a solve reported as reached passes there.
function checkSolidMuted(j) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) for (const [role, m] of Object.entries(M.solidMuted || { missing: {} })) {
    if (role === 'missing') { f.push(`${id}: solidMuted missing`); continue; }
    const got = M.variables[`--colors-${role}-on-solid-muted`], want = m.step ? `var(--colors-${m.family}-${m.step})` : `var(--colors-${role}-on-solid)`;
    if (got !== want) f.push(`${id} --colors-${role}-on-solid-muted is ${got}, not ${want}`);
    const p = M.contrast.pairs.find((x) => x.fg === role + '-on-solid-muted' && x.bg === role + '-solid');
    if (!p || p.intent !== 'hint') f.push(`${id}: ${role}-on-solid-muted on ${role}-solid is not a hint pair of the matrix`);
    else if (m.reached && !p.pass) f.push(`${id}: ${role}-on-solid-muted reported as reached but Lc ${p.lc} is under ${p.threshold}`); }
  return f;
}
// 9d. The inverse pair on the endpoints: where the request names an endpoint, bg-inverse is the scheme's far endpoint (black in
// light, white in dark) and fg-inverse the near one; a side whose endpoint is not named, and every mode of a request without
// `endpoints`, keeps neutral 12 and 1. The pair is a text pair of the matrix.
function checkInverse(j) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) { const V = M.variables, E = j.request.modes?.[id]?.endpoints ?? j.request.endpoints ?? {}, dark = M.scheme === 'dark', far = dark ? 'white' : 'black', near = dark ? 'black' : 'white';
    const bg = V['--colors-bg-inverse'], fg = V['--colors-fg-inverse'];
    if (E[far] != null ? bg !== `var(--colors-${far})` : /--colors-(white|black)\)/.test(bg)) f.push(`${id} --colors-bg-inverse is ${bg} with endpoints ${JSON.stringify(E)}`);
    if (E[near] != null ? fg !== `var(--colors-${near})` : /--colors-(white|black)\)/.test(fg)) f.push(`${id} --colors-fg-inverse is ${fg} with endpoints ${JSON.stringify(E)}`);
    if (!M.contrast.pairs.some((p) => p.fg === 'fg-inverse' && p.bg === 'bg-inverse' && p.intent === 'text')) f.push(`${id}: fg-inverse on bg-inverse is not a text pair of the matrix`); }
  return f;
}
// 9e. Default endpoints: without `endpoints`, white is at least as light as every step of every ramp in the mode and black at
// least as dark, and each is short of pure unless a step already is pure. A request that names a step or `pure` is not held to this.
function checkEndpoints(j) {
  const f = [];
  if (j.request.endpoints) return f;
  // An endpoint is the same in both schemes, so a pure step in any mode's ramps lets it be pure in every mode.
  const any = Object.values(j.modes).flatMap((M) => Object.values(M.ramps).flatMap((r) => r.map((x) => x.oklch[0]))), HI = Math.max(...any), LO = Math.min(...any);
  for (const [id, M] of Object.entries(j.modes)) { if (j.request.modes?.[id]?.endpoints) continue;
    const L = (k) => nums(M.variables[k] || '')[0], all = Object.values(M.ramps).flatMap((r) => r.map((s) => s.oklch[0])), w = L('--colors-white'), b = L('--colors-black');
    const hi = Math.max(...all), lo = Math.min(...all), e = 0.0002;
    if (w < hi - e || (HI < 1 - e && !(w > hi && w < 1))) f.push(`${id}: --colors-white L ${w} is not past the lightest step (${hi.toFixed(4)}) and short of pure`);
    if (b > lo + e || (LO > e && !(b < lo && b > 0))) f.push(`${id}: --colors-black L ${b} is not past the darkest step (${lo.toFixed(4)}) and short of pure`); }
  return f;
}
// 13. Neutrals split (references/system.md › Neutrals), each re-derived here from the request on its own.
// 13a. Role mapping: every split role points at its family and step (restated here, not imported), gray-N is an alias of
// ink-N and ink-N is the gray ramp's own colour; the default run has none of it.
const SPLIT = { bg: 'ground 1', 'bg-subtle': 'ground 2', surface: 'surface 1', 'surface-subtle': 'surface 2', 'surface-muted': 'surface 3', 'bg-muted': 'surface 3', 'bg-muted-hover': 'surface 4', 'bg-muted-active': 'surface 5',
  border: 'surface 6', 'border-strong': 'surface 7', 'control-border': 'surface 8', fg: 'ink 12', 'fg-muted': 'ink 11', 'bg-inverse': 'ink 12', 'fg-inverse': 'ground 1' };
const SPLIT_MIX = { 'bg-control': 'surface 12', 'bg-control-hover': 'surface 12', 'bg-control-active': 'surface 12', shadow: 'ground 12|ground 1', 'bg-overlay': 'surface 1|surface 3', 'bg-overlay-muted': 'surface 3|surface 4' };
// Follow var() aliases inside one mode's variables to the colour they name.
const resolveVar = (V, x) => { for (let d = 0; d < 8 && /^var\(/.test(x || ''); d++) x = V[/^var\((--[\w-]+)\)$/.exec(x)[1]]; return x && /^oklch\(/.test(x) ? x : null; };
// Generated, not derived: every value in the CSS files and the JSON variables is a colour or an alias, never color-mix(),
// calc() or relative colour syntax (`from`), which would leave the browser to derive the colour.
const DERIVED = /color-mix\(|calc\(|\(\s*from\s/;
const checkGenerated = (texts) => texts.flatMap(([name, t]) => t.split('\n').filter((l) => /^\s*--/.test(l) && DERIVED.test(l)).slice(0, 3).map((l) => `${name}: ${l.trim().slice(0, 110)}`));
const checkGeneratedJson = (j, name) => Object.entries(j.modes).flatMap(([id, M]) => Object.entries(M.variables).filter(([, x]) => DERIVED.test(String(x))).slice(0, 3).map(([k, x]) => `${name} ${id} ${k}: ${x}`));
// Selection fills by emphasis e (0–2), recomputed: light neutral 3 → neutral 1 (t = clamp(e)) → primary 3 (t = clamp(e − 1));
// dark neutral 4 → bg-inverse (t = clamp(e)) → primary solid (t = clamp(e − 1)), text neutral 12 → fg-inverse → the solid's label;
// bg-selected-multiple is the lowest of neutral (surface) steps 5–7 at apca.ui against step 1, at every emphasis. Under the split: surface 3, surface 4,
// ink 12. A whole step is an alias to it; between steps the OKLCH mix (shorter hue arc) as a colour.
const mixC = (a, b, t) => { let ha = a[2], hb = b[2]; if (a[1] < 1e-4) ha = hb; if (b[1] < 1e-4) hb = ha; const d = ((hb - ha + 540) % 360) - 180; return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, ha + d * t]; };
function checkSelection(j, e, split) {
  const f = [], cl = (x) => Math.min(1, Math.max(0, x)), lo = cl(e), hi = cl(e - 1);
  const n = (k) => '--colors-' + (split ? { 'neutral-3': 'surface-3', 'neutral-1': 'surface-4', 'neutral-4': 'surface-4', 'neutral-12': 'ink-12' }[k] ?? k : k);
  for (const [id, M] of Object.entries(j.modes)) { const V = M.variables, col = (k) => nums(resolveVar(V, `var(${k})`) || '').slice(0, 3);
    const step = (a, b, t) => (t <= 0 ? a : t >= 1 ? b : mixC(typeof a === 'string' ? col(a) : a, typeof b === 'string' ? col(b) : b, t));
    let want = M.scheme === 'light' ? { 'bg-selected': step(step(n('neutral-3'), n('neutral-1'), lo), n('primary-3'), hi), 'fg-selected': n('neutral-12') } : { 'bg-selected': step(step(n('neutral-4'), '--colors-bg-inverse', lo), '--colors-primary-solid', hi), 'fg-selected': step(step(n('neutral-12'), '--colors-fg-inverse', lo), '--colors-fg-on-solid', hi) };
    { const fam = split ? 'surface' : 'neutral', row = col(`--colors-${fam}-1`), s = [5, 6, 7].find((k) => lcOk(col(`--colors-${fam}-${k}`), row) >= M.apca.ui + 0.5) ?? 7; want['bg-selected-multiple'] = `--colors-${fam}-${s}`; }
    for (const [r, w] of Object.entries(want)) { const got = V['--colors-' + r];
      if (typeof w === 'string') { if (got !== `var(${w})`) f.push(`${id} --colors-${r} is ${got}, not var(${w})`); }
      else if (!/^oklch\(/.test(got || '') || dE(nums(got).slice(0, 3), w) > 0.05) f.push(`${id} --colors-${r} is ${got}, not the emphasis ${e} mix`); } }
  return f;
}
// 14. Terms (references/terms.json): the vocabulary as data. Shape, links, and the role catalogue against what the runs emit,
// both ways: every emitted role is catalogued and every catalogued role is emitted by some run.
const LAYERS = ['source', 'system', 'role', 'input', 'axis'];
// 14b. Terms in the docs: every concept's term (or an accepted alias) is used in SKILL.md or references/system.md under
// that label; no `avoid` phrase appears in SKILL.md or references/*.md; every concrete variable a concept owns (`names`
// without a placeholder) is emitted by some run.
const termLabel = (t) => t.replace(/\s*\(.*\)\s*$/, '').trim();
const phraseRe = (w) => new RegExp('(?<![\\w-])' + w.toLowerCase().split(/[\s-]+/).map((x) => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('[\\s-]') + 's?(?![\\w-])', 'i');
function checkTermsInDocs(T, docs, refs, runs) {
  const f = [], used = docs.join('\n'), all = refs.join('\n');
  for (const c of T.concepts) {
    const labels = [termLabel(c.term), ...(c.aliases || []).map(termLabel)];
    if (!labels.some((l) => phraseRe(l).test(used))) f.push(`concept ${c.id}: neither "${labels.join('" nor "')}" appears in SKILL.md or references/system.md`);
    for (const a of c.avoid || []) { const m = all.split('\n').findIndex((l) => phraseRe(a).test(l)); if (m >= 0) f.push(`concept ${c.id}: avoided phrase "${a}" is used in the docs (line ${m + 1} of the joined docs)`); }
  }
  const emitted = new Set(runs.flatMap((j) => Object.values(j.modes).flatMap((M) => Object.keys(M.variables))));
  for (const c of T.concepts) for (const n of c.names || []) if (/^--[\w-]+$/.test(n) && !emitted.has(n)) f.push(`concept ${c.id}: names ${n}, which no run emits`);
  return f;
}
// 15. Invariants named in SKILL.md › Invariants. Host-project names: the words are stored reversed so this file never
// contains them. Default targets: the default system and the field-operator palette preset are Display P3.
const FORBIDDEN = ['omissam', 'nosiam'].map((w) => [...w].reverse().join(''));
function checkNames(files) {
  const f = [];
  for (const [path, text] of files) for (const w of FORBIDDEN) { const i = text.toLowerCase().indexOf(w); if (i >= 0) f.push(`${path}: contains a host-project name at offset ${i}`); }
  return f;
}
// 15b. Entry files: every relative Markdown link in SKILL.md and references/*.md resolves to a file the skill ships, and
// SKILL.md stays under the host's 18,000-character limit. `files` is [path, text] pairs; `exists` takes a skill-relative path.
function checkEntry(files, exists) {
  const f = [];
  for (const [path, text] of files) {
    if (path === 'SKILL.md' && text.length >= 18000) f.push(`SKILL.md is ${text.length} characters (limit 18,000)`);
    // The description is written unquoted, so it must stay a plain YAML scalar of at most 1,024 characters, or a host refuses the file.
    if (path === 'SKILL.md') { const d = (/^description: (.*)$/m.exec(text) || [])[1]; if (d == null) f.push('SKILL.md has no description'); else { if (d.length > 1024) f.push(`description is ${d.length} characters (limit 1,024)`); if (/: | #/.test(d)) f.push('description holds ": " or " #", which ends a plain YAML scalar'); } }
    for (const m of text.matchAll(/\]\(([^)#\s]+)(?:#[^)]*)?\)/g)) {
      if (/^[a-z]+:/i.test(m[1])) continue;
      if (!exists(join(dirname(path), m[1]))) f.push(`${path}: link ${m[1]} does not resolve`);
    }
  }
  return f;
}
// 15c. Requested translucent roles (request key `translucent`): each is emitted in every mode as a literal at the alpha asked
// for that mode's scheme, on the base the request names, and reported in system.json; a system without the key has none.
const BAD_TRANSLUCENT = [[], { Bad: { of: 'bg', alpha: 0.5 } }, { x: { of: 'bg' } }, { x: { of: 'bg', alpha: 2 } }, { x: { of: 'nope', alpha: 0.5 } }, { bg: { of: 'fg', alpha: 0.5 } },
  { x: { of: 'shadow', alpha: 0.5 } }, { x: { of: '#fff', alpha: 0.5 } }, { x: { of: 'bg', alpha: 0.5, extra: 1 } }, { x: { of: 'bg', alpha: 0.5, darkAlpha: -0.1 } }].map((translucent) => ({ translucent }));
function checkTranslucent(j, css, spec, plain) {
  const f = [], num = (s) => s.match(/-?[\d.]+/g).map(Number), isColour = (s) => /^#|\(/.test(s), TOL = [1e-4, 1e-4, 6e-3];
  for (const [id, M] of Object.entries(j.modes)) {
    const dark = M.scheme === 'dark';
    for (const [name, e] of Object.entries(spec)) {
      const key = '--colors-' + name, got = M.variables[key], want = dark && e.darkAlpha != null ? e.darkAlpha : e.alpha, rep = (M.translucent || {})[name];
      if (!got) { f.push(`${id}: ${key} is not emitted`); continue; }
      if (!/^oklch\(-?[\d.]+ -?[\d.]+ -?[\d.]+(?: \/ [\d.]+)?\)$/.test(got)) { f.push(`${id}: ${key} is not a literal colour (${got})`); continue; }
      const n = num(got), alpha = n.length > 3 ? n[3] : 1;
      if (Math.abs(alpha - want) > 5e-4) f.push(`${id}: ${key} has alpha ${alpha}, the request asks ${want}`);
      if (!rep || Math.abs(rep.alpha - want) > 1e-9) { f.push(`${id}: system.json › translucent.${name} is missing or reports another alpha`); continue; }
      const base = num(rep.base), src = [].concat(dark && e.darkOf != null ? e.darkOf : e.of).find((s) => isColour(s) || '--colors-' + s in M.variables);
      if (base.slice(0, 3).some((x, i) => Math.abs(x - n[i]) > 1e-9)) f.push(`${id}: ${key} is not its reported base ${rep.base}`);
      if (src !== rep.of) f.push(`${id}: translucent.${name} reports base ${rep.of}, the request names ${src}`);
      else if (!isColour(src)) { const lit = resolveVar(M.variables, M.variables['--colors-' + src]); if (!lit || num(lit).slice(0, 3).some((x, i) => Math.abs(x - base[i]) > TOL[i])) f.push(`${id}: ${key} is not ${src} of this mode`); }
      if (!css.includes(key + ': ')) f.push(`system.css lacks ${key}`);
    }
  }
  for (const [id, M] of Object.entries(plain.modes)) if ('translucent' in M) f.push(`a system without the key: mode ${id} reports translucent roles`);
  return f;
}
const checkTargets = (system, preset) => [...(system.target === 'display-p3' ? [] : [`default system targets ${system.target}, not display-p3`]), ...(preset.request && preset.request.target === 'display-p3' ? [] : [`palette preset targets ${preset.request && preset.request.target}, not display-p3`])];
// 16. Closed sets declared once: system.mjs KEYS and the system.md Request keys table name the same keys; preset.mjs
// ALLOWED keys are each documented in references/requests.md.
const docKeys = (md) => { const sec = (md.split('\n## Request keys')[1] || '').split('\n## ')[0]; return new Set(sec.split('\n').filter((l) => /^\| `/.test(l)).flatMap((l) => [...l.split('|')[1].matchAll(/`([\w.]+)`/g)].map((m) => m[1]))); };
function checkKeyClosure(keys, md, allowed, requestsMd) {
  const d = docKeys(md), f = [];
  for (const k of keys) if (!d.has(k)) f.push(`request key ${k} is accepted by system.mjs but has no row in system.md › Request keys`);
  for (const k of d) if (!keys.includes(k)) f.push(`system.md documents request key ${k}, which system.mjs rejects`);
  for (const k of allowed) if (!requestsMd.includes('`' + k + '`')) f.push(`preset.mjs accepts ${k}, which references/requests.md does not document`);
  return f;
}
function checkTerms(T, runs) {
  const f = [], ids = new Set();
  for (const p of T.principles || []) if (!p.id || !p.rule || !p.why) f.push('principle ' + (p.id || '?') + ' lacks id, rule or why');
  for (const c of T.concepts || []) { if (ids.has(c.id)) f.push('duplicate concept ' + c.id); ids.add(c.id);
    for (const k of ['id', 'term', 'layer', 'definition', 'intent']) if (!c[k]) f.push(`concept ${c.id || '?'} lacks ${k}`);
    if (c.layer && !LAYERS.includes(c.layer)) f.push(`concept ${c.id} has unknown layer ${c.layer}`); }
  for (const c of T.concepts || []) for (const r of c.related || []) if (!ids.has(r)) f.push(`concept ${c.id} relates to unknown ${r}`);
  const R = T.roles || {}, scale = R.scaleRoles || [], suf = R.scaleSuffixes || {}, page = R.page || {};
  for (const [k, c] of [...Object.entries(suf), ...Object.entries(page)]) if (!ids.has(c)) f.push(`role ${k} names unknown concept ${c}`);
  const norm = (r) => r.replace(/-\d+$/, '-<n>');
  const known = new Set([...Object.keys(page), ...scale.flatMap((x) => Object.keys(suf).map((sx) => x + sx))]);
  const seen = new Set();
  for (const j of runs) { const fam = new Set([...j.families.all, 'gray', 'ground', 'surface', 'ink']);
    for (const M of Object.values(j.modes)) for (const k of Object.keys(M.variables)) { const m = /^--colors-(.+)$/.exec(k); if (!m) continue;
      const fm = /^(.+)-a?\d+$/.exec(m[1]); if (fm && fam.has(fm[1])) continue;
      const r = norm(m[1]); seen.add(r); if (!known.has(r)) f.push(`emitted role ${m[1]} is not in terms.json › roles`); } }
  for (const r of known) if (!seen.has(r)) f.push(`terms.json › roles lists ${r}, which no run emits`);
  return [...new Set(f)];
}
const varOf = (x) => { const [f, n] = x.split(' '); return `var(--colors-${f}-${n})`; };
function checkNeutralRoles(j) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) { const V = M.variables, dark = M.scheme === 'dark';
    for (const [role, at] of Object.entries(SPLIT)) if (V['--colors-' + role] !== varOf(at)) f.push(`${id} --colors-${role} is ${V['--colors-' + role]}, not ${varOf(at)}`);
    // The backdrop is pure black at 80% in every mode, split or not (system.mjs › BACKDROP_ALPHA).
    if (V['--colors-bg-backdrop'] !== 'oklch(0 0 0 / 0.8)') f.push(`${id} --colors-bg-backdrop is ${V['--colors-bg-backdrop']}, not pure black at 80%`);
    // Translucent split roles are generated colours: the source step's colour at an alpha under 1 (never a var() mix).
    for (const [role, at] of Object.entries(SPLIT_MIX)) { const want = varOf(at.split('|')[dark && at.includes('|') ? 1 : 0]), got = String(V['--colors-' + role]);
      if (got === want) continue; const src = resolveVar(V, want), c = nums(got);
      if (!/^oklch\(/.test(got) || c.length !== 4 || !(c[3] < 1) || !src || dE(c.slice(0, 3), nums(src).slice(0, 3)) > 0.05) f.push(`${id} --colors-${role} (${got}) is not ${want}'s colour at an alpha`); }
    for (let n = 1; n <= 12; n++) { if (V[`--colors-gray-${n}`] !== `var(--colors-ink-${n})`) f.push(`${id} --colors-gray-${n} is not an alias of ink-${n}`);
      const ink = nums(V[`--colors-ink-${n}`] || ''); if (ink.length !== 3 || dE(ink, M.ramps.gray[n - 1].oklch) > 0.05) f.push(`${id} --colors-ink-${n} is not the ink ramp's step ${n}`); }
    if (M.alpha && V['--colors-gray-a1'] !== 'var(--colors-ink-a1)') f.push(`${id} --colors-gray-a1 is not an alias of ink-a1`);
    for (const r of ['fg', 'fg-muted', 'bg', 'border', 'control-border', 'bg-selected', 'fg-selected']) if (/--colors-(gray|neutral)-/.test(V['--colors-' + r] || '')) f.push(`${id} --colors-${r} still reads the one neutral: ${V['--colors-' + r]}`); }
  return f;
}
const checkNoSplit = (j) => { const f = []; for (const [id, M] of Object.entries(j.modes)) { const k = Object.keys(M.variables).find((x) => /^--colors-(ground|surface|ink)(-|$)/.test(x)); if (k) f.push(`${id}: ${k} without neutrals`); if (M.variables['--colors-bg'] !== 'var(--colors-gray-1)') f.push(`${id}: bg is ${M.variables['--colors-bg']}`); if (M.separation || M.neutralSources) f.push(`${id}: split fields without neutrals`); } if (j.neutrals) f.push('json.neutrals without the key'); return f; };
// 13b. Sources: each family's steps 1–7 (nothing post-solves them) equal the neutral the engine makes at the mode's settings
// for that family's spec — ground and ink at the page, surface at the lifted page (+2.5 L* light, capped at 100, else −2.5;
// +4 dark, capped at 20, else −4) — with cross swapping the ground and surface specs in dark schemes. Families an anchor
// pins (ground 1 / ink 12 and the dark ends, surface 1) are skipped.
const LIFT = { light: 2.5, dark: 4 }, genCache = new Map();
const gen = (settings) => { const k = JSON.stringify(settings); if (!genCache.has(k)) genCache.set(k, generateSpectrum(spectrumOverrides(normalizeSpectrum(settings)))); return genCache.get(k); };
function specOf(spec, s) {
  if (!spec) return { set: {}, key: 'neutral' };
  if (spec.from) return { set: { grays: [...new Set([...(s.grays || []), spec.from])] }, key: spec.from === 'Gray' ? 'gray-base' : spec.from.toLowerCase() };
  let nf = spec.neutralFrom ?? s.neutralFrom; if (spec.hue != null) { const g = gen(s), acc = g.metadata.light.accents.slice(0, 12), gap = (x) => { const d = Math.abs(g.schemes.light[x][8].hct[0] - spec.hue) % 360; return Math.min(d, 360 - d); }; nf = acc.indexOf(acc.reduce((a, b) => (gap(b) < gap(a) ? b : a))); }
  return { set: { mat: 'tinted', tint: spec.tint ?? s.tint, neutralFrom: nf }, key: 'neutral' };
}
function checkNeutralSources(j) {
  const f = [], N = splitOf(j); let compared = 0;
  for (const [id, M] of Object.entries(j.modes)) { const s = M.settings, dark = M.scheme === 'dark', cross = N.cross && dark;
    const up = Math.min(100, s.toneMax + LIFT.light), dn = Math.min(20, s.darkTone + LIFT.dark), lift = { toneMax: up - s.toneMax >= 1.5 ? up : s.toneMax - LIFT.light, darkTone: dn - s.darkTone >= 2 ? dn : s.darkTone - LIFT.dark };
    const pinned = (fam) => M.anchorReport.some((a) => (a.role === 'surface' && fam === 'surface') || (a.role === 'neutral' && fam !== 'surface') || (dark ? (a.role === 'ground' && fam === 'ink') || (a.role === 'ink' && fam === 'ground') : (a.role === 'ground' && fam === 'ground') || (a.role === 'ink' && fam === 'ink')));
    for (const [fam, spec, lifted] of [['ground', cross ? N.surface : N.ground, false], ['surface', cross ? N.ground : N.surface, true], ['ink', N.ink, false]]) { if (pinned(fam)) continue;
      const sp = specOf(spec, s), ramp = gen({ ...s, ...sp.set, ...(lifted ? lift : {}) }).schemes[M.scheme][sp.key], mine = M.ramps[fam === 'ink' ? 'gray' : fam];
      if (!ramp || !mine) { f.push(`${id} ${fam}: family missing`); continue; }
      for (let i = 0; i < 7; i++) { compared++; const d = dE(ramp[i].oklch, mine[i].oklch); if (d > 0.1) { f.push(`${id} ${fam} step ${i + 1}: ΔE ${d.toFixed(2)} from the engine's ${sp.key}${lifted ? ' (lifted page)' : ''}${cross ? ' (crossed)' : ''}`); break; } } } }
  if (!compared) f.push('no neutral family to compare');
  return f;
}
// 13c. Separation: surface 1 against ground 1 per mode, OKLab ΔE × 100 and APCA |Lc| recomputed and equal to system.json; the
// threshold is 2 (one CSS Color 4 JND) and pass is ΔE ≥ 2.
const SEP_MIN = 2, SEP_RAISED = 6;
const SEP_LAYERS = [['surface', 'bg', 'resting'], ['bg-overlay', 'bg', 'raised'], ['bg-overlay', 'surface', 'raised'], ['bg-muted', 'surface', 'resting'], ['bg-overlay-muted', 'bg-overlay', 'resting']];
function checkSeparation(j) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) { const S = M.separation; if (!S) { f.push(id + ': separation missing'); continue; }
    const g = M.ramps.ground[0].oklch, sf = M.ramps.surface[0].oklch, d = dE(sf, g), lc = Math.abs(apcaLc(toneOk(sf), toneOk(g)));
    if (Math.abs(d - S.dE) > 0.05) f.push(`${id}: separation ΔE ${S.dE}, recomputed ${d.toFixed(2)}`);
    if (Math.abs(lc - S.lc) > 0.1) f.push(`${id}: separation Lc ${S.lc}, recomputed ${lc.toFixed(2)}`);
    if (S.threshold !== SEP_MIN) f.push(`${id}: separation threshold ${S.threshold}, not ${SEP_MIN}`);
    if (S.pass !== d >= SEP_MIN && Math.abs(d - SEP_MIN) > 0.05) f.push(`${id}: separation pass ${S.pass} at ΔE ${d.toFixed(2)}`);
    // Every adjacent pair of the stack, recomputed from the variables: a resting pair at the floor, a raised pair at the
    // raised gate (6) in a dark scheme and at no gate in a light one.
    const col = (r) => nums(resolveVar(M.variables, `var(--colors-${r})`) || '').slice(0, 3), L = S.layers || [];
    for (const [u, l, level] of SEP_LAYERS) { const p = L.find((x) => x.upper === u && x.lower === l); if (!p) { f.push(`${id}: layer ${u} on ${l} not reported`); continue; }
      const x = dE(col(u), col(l)), need = level === 'resting' ? SEP_MIN : M.scheme === 'dark' ? SEP_RAISED : null;
      if (Math.abs(x - p.dE) > 0.05) f.push(`${id}: layer ${u} on ${l} ΔE ${p.dE}, recomputed ${x.toFixed(2)}`);
      if (p.threshold !== need) f.push(`${id}: layer ${u} on ${l} threshold ${p.threshold}, not ${need}`);
      if (need == null ? p.pass !== null : p.pass !== x >= need && Math.abs(x - need) > 0.05) f.push(`${id}: layer ${u} on ${l} pass ${p.pass} at ΔE ${x.toFixed(2)}`); } }
  return f;
}
const allSeparate = (j) => Object.entries(j.modes).filter(([, M]) => !M.separation?.pass).map(([id, M]) => `${id}: surface 1 ΔE ${M.separation?.dE} from ground 1, under ${SEP_MIN}`);
// 13g. Hover steps (every run): each rest → hover pair recomputed from the emitted variables, OKLab ΔE × 100 within 0.05 —
// bg-muted, bg-control composited over bg (and surface with neutrals) in encoded sRGB, each scale role's -subtle and -solid —
// at threshold 4, pass consistent, summary counts; the neutral's (and surface's) steps 1→6 recomputed from the ramps.
const HOVER_MIN = 4, SCALE = ['primary', 'secondary', 'neutral', 'critical', 'warning', 'success', 'info'];
const encS = (v) => (v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055), decS = (v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
const labLin = (rgb) => { const [l, m, q] = [0.4122214708 * rgb[0] + 0.5363325363 * rgb[1] + 0.0514459929 * rgb[2], 0.2119034982 * rgb[0] + 0.6806995451 * rgb[1] + 0.1073969566 * rgb[2], 0.0883024619 * rgb[0] + 0.2817188376 * rgb[1] + 0.6299787005 * rgb[2]].map(Math.cbrt);
  return [0.2104542553 * l + 0.793617785 * m - 0.0040720468 * q, 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * q, 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * q]; };
function checkHover(j) {
  const f = [];
  for (const [id, M] of Object.entries(j.modes)) { const H = M.hover; if (!H || !Array.isArray(H.pairs)) { f.push(id + ': hover report missing'); continue; }
    if (H.threshold !== HOVER_MIN) f.push(`${id}: hover threshold ${H.threshold}, not ${HOVER_MIN}`);
    const lit = (r) => resolveVar(M.variables, `var(--colors-${r})`), col = (r) => nums(lit(r) || '').slice(0, 3);
    const over = (r, g) => { const c = nums(lit(r) || ''), a = c[3] ?? 1, G = lin(col(g)).map(encS); return labLin(lin(c.slice(0, 3)).map(encS).map((x, i) => x * a + G[i] * (1 - a)).map(decS)); };
    const want = [['bg-muted', 'bg-muted-hover'], ...(splitOf(j) ? ['bg', 'surface'] : ['bg']).map((g) => ['bg-control', 'bg-control-hover', g]), ...SCALE.flatMap((r) => [[r + '-subtle', r + '-subtle-hover'], [r + '-solid', r + '-solid-hover']])];
    for (const [rest, hover, g] of want) { const p = H.pairs.find((x) => x.rest === rest && x.hover === hover && (x.over ?? null) === (g ?? null)); if (!p) { f.push(`${id}: hover pair ${rest} → ${hover}${g ? ' over ' + g : ''} not reported`); continue; }
      const d = g ? 100 * Math.hypot(...over(rest, g).map((x, i) => x - over(hover, g)[i])) : dE(col(rest), col(hover));
      if (!Number.isFinite(d) || Math.abs(d - p.dE) > 0.05) f.push(`${id}: hover ${rest} → ${hover}${g ? ' over ' + g : ''} ΔE ${p.dE}, recomputed ${d.toFixed(2)}`);
      if (p.pass !== d >= HOVER_MIN && Math.abs(d - HOVER_MIN) > 0.05) f.push(`${id}: hover ${rest} → ${hover} pass ${p.pass} at ΔE ${d.toFixed(2)}`); }
    if (H.pairs.length !== want.length) f.push(`${id}: ${H.pairs.length} hover pairs, expected ${want.length}`);
    const fails = H.pairs.filter((p) => !p.pass).length; if (H.summary?.pairs !== H.pairs.length || H.summary?.fail !== fails || H.summary?.failures?.length !== fails) f.push(`${id}: hover summary disagrees with the pairs`);
    const neutralFam = M.roles.neutral === 'neutral' ? 'gray' : M.roles.neutral;
    for (const fam of splitOf(j) ? [neutralFam, 'surface'] : [neutralFam]) { const s = H.steps?.[fam], r = M.ramps[fam]; if (!Array.isArray(s) || s.length !== 5) { f.push(`${id}: hover steps for ${fam} missing`); continue; }
      for (let i = 0; i < 5; i++) { const d = dE(r[i].oklch, r[i + 1].oklch); if (Math.abs(d - s[i]) > 0.05) f.push(`${id}: ${fam} step ${i + 1} → ${i + 2} ΔE ${s[i]}, recomputed ${d.toFixed(2)}`); } } }
  return f;
}
// 3e. The pressed solid (-solid-active), per family and role: `side` is "on" exactly where the solid's label clears
// apca.solid + 0.5 on the step past the hover (11 above a step-9 solid), and the role's variable is then the alias to that
// step; otherwise "back": a colour at page Lc max(Lc9 − (Lc10 − Lc9), apca.ui + 0.5), `clamped` where the limit binds, never
// under apca.ui on the page, the variable that colour. Either way the label clears apca.solid on it, and lc and lcOnPage are
// recomputed (worse of the two renderings with a P3 upgrade).
function checkActive(j) {
  const lcS = lcShown(j), f = [], labels = labelsOf(j), eps = 0.05;
  for (const [id, M] of Object.entries(j.modes)) { const T = thrOf(j, M);
    const one = (fam, st, e, where) => { const a = e?.active, r = M.ramps[fam]; if (!a) { f.push(`${id} ${where}: no active entry`); return; }
      const lab = labels[e.label], page = toneOk(r[0].oklch), lcP = (c) => apcaLc(toneOk(c), page), hv = st === 12 ? 11 : st + 1, on = st === 12 ? 10 : st + 2;
      // Past the hover: a step, or (no step there: an anchored step 11) the colour at one hover gap beyond it, given as oklch
      // (at the end of the lightness range where that gap runs past it).
      const l9 = lcP(r[st - 1].oklch), l10 = lcP(r[hv - 1].oklch), past = on <= 12 ? r[on - 1].oklch : a.side === 'on' ? a.oklch : null, F = T.solid + MARGIN;
      if (on > 12 && a.side === 'on' && Math.abs(lcP(a.oklch) - Math.min(108, 2 * l10 - l9)) > 0.15 && a.oklch[0] > 1e-3 && a.oklch[0] < 1 - 1e-3) f.push(`${id} ${where}: active past the hover at page Lc ${lcP(a.oklch).toFixed(2)}, not ${Math.min(108, 2 * l10 - l9).toFixed(2)}`);
      const onLc = past ? lcS(lab, past) : -1;
      if (past && Math.abs(onLc - F) > eps && (a.side === 'on') !== onLc >= F) f.push(`${id} ${where}: active side ${a.side}, but the label on step ${on} is Lc ${onLc.toFixed(2)} (needs ${F})`);
      const c = a.step ? r[a.step - 1]?.oklch : a.oklch; if (!c) { f.push(`${id} ${where}: active colour missing`); return; }
      if (a.side === 'on' && on <= 12 && a.step !== on) f.push(`${id} ${where}: active on step ${a.step}, not ${on}`);
      // A back step clamped at apca.ui on a solid already nearer the page than that can miss the label: the matrix reports it.
      const v = lcS(lab, c); if (v < T.solid - eps && !(a.side === 'back' && a.clamped)) f.push(`${id} ${where}: label on active Lc ${v.toFixed(2)} < ${T.solid}`);
      if (Math.abs(v - a.lc) > 0.1) f.push(`${id} ${where}: active lc ${a.lc}, recomputed ${v.toFixed(2)}`);
      if (Math.abs(lcP(c) - a.lcOnPage) > 0.1) f.push(`${id} ${where}: active lcOnPage ${a.lcOnPage}, recomputed ${lcP(c).toFixed(2)}`);
      if (a.side === 'back') { const want = l9 - (l10 - l9), min = T.ui + MARGIN;
        if (lcP(c) < T.ui - eps) f.push(`${id} ${where}: back step at page Lc ${lcP(c).toFixed(2)}, under apca.ui ${T.ui}`);
        if (Math.abs(lcP(c) - Math.min(108, Math.max(want, min))) > 0.15) f.push(`${id} ${where}: back step at page Lc ${lcP(c).toFixed(2)}, not ${Math.max(want, min).toFixed(2)}`);
        if (a.clamped !== want < min) f.push(`${id} ${where}: clamped ${a.clamped} with Lc9 − (Lc10 − Lc9) = ${want.toFixed(2)}`); } };
    for (const fam of j.families.all) { const e = M.solidLabels?.[fam]; if (!e) continue; one(fam, 9, e, fam);
      for (const [st, x] of Object.entries(e.anchored || {})) one(fam, +st, x, `${fam} ${st}`); }
    for (const [role, fam0] of Object.entries(M.roles)) { const v = M.variables['--colors-' + role + '-solid-active']; if (!(('--colors-' + role + '-solid') in M.variables) || /^data/.test(role)) continue;
      const fam = fam0 === 'neutral' ? 'gray' : fam0, st = M.solidSteps?.[role] ?? 9, e = M.solidLabels?.[fam], x = st === 9 ? e : e?.anchored?.[st] ?? e, a = x?.active;
      if (v == null || !a) { f.push(`${id} --colors-${role}-solid-active missing`); continue; }
      if (a.step ? v !== `var(--colors-${fam}-${a.step})` : !(nums(v).length === 3 && dE(nums(v), a.oklch) < 0.05)) f.push(`${id} --colors-${role}-solid-active is ${v}, not the ${a.side} step of ${fam} ${st}`); }
    for (const r of SCALE) { const p = (M.hover?.active || []).find((x) => x.active === r + '-solid-active'), d = dE(nums(resolveVar(M.variables, `var(--colors-${r}-solid-hover)`) || '').slice(0, 3), nums(resolveVar(M.variables, `var(--colors-${r}-solid-active)`) || '').slice(0, 3));
      if (!p || Math.abs(p.dE - d) > 0.05) f.push(`${id}: hover → active of ${r} ${p ? 'ΔE ' + p.dE + ', recomputed ' + d.toFixed(2) : 'not reported'}`); } }
  return f;
}
// 13d. Anchors: ground → ground light 1 and ink dark 12; ink → ink light 12 and ground dark 1; surface → surface light 1 and
// (with dark) surface dark 1. Read from the request; hex values, so ΔE ≤ 0.5 covers 8-bit rounding.
const hexOk = (h) => { const c = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255).map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  const l = Math.cbrt(0.4122214708 * c[0] + 0.5363325363 * c[1] + 0.0514459929 * c[2]), m = Math.cbrt(0.2119034982 * c[0] + 0.6806995451 * c[1] + 0.1073969566 * c[2]), q = Math.cbrt(0.0883024619 * c[0] + 0.2817188376 * c[1] + 0.6299787005 * c[2]);
  const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * q, a = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * q, b = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * q; return [L, Math.hypot(a, b), (Math.atan2(b, a) * 180 / Math.PI + 360) % 360]; };
function checkNeutralAnchors(j) {
  const f = [], req = j.resolvedRequest || j.request; let n = 0;
  for (const a of req.anchors || []) { const where = { ground: [['light', 'ground', 1, a.value], ['dark', 'gray', 12, a.dark ?? a.value]], ink: [['light', 'gray', 12, a.value], ['dark', 'ground', 1, a.dark ?? a.value]], surface: [['light', 'surface', 1, a.value], ...(a.dark ? [['dark', 'surface', 1, a.dark]] : [])] }[a.role];
    for (const [id, fam, st, hex] of where || []) { n++; const d = dE(hexOk(hex), j.modes[id].ramps[fam][st - 1].oklch); if (d > 0.5) f.push(`${a.role} anchor ${hex}: ${id} ${fam === 'gray' ? 'ink' : fam} ${st} is ΔE ${d.toFixed(2)} away`); } }
  if (!n) f.push('no ground, ink or surface anchor to check');
  return f;
}
// 13e. The showcase's Neutral & surfaces group shows the three families and a card (surface) on the page per shown mode.
function checkShowcaseNeutrals(html, j) {
  const f = [], grp = /data-group="neutral"[\s\S]*?<\/section>/.exec(html)?.[0] || '';
  for (const fam of ['ground', 'surface', 'ink']) for (let n = 1; n <= 12; n++) if (!grp.includes(`var(--colors-${fam}-${n})`)) { f.push(`neutral group lacks the ${fam} strip (step ${n})`); break; }
  const shown = ['light', 'dark', ...Object.keys(j.modes).filter((x) => x !== 'light' && x !== 'dark').slice(0, 1)];
  const card = /data-specimen="surface-ladder"[\s\S]*?<\/figure>/.exec(grp)?.[0] || '';
  for (const id of shown) { const m = new RegExp(`data-mode-panel="${id}"><div class="sc-page" style="background:var\\(--colors-bg\\)"><div class="sc-card2" style="background:var\\(--colors-surface\\)`).test(card); if (!m) f.push(`no card on the page for mode ${id}`);
    if (!card.includes('ΔE ' + j.modes[id].separation.dE)) f.push(`mode ${id}: separation ΔE ${j.modes[id].separation.dE} not shown`); }
  return f;
}
// 13g. Radix comparison. The bundled data (system/radix-colors.json): 31 @radix-ui/colors scales, each of its eight variants 12
// steps (sRGB hex for light and dark, hex with or without alpha for the alpha ones, Display P3 strings for the P3 ones; Radix ships a few
// alpha steps opaque), the package and version named, the scales hashing to
// their recorded sha256 and the licence text kept. compare: "radix": every family with a Radix scale of its name reported in
// every mode, each step's ΔE and ΔL recomputed here from the system.json ramps and the data (check.mjs's own maths), some step
// measured away from 0, and every pinned family (familyAnchors at Radix's step 9) at ΔE 0 there. Without the key, none of it.
const RADIX = readJson(here + 'system/radix-colors.json');
const RADIX_VARIANTS = ['light', 'lightAlpha', 'lightP3', 'lightP3Alpha', 'dark', 'darkAlpha', 'darkP3', 'darkP3Alpha'];
const RADIX_FORM = { light: /^#[0-9a-f]{6}$/, dark: /^#[0-9a-f]{6}$/, lightAlpha: /^#[0-9a-f]{6}(?:[0-9a-f]{2})?$/, darkAlpha: /^#[0-9a-f]{6}(?:[0-9a-f]{2})?$/, lightP3: /^color\(display-p3 [\d.]+ [\d.]+ [\d.]+\)$/, darkP3: /^color\(display-p3 [\d.]+ [\d.]+ [\d.]+\)$/, lightP3Alpha: /^color\(display-p3 [\d.]+ [\d.]+ [\d.]+(?: \/ [\d.]+)?\)$/, darkP3Alpha: /^color\(display-p3 [\d.]+ [\d.]+ [\d.]+(?: \/ [\d.]+)?\)$/ };
function checkRadixData(d) {
  const f = [], P = d.provenance || {}, names = Object.keys(d.scales || {});
  if (P.package !== '@radix-ui/colors' || !/^\d+\.\d+\.\d+$/.test(P.version || '')) f.push(`provenance names ${P.package}@${P.version}, not @radix-ui/colors at a version`);
  if (!/^[0-9a-f]{64}$/.test(P.tarballSha256 || '')) f.push('provenance has no tarball sha256');
  if (sha(JSON.stringify(d.scales || {})) !== P.scalesSha256) f.push('the scales do not hash to provenance.scalesSha256 (edited by hand, or regenerated without the hash)');
  if (!/^MIT License[\s\S]*Copyright/.test(P.licenseText || '')) f.push('provenance lacks the package licence text');
  if (names.length !== 31) f.push(`${names.length} scales, not 31`);
  for (const n of names) for (const v of RADIX_VARIANTS) { const a = d.scales[n][v];
    if (!Array.isArray(a) || a.length !== 12) { f.push(`${n}.${v}: ${Array.isArray(a) ? a.length : 'no'} steps, not 12`); continue; }
    a.forEach((x, i) => { if (!RADIX_FORM[v].test(x)) f.push(`${n}.${v} step ${i + 1}: ${x} is not a ${v} value`); }); }
  return f;
}
const RADIX_PIN = { orange: { value: RADIX.scales.orange.light[8], dark: RADIX.scales.orange.dark[8] } };
const RADIX_REQ = { extraModes: false, tonal: false, alpha: false, series: false, dtcg: false, familyAnchors: RADIX_PIN, compare: 'radix' };
const BAD_COMPARE = [{ compare: 'material' }, { compare: true }, { compare: ['radix'] }, { compare: null }];
function checkRadixCompare(j, pinned, plain, plainHtml) {
  const f = []; let n = 0, away = 0;
  if (j.compare?.source?.version !== RADIX.provenance.version) f.push(`system.json › compare.source.version is ${j.compare?.source?.version}, the data's is ${RADIX.provenance.version}`);
  for (const [id, M] of Object.entries(j.modes)) {
    if (!M.radix) { f.push(`${id}: no modes.${id}.radix`); continue; }
    for (const fam of j.families.all) { const ref = RADIX.scales[fam], r = M.radix.families[fam]; if (!ref) continue; if (!r) { f.push(`${id}: ${fam} has a Radix scale but is not compared`); continue; }
      r.steps.forEach((s, i) => { n++; const a = M.ramps[fam][i].oklch, b = hexOk(ref[M.scheme][i]), d = dE(a, b);
        if (Math.abs(d - s.dE) > 0.02) f.push(`${id} ${fam} step ${i + 1}: reported ΔE ${s.dE}, recomputed ${d.toFixed(2)}`);
        if (Math.abs(100 * (a[0] - b[0]) - s.dL) > 0.02) f.push(`${id} ${fam} step ${i + 1}: reported ΔL ${s.dL}, recomputed ${(100 * (a[0] - b[0])).toFixed(2)}`);
        if (d > 0.5) away++; }); }
    for (const fam of pinned) { const s = M.radix.families[fam]?.steps[8]; if (!s || s.dE !== 0) f.push(`${id}: ${fam} pinned to Radix step 9 reports ΔE ${s?.dE} there, not 0`); }
  }
  if (n < 13 * 12 * 2) f.push(`only ${n} steps compared`);
  if (!away) f.push('every compared step reports ΔE 0 (nothing measured)');
  if ('compare' in plain || Object.values(plain.modes).some((M) => 'radix' in M) || /class="rdx"/.test(plainHtml)) f.push('a run without the key carries a Radix comparison');
  return f;
}
// 13f. Byte-identical default: the default system.css and system.json hash to the recorded digest (fixtures/default-digest.json).
// A change to the default output must be deliberate: refresh with --update-digest.
const sha = (t) => createHash('sha256').update(t).digest('hex');
const DIGEST = here + 'system/fixtures/default-digest.json';
const checkDigest = (css, jsonText) => { const d = existsSync(DIGEST) ? readJson(DIGEST) : {}; const f = [];
  if (d['system.css'] !== sha(css)) f.push(`default system.css sha256 ${sha(css).slice(0, 12)} ≠ recorded ${String(d['system.css']).slice(0, 12)}`);
  if (d['system.json'] !== sha(jsonText)) f.push(`default system.json sha256 ${sha(jsonText).slice(0, 12)} ≠ recorded ${String(d['system.json']).slice(0, 12)}`); return f; };
const BAD_NEUTRALS = [[], { foo: 1 }, { ground: { from: 'Blue' } }, { ground: { from: 'Sand', tint: 3 } }, { cross: 'yes' }, { ground: { tint: 200 } }, { ground: { neutralFrom: 12 } }, { ground: { hue: 400 } }, { surface: 'Sand' }, { ground: { hue: 30, neutralFrom: 2 } }].map((neutrals) => ({ neutrals }))
  .concat([{ anchors: [{ role: 'surface', value: '#ffffff' }] }, { neutrals: {}, anchors: [{ role: 'surface', value: '#ffffff', step: 2 }] }, { neutrals: { ink: { from: 'Sand' } }, anchors: [{ role: 'neutral', value: '#888888' }] }, { neutrals: {}, roles: { neutral: 'neutral' } }, { neutrals: { ground: { from: 'Sand' } }, settings: { generator: 'oklch' } }]);

// ── Run ───────────────────────────────────────────────────────────────────────────────────────────────────
let failed = false;
try {
  const out1 = join(tmp, 'default'), out2 = join(tmp, 'light-dark'), out3 = join(tmp, 'showcase'), out4 = join(tmp, 'showcase-scoped'), out5 = join(tmp, 'apca-anchored');
  const LD = { brightHues: false, lightDark: true, split: true, figma: true, tonalRoles: true, showcase: true, extraModes: [{ id: 'dim', scheme: 'dark', settings: { darkTone: 14 } }, { id: 'light-contrast', scheme: 'light', contrast: true }, { id: 'dark-contrast', scheme: 'dark', contrast: true }] };
  // Showcase runs: the default system, and a scoped attribute-selector sRGB system with an out-of-order and a clipped anchor.
  const SC = { showcase: true, selectors: 'attribute', scope: '.brand', extraModes: false, settings: { target: 'srgb' }, anchors: [{ role: 'primary', value: '#0a4dff', step: 5 }, { role: 'success', value: 'color(display-p3 0 0.8 0.3)' }] };
  // APCA overrides and key-run anchors: solid 60 and hint 60 (so hint pairs miss), the contrast mode's own solid 75; primary
  // anchored exactly at step 9 in both schemes (its dark hover cannot be spaced evenly: a deviation), secondary at step 11.
  const AN = { showcase: true, extraModes: [{ id: 'light-contrast', scheme: 'light', contrast: true }], apca: { solid: 60, hint: 60, contrast: { solid: 75 } }, anchors: [{ role: 'primary', value: '#0a4dff', step: 9, dark: '#3d6bff', darkStep: 9 }, { role: 'secondary', value: '#8a4b00', step: 11 }] };
  // Neutrals split: Radix Sand page and Slate cards crossed in dark (showcase); generated tinted neutrals (light-dark, split,
  // Figma); ground, ink and surface anchors with a card colour too close to the page (a separation miss).
  const out6 = join(tmp, 'neutrals-cross'), out7 = join(tmp, 'neutrals-tinted'), out8 = join(tmp, 'neutrals-anchored');
  const NA = { showcase: true, neutrals: { ground: { from: 'Sand' }, surface: { from: 'Slate' }, cross: true } };
  const NB = { emphasis: 1.5, diverging: true, lightDark: true, split: true, figma: true, extraModes: [{ id: 'dim', scheme: 'dark', settings: { darkTone: 14 } }], neutrals: { ground: { tint: 20, neutralFrom: 6 }, surface: { tint: 60 }, ink: { hue: 280 } } };
  const NC = { showcase: true, extraModes: false, neutrals: { ground: { from: 'Sand' } }, anchors: [{ role: 'ground', value: '#f6f2ea', dark: '#e9e4da' }, { role: 'ink', value: '#1c1a17', dark: '#121110' }, { role: 'surface', value: '#f7f3eb', dark: '#24221f' }] };
  const line1 = runSystem({}, out1), line2 = runSystem(LD, out2); runSystem({ showcase: true }, out3); runSystem(SC, out4); runSystem(AN, out5); runSystem(NA, out6); runSystem(NB, out7); runSystem(NC, out8);
  console.log('ran system.mjs on {}, a light-dark request, two showcase requests, an APCA-override anchored request and three neutrals requests in ' + tmp + '\n  ' + line1.trim().slice(0, 160) + '…');
  const j6 = readJson(join(out6, 'system.json')), j7 = readJson(join(out7, 'system.json')), j8 = readJson(join(out8, 'system.json')), sc6 = readFileSync(join(out6, 'showcase.html'), 'utf8'), sc8 = readFileSync(join(out8, 'showcase.html'), 'utf8');
  // Requested translucent roles: a role with a dark base and alpha, a given colour, and a list that falls back (surface is split-only).
  const outT = join(tmp, 'translucent'), TR = { tonal: false, series: false, translucent: { 'veil-a': { of: 'neutral-12', alpha: 0.12, darkOf: '#000000', darkAlpha: 0.36 }, 'veil-b': { of: '#ffffff', alpha: 0.5, darkAlpha: 0.125 }, 'veil-c': { of: ['surface', 'bg'], alpha: 0.62 } } };
  runSystem(TR, outT);
  // Endpoints: both pure (the inverse pair follows them), and white alone (only that side follows).
  const outE = join(tmp, 'endpoints'), outE2 = join(tmp, 'endpoints-white'); runSystem({ extraModes: false, tonal: false, endpoints: { white: 'pure', black: 'pure' } }, outE); runSystem({ extraModes: false, tonal: false, endpoints: { white: 'pure' } }, outE2);
  const jE = readJson(join(outE, 'system.json')), jE2 = readJson(join(outE2, 'system.json'));
  const outFA = join(tmp, 'family-anchors'); writeFileSync(outFA + '.line', runSystem(FAMILY_REQ, outFA)); const outFF = join(tmp, 'family-files'); execFileSync(process.execPath, [here + 'families.mjs', '--from', outFA, '--out', outFF], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }); const jFA = readJson(join(outFA, 'system.json')), cssFA = readFileSync(join(outFA, 'system.css'), 'utf8');
  const outP3 = join(tmp, 'p3-anchors'), lineP3 = runSystem(P3_REQ, outP3), jP3 = readJson(join(outP3, 'system.json')), outFFP3 = join(tmp, 'family-files-p3'), outFFP3x = join(tmp, 'family-files-p3-both');
  execFileSync(process.execPath, [here + 'families.mjs', '--from', outFA, '--from-p3', outP3, '--out', outFFP3], { stdio: ['ignore', 'pipe', 'pipe'] }); execFileSync(process.execPath, [here + 'families.mjs', '--from', outP3, '--from-p3', outP3, '--out', outFFP3x], { stdio: ['ignore', 'pipe', 'pipe'] });
  const lineFA = readFileSync(outFA + '.line', 'utf8'), outLow = join(tmp, 'p3-low'), lineLow = runSystem({ ...P3_LOW, p3: 'exact' }, outLow), jLow = readJson(join(outLow, 'system.json'));
  const outHM = join(tmp, 'hover-min'), outHA = join(tmp, 'hover-min-anchored'), outH0 = join(tmp, 'hover-min-unset'); runSystem(HOVER_MIN_REQ, outHM); runSystem(HOVER_MIN_FA, outHA); runSystem({ settings: { hueSet: 'radix' } }, outH0);
  const jHM = readJson(join(outHM, 'system.json')), jHA = readJson(join(outHA, 'system.json')), jH0 = readJson(join(outH0, 'system.json'));
  const outRC = join(tmp, 'radix-compare'); runSystem(RADIX_REQ, outRC); const jRC = readJson(join(outRC, 'system.json')), htmlRC = readFileSync(join(outRC, 'preview.html'), 'utf8');
  const outB = join(tmp, 'brand'), outBL = join(tmp, 'brand-loose'); runSystem(BRAND, outB); runSystem({ ...BRAND, brandExact: false, autoDark: true, extraModes: false }, outBL);
  const jB = readJson(join(outB, 'system.json')), cssB = readFileSync(join(outB, 'system.css'), 'utf8'), jBL = readJson(join(outBL, 'system.json'));
  const jT = readJson(join(outT, 'system.json')), cssT = readFileSync(join(outT, 'system.css'), 'utf8');
  const json1Text = readFileSync(join(out1, 'system.json'), 'utf8');
  if (process.argv.includes('--update-digest')) { writeFileSync(DIGEST, JSON.stringify({ $description: 'sha256 of system.css and system.json for the request {} (check.mjs › byte-identical default). Refresh with check.mjs --update-digest after a deliberate change to the default output.', 'system.css': sha(readFileSync(join(out1, 'system.css'), 'utf8')), 'system.json': sha(json1Text) }, null, 2) + '\n'); console.log('updated ' + DIGEST); }
  const j3 = readJson(join(out3, 'system.json')), j4 = readJson(join(out4, 'system.json')), j5 = readJson(join(out5, 'system.json')), sc3 = readFileSync(join(out3, 'showcase.html'), 'utf8'), sc4 = readFileSync(join(out4, 'showcase.html'), 'utf8'), sc5 = readFileSync(join(out5, 'showcase.html'), 'utf8');
  const TERMS = readJson(here + '../references/terms.json');
  const skillRoot = here + '../', readText = (r) => readFileSync(skillRoot + r, 'utf8');
  const REF_MD = ['SKILL.md', ...readdirSync(skillRoot + 'references').filter((x) => x.endsWith('.md')).map((x) => 'references/' + x)];
  const DOCS = [readText('SKILL.md'), readText('references/system.md')], REFS = REF_MD.map(readText);
  const walk = (d) => readdirSync(skillRoot + d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(d + e.name + '/') : /\.(md|json|mjs|cjs|js|yaml|txt|html)$/.test(e.name) ? [d + e.name] : []));
  const SKILL_FILES = walk('').map((r) => [r, readText(r)]);
  const SYS_SRC = readText('scripts/system.mjs'), KEYS_SRC = JSON.parse(SYS_SRC.match(/const KEYS = (\[[^\]]*\])/)[1].replace(/'/g, '"'));
  const ALLOWED_SRC = JSON.parse(readText('scripts/preset.mjs').match(/const ALLOWED = (\[[^\]]*\])/)[1].replace(/'/g, '"'));
  const outP = join(tmp, 'palette-preset'); execFileSync(process.execPath, [here + 'preset.mjs', '--preset', 'field-operator', '--out', outP], { stdio: ['ignore', 'ignore', 'pipe'] });
  const presetJson = readJson(join(outP, 'palettes.json'));
  const fx = readJson(here + 'system/fixtures/hct-default.json'), j1 = readJson(join(out1, 'system.json')), j2 = readJson(join(out2, 'system.json'));
  const css1 = readFileSync(join(out1, 'system.css'), 'utf8'), css2 = readFileSync(join(out2, 'system.css'), 'utf8'), fg2 = readJson(join(out2, 'figma-variables.json'));
  const FILES1 = ['request.json', 'system.css', 'system.json', 'tokens.dtcg.json', 'preview.html'], FILES2 = [...FILES1, 'figma-variables.json', 'system.base.css', 'system.dim.css', 'system.light-contrast.css', 'system.dark-contrast.css'];
  const cuspN = (j) => { const r = checkCusp(j); return r.n ? r.f : [...r.f, 'no dark-label solid below its cusp to check']; };
  const krWorst = []; const kr = (j) => { const r = checkKeyRun(j); krWorst.push(r.worst); return r.f; };

  console.log('\nChecks');
  const checks = {
    'fixture: raw HCT ramps at the fixture targets (ΔE ≤ 0.1, all steps)': () => checkFixture(fx),
    'placement: unsolved steps at their APCA targets': () => checkPlacement(j1),
    'floors (APCA): solids, hovers, control border, series (default)': () => checkFloors(j1),
    'floors (APCA): solids, hovers, control border, series (light-dark request)': () => checkFloors(j2),
    'floors (APCA): thresholds overridden by the request (apca)': () => checkFloors(j5),
    'apca request key: thresholds as requested, contrast mode +15 or its own': () => { const L = j5.modes.light.apca, C = j5.modes['light-contrast'].apca; return L.solid === 60 && L.hint === 60 && L.text === 45 && C.solid === 75 && C.hint === 75 && C.text === 60 ? [] : [`light ${JSON.stringify(L)}, light-contrast ${JSON.stringify(C)}`]; },
    'apca and brightHues request keys: bad values exit 2': () => checkBadRequests(BAD_REQUESTS),
    'bright hues: default families in the window take the dark label (default)': () => { const M = j1.modes.light, b = j1.families.accents.filter((x) => M.solidLabels[x].brightHue); return b.length ? [] : ['no bright-hue family in the default run']; },
    'bright hues: brightHues false leaves every family white first (light-dark request)': () => (Object.values(j2.modes).some((M) => Object.values(M.solidLabels).some((e) => e.brightHue)) ? ['a brightHue mark with brightHues: false'] : []),
    'solids: white first, kept when passing, every later move recorded (default)': () => checkKeep(j1),
    'solids: white first, kept or moved, as generated (light-dark request)': () => checkKeep(j2),
    'solids: dark-label solids at their hue cusp (default)': () => cuspN(j1),
    'solids: dark-label solids at their hue cusp (light-dark request)': () => cuspN(j2),
    'key run: 9–12 evenly spaced in page Lc, monotonic, text steps clear (default)': () => kr(j1),
    'key run: (light-dark request)': () => kr(j2),
    'key run: around anchors, deviations real and flagged (anchored request)': () => kr(j5),
    'key run: the anchored request has a deviation to check': () => (Object.values(j5.modes).some((M) => Object.values(M.keyRun).some((r) => r.deviations.length)) ? [] : ['no key-run deviation in the anchored request']),
    'files: default outputs exist': () => checkFiles(out1, FILES1),
    'files: light-dark request outputs exist': () => checkFiles(out2, FILES2),
    'css: system.css parses, every var() declared (default)': () => checkCss(css1),
    'css: system.css parses, every var() declared (light-dark)': () => checkCss(css2),
    'css: preview.html stylesheet parses': () => checkCss(/<style>([\s\S]*?)<\/style>/.exec(readFileSync(join(out1, 'preview.html'), 'utf8'))[1], 'preview'),
    'light-dark: color-scheme per block, P3 light-dark complete': () => checkLightDark(css2, j2),
    'split: base + per-mode files cover system.css': () => checkSplit(out2, j2),
    'figma: aliases resolve to their target colour': () => checkFigma(fg2),
    'disabled: neutral fill and faded ink in every mode, reported with no level (default, light-dark, cross)': () => [...checkDisabled(j1, false), ...checkDisabled(j2, false), ...checkDisabled(j6, true)],
    'quiet ink on a solid: a step of the role\'s own family, held to apca.hint against its solid (default, light-dark, anchored, cross)': () => [...checkSolidMuted(j1), ...checkSolidMuted(j2), ...checkSolidMuted(j5), ...checkSolidMuted(j6)],
    'inverse: the pair follows each endpoint the request names, and neutral 12 and 1 otherwise (default, pure, white only, cross)': () => [...checkInverse(j1), ...checkInverse(jE), ...checkInverse(jE2), ...checkInverse(j6)],
    'endpoints: by default white and black sit past every step and short of pure (default, light-dark, cross, tinted)': () => [...checkEndpoints(j1), ...checkEndpoints(j2), ...checkEndpoints(j6), ...checkEndpoints(j7)],
    'terms: concepts complete and linked, roles catalogued both ways (default, light-dark, cross, tinted)': () => checkTerms(TERMS, [j1, j2, j6, j7]),
    'terms: every concept used under its term or alias, no avoided phrase, every concrete name emitted': () => checkTermsInDocs(TERMS, DOCS, REFS, [j1, j2, j6, j7]),
    'invariants: no host-project name anywhere in the skill': () => checkNames(SKILL_FILES),
    'entry: every relative link in SKILL.md and the references resolves; SKILL.md under 18,000 characters': () => checkEntry(REF_MD.map((r) => [r, readText(r)]), (p) => existsSync(skillRoot + p)),
    'invariants: Display P3 by default (system and palette preset)': () => checkTargets(j1, presetJson),
    'closure: request keys in system.mjs and system.md match; preset.mjs keys documented': () => checkKeyClosure(KEYS_SRC, DOCS[1], ALLOWED_SRC, readText('references/requests.md')),
    'generated: no color-mix(), calc() or relative colour in any CSS file or JSON variable (all runs)': () => [...checkGenerated([['default', css1], ['light-dark', css2], ['tinted', readFileSync(join(out7, 'system.css'), 'utf8')], ...['system.base.css', 'system.light.css', 'system.dark.css'].filter((x) => existsSync(join(out7, x))).map((x) => ['tinted ' + x, readFileSync(join(out7, x), 'utf8')])]), ...[[j1, 'default'], [j2, 'light-dark'], [j6, 'cross'], [j7, 'tinted'], [j8, 'anchored']].flatMap(([j, nm]) => checkGeneratedJson(j, nm))],
    'selection: emphasis 1 lands on steps as aliases (default, cross)': () => [...checkSelection(j1, 1, false), ...checkSelection(j6, 1, true)],
    'selection: emphasis 1.5 is the generated mix in light and in dark (tinted)': () => checkSelection(j7, 1.5, true),
    'contrast (APCA): matrix recomputed from ramps (default)': () => checkContrast(j1),
    'contrast (APCA): matrix recomputed from ramps (light-dark)': () => checkContrast(j2),
    'contrast (APCA): matrix at overridden thresholds (anchored request)': () => checkContrast(j5),
    'series CVD: present, unsimulated minimum recomputed': () => checkCvd(j1),
    'tonal: agreement diagnostics and tonalMap': () => checkTonal(j1),
    'showcase: written only when requested': () => (existsSync(join(out1, 'showcase.html')) ? ['showcase.html written without showcase: true'] : []),
    'showcase: default (24 specimens, annotation, flags, panels, colours)': () => checkShowcase(out3, j3),
    'showcase: light-dark request': () => checkShowcase(out2, j2),
    'showcase: scoped attribute sRGB request with failing anchors': () => checkShowcase(out4, j4),
    'showcase: APCA-override anchored request': () => checkShowcase(out5, j5),
    'neutrals: default run byte-identical to the recorded digest (system.css, system.json)': () => checkDigest(css1, json1Text),
    'neutrals: default run has no split families, roles or fields': () => checkNoSplit(j1),
    'neutrals: roles mapped to ground / surface / ink, gray an alias of ink (cross, tinted, anchored)': () => [...checkNeutralRoles(j6), ...checkNeutralRoles(j7), ...checkNeutralRoles(j8)],
    'neutrals: families regenerated from their specs, surface lifted, cross swaps in dark (cross, tinted)': () => [...checkNeutralSources(j6), ...checkNeutralSources(j7)],
    'neutrals: cross run takes Slate for the dark page and Sand for the dark cards': () => { const f = [], d = j6.modes.dark, l = j6.modes.light; if (!/Slate/.test(d.neutralSources.ground.source) || !/Sand/.test(d.neutralSources.surface.source) || !/Sand/.test(l.neutralSources.ground.source)) f.push('neutralSources do not show the cross'); return f; },
    'pressed solid: step 11 where the label holds, else one step back, never under apca.ui (default, light-dark, anchored, cross, tinted)': () => [...checkActive(j1), ...checkActive(j2), ...checkActive(j5), ...checkActive(j6), ...checkActive(j7)],
    'hover steps: each rest → hover ΔE recomputed, threshold 4, summary (default, light-dark, anchored, cross, tinted)': () => [...checkHover(j1), ...checkHover(j2), ...checkHover(j5), ...checkHover(j6), ...checkHover(j7)],
    'neutrals: separation recomputed (all runs)': () => [...checkSeparation(j6), ...checkSeparation(j7), ...checkSeparation(j8)],
    'neutrals: surface separates from ground in every mode (cross, tinted)': () => [...allSeparate(j6), ...allSeparate(j7)],
    'neutrals: the anchored run has a separation miss to flag': () => (allSeparate(j8).length ? [] : ['no separation miss in the anchored neutrals run']),
    'neutrals: ground, ink and surface anchors pin their families': () => checkNeutralAnchors(j8),
    'neutrals: floors with the split labels and control border (cross, tinted, anchored)': () => [...checkFloors(j6), ...checkFloors(j7), ...checkFloors(j8)],
    'neutrals: key run (cross)': () => kr(j6),
    'neutrals: contrast matrix recomputed, ink on ground 1–2 and surface 1–3 (cross, tinted)': () => [...checkContrast(j6), ...checkContrast(j7), ...['fg', 'fg-muted', 'fg-subtle'].flatMap((fg) => ['bg', 'bg-subtle', 'surface', 'surface-subtle', 'surface-muted'].filter((bg) => !j6.modes.light.contrast.pairs.some((p) => p.fg === fg && p.bg === bg)).map((bg) => `no ${fg} on ${bg} pair`)), ...['bg', 'bg-subtle', 'surface', 'surface-subtle'].filter((bg) => !j6.modes.dark.contrast.pairs.some((p) => p.fg === 'control-border' && p.bg === bg)).map((bg) => `no control-border on ${bg} pair`)],
    'neutrals: css, light-dark, split and Figma (tinted)': () => [...checkCss(readFileSync(join(out7, 'system.css'), 'utf8')), ...checkLightDark(readFileSync(join(out7, 'system.css'), 'utf8'), j7), ...checkSplit(out7, j7), ...checkFigma(readJson(join(out7, 'figma-variables.json')))],
    'neutrals: preview shows the three families': () => { const h = readFileSync(join(out6, 'preview.html'), 'utf8'); return ['ground', 'surface', 'ink'].filter((x) => !h.includes(`var(--colors-${x}-12)`)).map((x) => 'preview lacks the ' + x + ' strip'); },
    'neutrals: showcase (24 specimens, flags incl. separation, panels, colours) and its Neutral & surfaces group': () => [...checkShowcase(out6, j6), ...checkShowcase(out8, j8), ...checkShowcaseNeutrals(sc6, j6), ...checkShowcaseNeutrals(sc8, j8)],
    'neutrals: bad values exit 2': () => checkBadRequests(BAD_NEUTRALS),
    'translucent: requested roles emitted in every mode at the requested alpha and base; none without the key': () => checkTranslucent(jT, cssT, TR.translucent, j1),
    'translucent: bad values exit 2': () => checkBadRequests(BAD_TRANSLUCENT),
    'brand colours: accents exact at step 9 in every mode (brandExact), no auto-dark block, no data roles, a renamed family, anchored families off the cusp': () => checkBrand(jB, cssB, jBL),
    'brand colours: bad roles, anchor steps, autoDark and familyNames exit 2': () => checkBadRequests(BAD_BRAND),
    'hoverMin 4: every family\'s step 9 to 10 ΔE ≥ 4 in every mode (Radix hues, alone and with the 25 Radix step 9s pinned)': () => [...checkHoverMin(jHM, 4), ...checkHoverMin(jHA, 4)],
    'hoverMin 4: floors and key run hold with the moved hovers (Radix hues, alone and pinned)': () => [...checkFloors(jHM), ...checkFloors(jHA), ...kr(jHM), ...kr(jHA)],
    'hoverMin: negative, non-number and out-of-range values exit 2': () => checkBadRequests(BAD_HOVER_MIN),
    'family anchors: exact at step 9 in every scheme, roles untouched, no internal names in the output': () => checkFamilyAnchors(jFA, cssFA),
    'family files: every variable resolves in both schemes, step 9 exact to the system, manifest hashes current (families.mjs)': () => checkFamilyFiles(outFF, jFA),
    'family anchors and role names: unknown roles, unknown families, a family a role anchor pins and bad keys exit 2': () => checkBadRequests(BAD_FAMILY),
    'P3 anchors: "edge" family anchors keep lightness and hue, saturated ones outside sRGB, muted ones scaled, requested and lifted in anchorReport': () => checkP3Anchors(jP3),
    'P3 usage: counts recounted from the ramps, the effectively-sRGB warning on exactly the modes under 5% (P3 anchors, family anchors, low chroma)': () => [...checkP3Usage(jP3, lineP3), ...checkP3Usage(jFA, lineFA, Object.fromEntries(Object.entries(jFA.modes).map(([id, M]) => [id, usageCount(M)]))), ...checkP3Usage(jLow, lineLow)],
    'P3 usage: the low-chroma run has a mode to warn about': () => (/^WARNING effectively sRGB/m.test(lineLow) ? [] : ['no effectively-sRGB warning in the low-chroma run']),
    'P3 usage: in system.json only when the request names p3 (default, family anchors)': () => [...checkNoP3Usage(j1), ...checkNoP3Usage(jFA)],
    'P3 option: bad values exit 2': () => checkBadRequests(BAD_P3),
    'family files: --from-p3 lays colors-p3/ out from the P3 run and colors/ from the sRGB run; manifest and README carry the P3 usage': () => [...checkFamilyFiles(outFFP3, jP3), ...checkFromP3(outFFP3, jFA, jP3), ...checkP3Usage(jFA, null, readJson(join(outFF, 'manifest.json')).p3Usage).map((x) => 'manifest without --from-p3: ' + x), ...[outFF, outFFP3].filter((d) => !/ramp swatches/.test(readFileSync(join(d, 'README.md'), 'utf8'))).map((d) => `${d}: README.md does not state the P3 usage`)],
    'radix data: 31 scales × 8 variants × 12 steps, the package version and tarball sha256 named, the scales at their recorded hash': () => checkRadixData(RADIX),
    'compare radix: every Radix-named family compared in every mode (ΔE, ΔL recomputed), a familyAnchors step-9 pin at ΔE 0, the preview column; none without the key': () => [...checkRadixCompare(jRC, Object.keys(RADIX_PIN), j1, readFileSync(join(out1, 'preview.html'), 'utf8')), ...(htmlRC.match(/class="rdx"/g) || []).length === 2 * jRC.families.all.length ? [] : ['the preview lacks a Radix column on some family row']],
    'compare: values other than "radix" exit 2': () => checkBadRequests(BAD_COMPARE),
    'showcase: the runs have anchor, APCA-miss and key-run flags to check': () => (/data-flag="anchor-order"/.test(sc4) && /data-flag="anchor-clip"/.test(sc4) && /data-flag="lc-miss"/.test(sc5) && /data-flag="keyrun"/.test(sc5) ? [] : ['a showcase run lacks the failures the controls need']),
  };
  for (const [name, fn] of Object.entries(checks)) record(name, fn());
  console.log(`  (key run: largest distance from even spacing ${Math.max(...krWorst).toFixed(3)} Lc, tolerance ${KEYRUN_TOL})`);

  // Negative controls: a mutated copy must fail its check. A control that passes means the check doesn't bite.
  console.log('\nNegative controls (each must FAIL)');
  const bites = [];
  const control = (name, fn) => { let f; try { f = fn(); } catch (e) { f = ['threw: ' + e.message]; } const ok = f.length > 0; bites.push({ name, ok }); console.log(`${ok ? 'bites' : 'DOES NOT BITE'}  ${name}${ok ? ' — ' + f[0] : ''}`); };
  const clone = (x) => structuredClone(x);
  const labelFam = (M, lbl, extra = () => true) => Object.keys(M.solidLabels).find((k) => M.solidLabels[k].label === lbl && extra(M.solidLabels[k], k));
  control('fixture with one step moved by ΔL 0.02', () => { const x = clone(fx); x.light.indigo[5] = x.light.indigo[5].replace(/oklch\(([\d.]+)/, (_, L) => 'oklch(' + (+L + 0.02)); return checkFixture(x); });
  control('a step 4 pushed off its target', () => { const x = clone(j1); x.modes.light.ramps.cyan[3].oklch[0] -= 0.05; return checkPlacement(x); });
  control('a solid lightened to L 0.75', () => { const x = clone(j1); x.modes.light.ramps.indigo[8].oklch[0] = 0.75; return checkFloors(x); });
  control('a contrast-mode solid at Lc 55 against its own label', () => { const x = clone(j2); const M = x.modes['light-contrast'], e = M.solidLabels.cyan, lbl = labelsOf(x)[e.label], s = M.ramps.cyan[8].oklch, dir = e.label === 'dark' ? -1 : 1; let L = s[0]; while (lcOk([L, s[1], s[2]], lbl) > 55) L += dir * 0.005; s[0] = L; return checkFloors(x); });
  control('a disabled ink left on a toned step', () => { const x = clone(j1); x.modes.light.variables['--colors-fg-disabled'] = 'var(--colors-primary-8)'; return checkDisabled(x, false); });
  control('a disabled pair held to a threshold', () => { const x = clone(j1); x.modes.dark.contrast.pairs.push({ fg: 'fg-disabled', bg: 'bg-disabled', intent: 'text', lc: 30, threshold: 45, pass: false, ratio: 2 }); return checkDisabled(x, false); });
  control('a quiet on-solid ink taken from the page', () => { const x = clone(j1); x.modes.light.variables['--colors-primary-on-solid-muted'] = 'var(--colors-fg-muted)'; return checkSolidMuted(x); });
  control('a quiet on-solid ink dropped from the matrix', () => { const x = clone(j1); x.modes.dark.contrast.pairs = x.modes.dark.contrast.pairs.filter((p) => p.fg !== 'critical-on-solid-muted'); return checkSolidMuted(x); });
  control('a pure-white request whose dark inverse stays on step 12', () => { const x = clone(jE); x.modes.dark.variables['--colors-bg-inverse'] = 'var(--colors-gray-12)'; return checkInverse(x); });
  control('a default inverse moved onto an endpoint', () => { const x = clone(j1); x.modes.light.variables['--colors-bg-inverse'] = 'var(--colors-black)'; return checkInverse(x); });
  control('a default white left on a ramp step', () => { const x = clone(j1); x.modes.light.variables['--colors-white'] = x.modes.light.variables['--colors-gray-3']; return checkEndpoints(x); });
  control('a default black left on a ramp step', () => { const x = clone(j1); x.modes.dark.variables['--colors-black'] = x.modes.dark.variables['--colors-gray-3']; return checkEndpoints(x); });
  control('a Display P3 miss left out of the summary', () => { const x = clone(j1); const p = x.modes.dark.contrast.pairs[0]; p.lcP3 = 1; p.passP3 = false; return checkContrast(x); });
  control('a P3 measurement in an sRGB-only system', () => { const x = clone(j4); x.modes.light.contrast.pairs[0].lcP3 = 50; return checkContrast(x); });
  control('a hover under the floor', () => { const x = clone(j1); const s = x.modes.dark.ramps.indigo[9].oklch; s[0] += 0.08; return checkFloors(x); });
  control('a dark-label solid claimed for the light label', () => { const x = clone(j2); const M = x.modes['dark-contrast'], fam = labelFam(M, 'dark'); M.solidLabels[fam].label = 'light'; return checkFloors(x); });
  control('a role labelled with the other label', () => { const x = clone(j1); const M = x.modes.light; M.variables['--colors-primary-on-solid'] = x.labelColors.dark.css; return checkFloors(x); });
  control('the request\'s apca solid raised to 75 (floors read the request)', () => { const x = clone(j5); x.request.apca.solid = 75; x.modes.light.apca.solid = 75; return checkFloors(x); });
  control('a control border under apca.ui', () => { const x = clone(j1); x.modes.light.ramps.gray[7].oklch = [...x.modes.light.ramps.gray[1].oklch]; return checkFloors(x); });
  control('a valid apca value in the bad list', () => checkBadRequests([{ apca: { solid: 50 } }]));
  control('a brand accent off its anchor in the dark section', () => { const x = clone(jB); const r = x.modes['on-dark'].anchorReport.find((a) => a.role === 'primary'); x.modes['on-dark'].ramps[r.family][8].oklch[0] -= 0.05; return checkBrand(x, cssB, jBL); });
  control('an auto-dark block written with autoDark false', () => checkBrand(jB, cssB + '\n@media (prefers-color-scheme: dark) { :root { color-scheme: dark; } }', jBL));
  control('a renamed family emitted under its hue name', () => checkBrand(jB, cssB + '\n:root { --colors-indigo-9: red; }', jBL));
  control('a data role written with series false', () => checkBrand(jB, cssB + '\n:root { --colors-data-1: red; }', jBL));
  control('an anchored family moved to its cusp', () => { const x = clone(jBL); const r = x.modes.dark.anchorReport.find((a) => a.role === 'secondary'); x.modes.dark.solidLabels[r.family].cusp = true; return checkBrand(jB, cssB, x); });
  control('a family file with a missing reference', () => { const v = familyVars(join(outFF, 'colors-p3')); delete v['--colors-indigo-9']; return checkFamilyFiles(outFF, jFA, { 'colors-p3': v, colors: familyVars(join(outFF, 'colors')) }); });
  control('a family file with a moved step 9', () => { const v = familyVars(join(outFF, 'colors-p3')); v['--colors-orange-9'] = 'oklch(0.6 0.19 45)'; return checkFamilyFiles(outFF, jFA, { 'colors-p3': v, colors: familyVars(join(outFF, 'colors')) }); });
  control('a family anchor off its step 9', () => { const x = clone(jFA); x.modes.light.ramps.orange[8].oklch[0] -= 0.05; return checkFamilyAnchors(x, cssFA); });
  control('a family anchor that moved a role', () => { const x = clone(jFA); x.modes.dark.roles.primary = 'orange'; return checkFamilyAnchors(x, cssFA); });
  control('an internal family: role in the output', () => checkFamilyAnchors(jFA, cssFA + '\n--colors-family:orange-solid: red;'));
  control('a valid family anchor in the bad list', () => checkBadRequests([{ settings: { hueSet: 'radix' }, familyAnchors: { orange: { value: '#f76b15' } } }]));
  control('a P3 usage count that does not match the ramps', () => { const x = clone(jP3); x.modes.dark.p3Usage.outsideSrgb += 1; return checkP3Usage(x, lineP3); });
  control('an "edge" anchor that stayed inside sRGB', () => { const x = clone(jP3); const c = x.modes.light.ramps.orange[8].oklch; c[1] = clampChroma(c[0], c[1], c[2], 'srgb'); return checkP3Anchors(x); });
  control('a valid p3 value in the bad list', () => checkBadRequests([{ p3: 'relative' }]));
  control('the effectively-sRGB warning dropped from the CLI', () => checkP3Usage(jLow, lineLow.replace(/^WARNING effectively sRGB.*$/m, '')));
  control('a p3Usage written without a p3 key', () => { const x = clone(j1); x.modes.light.p3Usage = usageCount(x.modes.light); return checkNoP3Usage(x); });
  control('colors/ laid out from the P3 run', () => checkFromP3(outFFP3x, jFA, jP3));
  control('a valid role hue in the bad list', () => checkBadRequests([{ roles: { primary: 'h85.5' } }, { roles: { primary: 'oklch:84' } }]));
  control('a requested translucent role at another alpha', () => { const x = clone(jT); x.modes.dark.variables['--colors-veil-a'] = x.modes.dark.variables['--colors-veil-a'].replace(/\/ [\d.]+\)$/, '/ 0.5)'); return checkTranslucent(x, cssT, TR.translucent, j1); });
  control('a requested translucent role missing from one mode', () => { const x = clone(jT); delete x.modes.dim.variables['--colors-veil-b']; return checkTranslucent(x, cssT, TR.translucent, j1); });
  control('a requested translucent role on another base', () => { const x = clone(jT); x.modes.light.variables['--colors-neutral-12'] = 'oklch(0.9 0 0)'; return checkTranslucent(x, cssT, TR.translucent, j1); });
  control('a system without the key that reports translucent roles', () => { const x = clone(j1); x.modes.light.translucent = {}; return checkTranslucent(jT, cssT, TR.translucent, x); });
  control('a valid translucent request in the bad list', () => checkBadRequests([{ translucent: { ok: { of: 'bg', alpha: 0.5 } } }]));
  control('a concept whose term the docs never use', () => { const x = clone(TERMS); x.concepts.push({ id: 'zebra', term: 'Zebra stripe', layer: 'system', definition: 'x', intent: 'x' }); return checkTermsInDocs(x, DOCS, REFS, [j1]); });
  control('an avoided phrase planted in SKILL.md', () => checkTermsInDocs(TERMS, DOCS, [REFS[0] + '\nThe tonal layer stays put.'], [j1, j2, j6, j7]));
  control('a concept naming a variable no run emits', () => { const x = clone(TERMS); x.concepts.find((c) => c.id === 'backdrop').names.push('--colors-bg-veil'); return checkTermsInDocs(x, DOCS, REFS, [j1, j2, j6, j7]); });
  control('a host-project name in a reference', () => checkNames([['references/x.md', 'Made for ' + FORBIDDEN[0].toUpperCase() + ' UI.']]));
  control('a link to a file the skill does not ship', () => checkEntry([['references/x.md', 'See [the contract](../recipes/NOPE.md).']], (p) => existsSync(skillRoot + p)));
  control('a SKILL.md of 18,000 characters', () => checkEntry([['SKILL.md', 'x'.repeat(18000)]], (p) => existsSync(skillRoot + p)));
  control('a description that is not a plain YAML scalar', () => checkEntry([['SKILL.md', '---\nname: x\ndescription: Generate HCT color: source palettes\n---\n']], (p) => existsSync(skillRoot + p)));
  control('a default system targeting sRGB', () => { const x = clone(j1); x.target = 'srgb'; return checkTargets(x, presetJson); });
  control('a palette preset targeting sRGB', () => checkTargets(j1, { request: { target: 'srgb' } }));
  control('a request key system.mjs accepts but system.md omits', () => checkKeyClosure([...KEYS_SRC, 'bogusKey'], DOCS[1], ALLOWED_SRC, readText('references/requests.md')));
  control('a documented request key system.mjs rejects', () => checkKeyClosure(KEYS_SRC.filter((k) => k !== 'emphasis'), DOCS[1], ALLOWED_SRC, readText('references/requests.md')));
  control('a preset.mjs key requests.md does not document', () => checkKeyClosure(KEYS_SRC, DOCS[1], [...ALLOWED_SRC, 'zebraKey'], readText('references/requests.md')));
  control('a role dropped from the terms catalogue', () => { const x = clone(TERMS); delete x.roles.page['bg-overlay']; return checkTerms(x, [j1, j2, j6, j7]); });
  control('a catalogued role no run emits', () => { const x = clone(TERMS); x.roles.page['bg-brand'] = 'brand'; return checkTerms(x, [j1, j2, j6, j7]); });
  control('a concept related to an unknown term', () => { const x = clone(TERMS); x.concepts[0].related.push('accent-colour'); return checkTerms(x, [j1]); });
  control('a concept without an intent', () => { const x = clone(TERMS); delete x.concepts.find((c) => c.id === 'surface').intent; return checkTerms(x, [j1]); });
  control('a color-mix() left in system.css', () => checkGenerated([['default', css1.replace(/(--colors-bg-control: )[^;]+/, '$1color-mix(in oklch, var(--colors-gray-12) 12%, transparent)')]]));
  control('a calc() alpha in the JSON variables', () => { const x = clone(j7); x.modes.light.variables['--colors-shadow'] = 'oklch(0.3 0 0 / calc(0.14 * 1))'; return checkGeneratedJson(x, 'tinted'); });
  control('the emphasis mix moved toward the primary', () => { const x = clone(j7); x.modes.light.variables['--colors-bg-selected'] = x.modes.light.variables['--colors-primary-3'] || 'oklch(0.9 0.05 270)'; return checkSelection(x, 1.5, true); });
  control('a dark single selection left on the primary solid', () => { const x = clone(j1); x.modes.dark.variables['--colors-bg-selected'] = 'var(--colors-primary-solid)'; return checkSelection(x, 1, false); });
  control('the multiple-selection tint left under apca.ui', () => { const x = clone(j2); x.modes['dark-contrast'].variables['--colors-bg-selected-multiple'] = 'var(--colors-neutral-5)'; return checkSelection(x, 1, false); });
  control('emphasis 1 written as a colour instead of an alias', () => { const x = clone(j1); x.modes.light.variables['--colors-bg-selected'] = 'oklch(0.99 0 0)'; return checkSelection(x, 1, false); });
  control('a translucent split role pointing at the wrong step', () => { const x = clone(j6); const V = x.modes.light.variables; V['--colors-bg-control'] = resolveVar(V, 'var(--colors-surface-6)').replace(/\)$/, ' / 0.12)'); return checkNeutralRoles(x); });
  control('a valid emphasis value in the bad list', () => checkBadRequests([{ emphasis: 1.5 }]));
  control('a valid brightHues value in the bad list', () => checkBadRequests([{ brightHues: [80, 110] }]));
  control('a bright-hue family on the light label', () => { const x = clone(j1); const M = x.modes.light, fam = Object.keys(M.solidLabels).find((k) => M.solidLabels[k].brightHue); M.solidLabels[fam].label = 'light'; return checkKeep(x); });
  control('a family outside the window marked bright', () => { const x = clone(j1); const M = x.modes.light; M.solidLabels.indigo.brightHue = true; return checkKeep(x); });
  control('the bright-hue window ignored (brightHues false read as default)', () => { const x = clone(j2); delete x.request.brightHues; return checkKeep(x); });
  control('white first broken: a white-passing solid given the dark label', () => { const x = clone(j1); const M = x.modes.light, fam = labelFam(M, 'light'); M.solidLabels[fam].label = 'dark'; return checkKeep(x); });
  control('white rejected without cause', () => { const x = clone(j1); const M = x.modes.dark, fam = labelFam(M, 'light'); M.solidLabels[fam].whiteRejected = { lc9OnPage: 0, floor: 15 }; return checkKeep(x); });
  control('a white-rejected solid back on the light label', () => { const x = clone(j1); const M = x.modes['dark-contrast'], fam = labelFam(M, 'dark', (e) => e.whiteRejected); M.solidLabels[fam].label = 'light'; delete M.solidLabels[fam].whiteRejected; return checkKeep(x); });
  control('a passing generated solid moved anyway', () => { const x = clone(j1); const M = x.modes.light, fam = labelFam(M, 'light', (e) => e.moved === 0 && !e.hoverRoom); M.ramps[fam][8].oklch[0] += 0.03; return checkKeep(x); });
  control('a failing generated solid reported kept', () => { const x = clone(j1); const M = x.modes['dark-contrast'], fam = Object.keys(M.solidLabels).find((k) => M.solidLabels[k].moved !== 0); M.solidLabels[fam].moved = 0; return checkKeep(x); });
  control('a hover room larger than needed', () => { const x = clone(j1); const M = x.modes.dark, fam = labelFam(M, 'light', (e) => e.hoverRoom); M.ramps[fam][9].oklch[0] -= 0.04; return checkKeep(x); });
  control('a cusp solid pulled back toward the floor', () => { const x = clone(j1); const M = x.modes['dark-contrast'], fam = labelFam(M, 'dark', (e) => e.cusp); M.ramps[fam][8].oklch[0] -= 0.05; return checkCusp(x).f; });
  control('a cusp solid with its hue rotated', () => { const x = clone(j1); const M = x.modes['dark-contrast'], fam = labelFam(M, 'dark', (e) => e.cusp); M.ramps[fam][8].oklch[2] += 6; return checkCusp(x).f; });
  control('a dark-label solid not taken to its cusp', () => { const x = clone(j1); const M = x.modes['dark-contrast'], fam = labelFam(M, 'dark', (e) => e.cusp); delete M.solidLabels[fam].cusp; return checkCusp(x).f; });
  control('key run: step 10 off even spacing', () => { const x = clone(j1); x.modes.light.ramps.indigo[9].oklch[0] += 0.02; return checkKeyRun(x).f; });
  control('key run: step 11 off even spacing (dark)', () => { const x = clone(j1); x.modes.dark.ramps.yellow[10].oklch[0] -= 0.02; return checkKeyRun(x).f; });
  control('key run: step 12 collapsed onto step 11', () => { const x = clone(j1); const r = x.modes.light.ramps.teal; r[11].oklch = [...r[10].oklch]; r[11].oklch[0] += 0.01; return checkKeyRun(x).f; });
  control('key run: a deviation dropped from system.json', () => { const x = clone(j5); for (const M of Object.values(x.modes)) for (const r of Object.values(M.keyRun)) r.deviations = []; return checkKeyRun(x).f; });
  control('key run: keyRun.lc misreported', () => { const x = clone(j1); x.modes.dim.keyRun.plum.lc[2] += 1; return checkKeyRun(x).f; });
  control('a series colour at Lc 10 on the surface', () => { const x = clone(j1); x.modes.dark.series[2].oklch = [...x.modes.dark.ramps.gray[2].oklch]; return checkFloors(x); });
  control('preview.html deleted', () => { const d = join(tmp, 'neg-files'); cpSync(out1, d, { recursive: true }); unlinkSync(join(d, 'preview.html')); return checkFiles(d, FILES1); });
  control('system.css missing its last }', () => checkCss(css1.replace(/\}\s*$/, '')));
  control('system.css with a declaration renamed', () => checkCss(css1.replace(/--colors-gray-12:/g, '--colors-grey-12:')));
  control('an extra mode block without its color-scheme', () => checkLightDark(css2.replace(/\.dim \{\n  color-scheme: dark;/, '.dim {\n  color-scheme: light;'), j2));
  control('the P3 light-dark block missing a wide-gamut variable', () => { const at = css2.indexOf('@media (color-gamut: p3)'), V = j2.modes.light.variables;
    const k = Object.keys(V).find((x) => [...String(V[x]).matchAll(/oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)/g)].some((m) => clampChroma(+m[1], +m[2], +m[3], 'srgb') < +m[2] - 1e-3));
    return checkLightDark(css2.slice(0, at) + css2.slice(at).replace(new RegExp('\\n  ' + k + ': [^\\n]*'), ''), j2); });
  control('a split mode file missing a role variable', () => { const d = join(tmp, 'neg-split'); cpSync(out2, d, { recursive: true }); const p = join(d, 'system.dim.css'); writeFileSync(p, readFileSync(p, 'utf8').replace(/\n  --colors-primary-solid: [^\n]*/g, '')); return checkSplit(d, j2); });
  control('a Figma alias pointed at the wrong step', () => { const x = clone(fg2); const v = x.collections[0].variables.find((y) => y.valuesByMode.light?.type === 'VARIABLE_ALIAS'); v.valuesByMode.light.id = v.valuesByMode.light.id.replace(/\/(\d+)$/, (_, n) => '/' + (n === '1' ? 2 : 1)); return checkFigma(x); });
  control('an APCA Lc misreported', () => { const x = clone(j1); x.modes.light.contrast.pairs[0].lc += 1; return checkContrast(x); });
  control('a pair passed under its threshold', () => { const x = clone(j5); const M = Object.values(x.modes).find((m) => m.contrast.pairs.some((q) => !q.pass)), p = M.contrast.pairs.find((q) => !q.pass); p.pass = true; M.contrast.summary.fail--; return checkContrast(x); });
  control('a matrix threshold not the request\'s', () => { const x = clone(j5); x.modes.light.contrast.pairs.find((q) => q.intent === 'hint').threshold = 30; return checkContrast(x); });
  control('a series CVD minimum misreported', () => { const x = clone(j1); x.modes.light.seriesCvd.normal.minDE += 3; return checkCvd(x); });
  control('tonalMap missing a role', () => { const x = clone(j1); delete x.modes.dark.tonalMap.info; return checkTonal(x); });
  const scCopy = (name, html) => { const d = join(tmp, name); cpSync(out3, d, { recursive: true }); if (html == null) unlinkSync(join(d, 'showcase.html')); else writeFileSync(join(d, 'showcase.html'), html); return d; };
  control('showcase.html deleted', () => checkShowcase(scCopy('neg-sc-file', null), j3));
  control('a showcase specimen dropped', () => checkShowcaseShape(sc3.replace('data-specimen="gamut"', 'data-dropped="gamut"')));
  control('a showcase group with a fourth specimen', () => checkShowcaseShape(sc3.replace('data-specimen="scrim"', 'data-specimen="scrim"></figure><figure data-specimen="extra"')));
  control('an annotated Lc misreported', () => checkShowcaseAnnotation(sc3.replace(/(data-annot="lc" data-step="4" data-lc=")([\d.]+)/, (_, a, v) => a + (+v + 1)), j3));
  control('an annotated target misreported', () => checkShowcaseAnnotation(sc3.replace(/(data-step="6" data-lc="[\d.]+" data-target=")([\d.]+)/, (_, a, v) => a + (+v + 2)), j3));
  control('the solid Lc misreported', () => checkShowcaseAnnotation(sc3.replace(/(data-annot="solid-lc" data-step="\d+" data-value=")([\d.]+)/, (_, a, v) => a + (+v + 0.5)), j3));
  control('the solid floor misreported', () => checkShowcaseAnnotation(sc3.replace(/(data-annot="solid-lc"[^>]*data-floor=")([\d.]+)/, (_, a, v) => a + (+v + 15)), j3));
  control('the key-run annotation misreported', () => checkShowcaseAnnotation(sc3.replace(/(data-annot="keyrun" data-lc=")([\d.]+)/, (_, a, v) => a + (+v + 2)), j3));
  control('an APCA-miss flag removed', () => checkShowcaseFlags(sc5.replace(/<span class="sc-flag" data-flag="lc-miss"[^>]*>[^<]*<\/span>/, ''), j5));
  control('a key-run deviation flag removed', () => checkShowcaseFlags(sc5.replace(/<span class="sc-flag" data-flag="keyrun"[^>]*>[^<]*<\/span>/, ''), j5));
  // The default series clear the CVD threshold in every mode but one, so this control makes system.json report a weak one the sheet doesn't flag.
  control('a weak series in system.json, not flagged', () => { const x = clone(j3); x.modes.dark.seriesCvd.protan.minDE = x.modes.dark.seriesCvd.threshold - 3; return checkShowcaseFlags(sc3, x); });
  control('an out-of-order anchor flag removed', () => checkShowcaseFlags(sc4.replace(/<span class="sc-flag" data-flag="anchor-order"[^>]*>[^<]*<\/span>/, ''), j4));
  control('an anchor reported in order in system.json but flagged', () => { const x = clone(j4); for (const M of Object.values(x.modes)) for (const a of M.anchorReport) a.inOrder = true; return checkShowcaseFlags(sc4, x); });
  control('the dark panel without its forced class', () => checkShowcaseColours(sc3.replace(/class="sc-panel ([^"]*) dark" data-mode-panel="dark"/, 'class="sc-panel $1" data-mode-panel="dark"'), j3, readFileSync(join(out3, 'system.css'), 'utf8')));
  control('a scoped panel without its mode attribute', () => checkShowcaseColours(sc4.replace(/ data-color-mode="dark" data-mode-panel="dark"/, ' data-mode-panel="dark"'), j4, readFileSync(join(out4, 'system.css'), 'utf8')));
  control('a hand-picked colour in a specimen', () => checkShowcaseColours(sc3.replace('<span class="sc-bar" style="height:62%;background:', '<span class="sc-bar" style="height:62%;background:#ff00ff;x:'), j3, readFileSync(join(out3, 'system.css'), 'utf8')));
  control('a colour literal in the sheet CSS', () => checkShowcaseColours(sc3.replace('.sc-group h2{', '.sc-group h2{color:#333;'), j3, readFileSync(join(out3, 'system.css'), 'utf8')));

  // Neutrals split.
  control('the default output changed by one byte', () => checkDigest(css1.replace(/;\n}/, ' ;\n}'), json1Text));
  control('a split variable in the default run', () => { const x = clone(j1); x.modes.light.variables['--colors-surface'] = 'var(--colors-gray-1)'; return checkNoSplit(x); });
  control('border read from the ground instead of the surface', () => { const x = clone(j6); x.modes.dark.variables['--colors-border'] = 'var(--colors-ground-6)'; return checkNeutralRoles(x); });
  control('fg left on the one neutral', () => { const x = clone(j7); x.modes.light.variables['--colors-fg'] = 'var(--colors-gray-12)'; return checkNeutralRoles(x); });
  control('gray no longer an alias of ink', () => { const x = clone(j6); x.modes.light.variables['--colors-gray-5'] = x.modes.light.variables['--colors-ink-5']; return checkNeutralRoles(x); });
  control('cross ignored: dark ground and surface swapped back', () => { const x = clone(j6); const M = x.modes.dark; [M.ramps.ground, M.ramps.surface] = [M.ramps.surface, M.ramps.ground]; return checkNeutralSources(x); });
  control('surface not lifted off the page', () => { const x = clone(j7); x.modes.light.ramps.surface = clone(x.modes.light.ramps.ground); return checkNeutralSources(x); });
  control('cross read as off (request without cross)', () => { const x = clone(j6); delete x.request.neutrals.cross; return checkNeutralSources(x); });
  control('a dark overlay left one step above the card', () => { const x = clone(j6); x.modes.dark.variables['--colors-bg-overlay'] = 'var(--colors-surface-2)'; return checkNeutralRoles(x); });
  control('a layer of the stack misreported', () => { const x = clone(j6); x.modes.dark.separation.layers[2].dE += 1; return checkSeparation(x); });
  control('a raised dark layer held only to the floor', () => { const x = clone(j6); x.modes.dark.separation.layers[1].threshold = 2; return checkSeparation(x); });
  control('a pressed solid aliased to step 11 where its label fails there', () => { const x = clone(j1); const M = x.modes.dark, a = M.solidLabels.indigo.active; Object.assign(a, { side: 'on', step: 11 }); M.variables['--colors-primary-solid-active'] = 'var(--colors-indigo-11)'; return checkActive(x); });
  control('a pressed solid aliased to the hover', () => { const x = clone(j1); x.modes.light.variables['--colors-primary-solid-active'] = 'var(--colors-indigo-10)'; return checkActive(x); });
  control('a back step under apca.ui', () => { const x = clone(j1); const M = x.modes.dim, a = M.solidLabels.indigo.active; a.oklch = [...M.ramps.indigo[1].oklch]; M.variables['--colors-primary-solid-active'] = 'oklch(' + a.oklch.join(' ') + ')'; return checkActive(x); });
  control('a hover ΔE misreported', () => { const x = clone(j1); x.modes.dark.hover.pairs.find((p) => p.rest === 'primary-solid').dE += 1; return checkHover(x); });
  control('a hover under ΔE 4 passed', () => { const x = clone(j1); const p = x.modes.light.hover.pairs.find((q) => !q.pass); p.pass = true; x.modes.light.hover.summary.fail--; x.modes.light.hover.summary.failures.pop(); return checkHover(x); });
  control('a hover pair dropped', () => { const x = clone(j6); const H = x.modes.dark.hover; H.pairs = H.pairs.filter((p) => p.over !== 'surface'); H.summary.pairs--; return checkHover(x); });
  control('a separation misreported', () => { const x = clone(j6); x.modes.dim.separation.dE += 1; return checkSeparation(x); });
  control('the card on the page set to the page colour', () => { const x = clone(j7); x.modes.light.ramps.surface[0] = clone(x.modes.light.ramps.ground[0]); return [...checkSeparation(x), ...allSeparate(x)]; });
  control('a ground anchor not pinned', () => { const x = clone(j8); x.modes.light.ramps.ground[0].oklch[0] -= 0.03; return checkNeutralAnchors(x); });
  control('a surface anchor\'s dark colour not pinned', () => { const x = clone(j8); x.modes.dark.ramps.surface[0].oklch[0] += 0.03; return checkNeutralAnchors(x); });
  control('a separation-miss flag removed', () => checkShowcaseFlags(sc8.replace(/<span class="sc-flag" data-flag="separation"[^>]*>[^<]*<\/span>/, ''), j8));
  control('the ink strip dropped from the showcase', () => checkShowcaseNeutrals(sc6.replace(/var\(--colors-ink-7\)/g, 'var(--colors-gray-7)'), j6));
  control('a dark card drawn on the wrong role', () => checkShowcaseNeutrals(sc6.replace(/(data-mode-panel="dark"><div class="sc-page" style="background:var\(--colors-bg\)"><div class="sc-card2" style="background:var\(--colors-)surface/, '$1bg-subtle'), j6));
  control('hoverMin dropped (the same Radix request without the key)', () => checkHoverMin(jH0, 4));
  control('a valid hoverMin in the bad list', () => checkBadRequests([{ hoverMin: 4 }]));
  control('a valid neutrals value in the bad list', () => checkBadRequests([{ neutrals: { ground: { from: 'Sand' }, cross: true } }]));
  // Radix comparison.
  control('a family with no pin (teal) held to Radix ΔE 0 at step 9', () => checkRadixCompare(jRC, ['teal'], j1, ''));
  control('a compared ΔE misreported', () => { const x = clone(jRC); x.modes.dark.radix.families.indigo.steps[2].dE += 1; return checkRadixCompare(x, Object.keys(RADIX_PIN), j1, ''); });
  control('a default run that carries the comparison', () => { const x = clone(j1); x.compare = jRC.compare; return checkRadixCompare(jRC, Object.keys(RADIX_PIN), x, ''); });
  control('a Radix scale with a step dropped', () => { const x = clone(RADIX); x.scales.sky.darkP3.pop(); x.provenance.scalesSha256 = sha(JSON.stringify(x.scales)); return checkRadixData(x); });
  control('a Radix value edited by hand', () => { const x = clone(RADIX); x.scales.mint.light[8] = '#86ead5'; return checkRadixData(x); });
  control('a valid compare in the bad list', () => checkBadRequests([{ compare: 'radix' }]));

  const bad = results.filter((r) => r.failures.length), soft = bites.filter((b) => !b.ok);
  failed = bad.length > 0 || soft.length > 0;
  console.log(`\n${results.length - bad.length}/${results.length} checks pass; ${bites.length - soft.length}/${bites.length} negative controls bite` + (failed ? ' — FAILED' : ' — ok'));
} catch (e) { console.error('check failed to run: ' + (e.stderr ? String(e.stderr) : e.message)); failed = true; }
finally { if (keep) console.log('kept ' + tmp); else rmSync(tmp, { recursive: true, force: true }); }
process.exit(failed ? 1 : 0);
