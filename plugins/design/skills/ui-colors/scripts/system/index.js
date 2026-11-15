// Color ramps: generated Radix-style 12-step ramps (light and dark) and their mapping onto the kit's
// semantic color variables. The default generator runs the vendored HCT engine (runtime.json, see
// NOTICE.md) lazily; it takes ~300ms, so callers should debounce. `generator: 'oklch'` runs oklch.ts
// instead and never starts the engine.
import RUNTIME from './runtime.json' with { type: 'json' };
import { RADIX_HUES, SPECTRUM_FIXED, normalizeSpectrum } from './config.js';
import { apcaLc, stepTones, DEFAULT_TARGETS } from './contrast.js';
import { applyAnchors, shapeKeys, deriveKeys, deriveNeutral } from './anchors.js';
import { correctHues } from './correct.js';
import { generateOklch, oklchBoundary, quadratureOf } from './oklch.js';
export { apcaLc, stepTones, toneForLc, DEFAULT_TARGETS, TARGET_MAX } from './contrast.js';
export { applyAnchors, isAnchorColor, parseAnchorColor } from './anchors.js';
export { correctHues, yellowWeight } from './correct.js';
export { alphaRamps, alphaOver, oklchToSrgb } from './alpha.js';
export * from './config.js';
import { ROLE_NAMES, DEFAULT_ROLES, trimColor, SCALE_ROLES, ROLE_STEPS, rampVar, roleStep, withAlpha, selectionVars, DEFAULT_ENDPOINT } from './roles.js';
export * from './roles.js';
let engine;
let boundaryFn;
/** The step tones generateSpectrum asks for (contrast targets), per scheme; null while generating the legacy way. */
let toneOverride = null;
/** The even ladder's 12 output stops per scheme (recorded on the first generation), the keys our tones take. */
const stepStops = { light: [], dark: [] };
/**
 * Load the vendored runtime. Its inner HCT engine also has a `boundary(hue, tone, gamut)` function
 * (max in-gamut HCT chroma) that the published runtime API does not re-export. The runtime builds
 * that engine with `new Function("self", source)`; we wrap the global Function constructor only
 * for the first generation to keep a reference to it. The vendored file itself is untouched.
 */
function load() {
    if (engine)
        return engine;
    const Orig = Function;
    engine = new Orig(RUNTIME.code + '\nreturn SpectrumRuntime;')();
    const g = globalThis;
    g.Function = function (...args) {
        const f = Orig(...args);
        if (args.length === 2 && args[0] === 'self')
            return (self) => { f(self); boundaryFn ??= self.HCTPalettes?.boundary; installToneMap(self); };
        return f;
    };
    try {
        const first = engine.generate({ ...engineSettings(normalizeSpectrum({})), ladder: 'even', ...SPECTRUM_FIXED });
        for (const mode of ['light', 'dark'])
            stepStops[mode] = Object.values(first.schemes[mode])[0].map((sw) => sw.stop);
    }
    finally {
        g.Function = Orig;
    }
    return engine;
}
/**
 * The engine reads its step → tone map from a flag on its own global object (__HCT_TONEMAP, written
 * just after __HCT_TONES, the scheme's end tones). An accessor there hands back our solved tones, in
 * step order, while generateSpectrum asks for them; otherwise the engine's own map passes through.
 */
function installToneMap(self) {
    let stored = null;
    Object.defineProperty(self, '__HCT_TONEMAP', {
        configurable: true,
        get() {
            if (!toneOverride)
                return stored;
            const ends = self.__HCT_TONES;
            const tones = toneOverride[ends && ends[0] < ends[1] ? 'dark' : 'light'];
            // Keyed by the even ladder's output stops, in step order; other sampled stops keep the engine's tones.
            const stops = stepStops[ends && ends[0] < ends[1] ? 'dark' : 'light'];
            return stops.length === tones.length ? { ...(stored ?? {}), ...Object.fromEntries(stops.map((k, i) => [String(k), tones[i]])) } : stored;
        },
        set(v) { stored = v; },
    });
}
/** Max in-gamut HCT chroma at a hue and tone for a gamut ('srgb' | 'display-p3'). */
export function gamutBoundary(hue, tone, target) {
    load();
    if (!boundaryFn)
        throw new Error('Spectrum engine boundary function unavailable');
    return boundaryFn(hue, tone, target);
}
/** Generate both schemes. Throws on invalid settings or a malformed ramp. */
/** The engine's own settings: ours minus the contrast targets. */
const engineSettings = (s) => { const { targetsLight: _l, targetsDark: _d, generator: _g, oklchChroma: _c, keyIntensity: _k, keyDepth: _kd, keyRamp: _kr, ...rest } = s; return rest; };
/** A ramp the legacy way (the engine's own tone placement), for measuring targets from old settings. */
const generateLegacy = (s) => engine.generate({ ...engineSettings(s), ...SPECTRUM_FIXED, tint: s.tint });
/** The contrast targets (steps 2–12) a ramp has against its page, per scheme, measured on the neutral family. */
export function measureTargets(data) {
    const of = (mode) => {
        const fam = Object.keys(data.schemes[mode]).find((n) => /neutral/i.test(n)) ?? Object.keys(data.schemes[mode])[0];
        const ramp = data.schemes[mode][fam];
        return ramp.slice(1).map((sw) => Math.round(apcaLc(sw.hct[2], ramp[0].hct[2]) * 10) / 10);
    };
    return { light: of('light'), dark: of('dark') };
}
export function generateSpectrum(settings = {}) {
    const s = normalizeSpectrum(settings);
    if (s.generator === 'oklch')
        return correctHues(generateOklch(s), s);
    load();
    // Contrast targets (contrast.ts): a theme that sets only the legacy tone placement (peak tone,
    // scale) has its targets measured from the ramp those settings produce.
    const legacy = ['ptAuto', 'pt', 'ladder'].some((k) => k in settings) && !('targetsLight' in settings || 'targetsDark' in settings);
    const targets = legacy ? measureTargets(generateLegacy(s)) : { light: s.targetsLight, dark: s.targetsDark };
    const tones = { light: stepTones(s.toneMax, targets.light, 'light'), dark: stepTones(s.darkTone, targets.dark, 'dark') };
    toneOverride = tones;
    let out;
    try {
        // The even ladder keeps the kit's chroma envelope; its 12 stops take our tones. Step 9 is the chroma peak.
        out = engine.generate({ ...engineSettings(s), ladder: 'even', ptAuto: 0, pt: Math.round(tones.light[8] * 2) / 2, ...SPECTRUM_FIXED, tint: s.tint });
    }
    finally {
        toneOverride = null;
    }
    out.settings = { ...out.settings, keyIntensity: s.keyIntensity, keyDepth: s.keyDepth, keyRamp: s.keyRamp, targetsLight: targets.light, targetsDark: targets.dark };
    for (const mode of ["light", "dark"])
        for (const [name, ramp] of Object.entries(out.schemes[mode])) {
            if (ramp.length !== 12 || ramp.some((sw) => !sw.css))
                throw new Error(`Invalid generated ramp: ${name}`);
        }
    return correctHues(out, s);
}
export function families(data) {
    const all = Object.keys(data.schemes.light);
    const accents = data.metadata?.light.accents ?? all;
    const neutrals = data.metadata?.light.neutrals ?? all.filter((n) => !accents.includes(n));
    return { all, accents, neutrals };
}
const hueOf = (data, name) => data.schemes.light[name][8].hct[0];
/** Resolve a requested family name: exact match, else the candidate nearest in hue. */
export function closestFamily(data, requested, candidates) {
    if (candidates.includes(requested))
        return requested;
    // A family name: a Radix name, `hNNN` (an HCT hue, 0–360, decimals allowed) or `oklch:NNN` (an OKLCH hue, matched against
    // each family's step-9 OKLCH hue). Anything else is a request error, never a silent fallback to some hue.
    const hct = /^h(\d{1,3}(?:\.\d+)?)$/.exec(requested ?? ''), ok = /^oklch:(\d{1,3}(?:\.\d+)?)$/.exec(requested ?? '');
    const hue = RADIX_HUES[requested] ?? (hct ? Number(hct[1]) : ok ? Number(ok[1]) : undefined);
    if (hue === undefined || hue > 360) {
        const e = new Error(`role family ${JSON.stringify(requested)} is not a family of this system (${candidates.join(', ')}), a Radix name, an HCT hue (h0–h360) or an OKLCH hue (oklch:0–oklch:360)`);
        e.request = true;
        throw e;
    }
    // The Radix hues are HCT, and they land on the same families in OKLCH angles, except red, which sits
    // near 25° there and would tip to crimson at its HCT 20°.
    const want = data.settings.generator === 'oklch' && requested === 'red' ? 25 : hue;
    const hueAt = ok ? (n) => data.schemes.light[n][8].oklch[2] : (n) => hueOf(data, n);
    const distance = (n) => { const d = Math.abs(hueAt(n) - want) % 360; return Math.min(d, 360 - d); };
    return candidates.reduce((best, n) => (distance(n) < distance(best) ? n : best));
}
/**
 * Color roles, each a family: brand (primary, secondary, neutral), feedback (critical = errors and
 * destructive actions, warning, success, info) and data 1–6 (chart series and categories, well spaced in hue).
 */
/** Resolve the role families against what this generation actually produced. */
export function resolveRoles(data, wanted = {}) {
    const f = families(data);
    const w = { ...DEFAULT_ROLES, ...wanted };
    return Object.fromEntries(ROLE_NAMES.map((r) => [r, r === 'neutral'
            ? (f.all.includes(w.neutral) ? w.neutral : (f.neutrals[0] ?? 'neutral'))
            : closestFamily(data, w[r], f.accents)]));
}
/**
 * Steps 1–12 per family and scheme (index 0 = step 1). Step 1 is the scheme endpoint: the
 * Light endpoint tone in light ramps, the Dark endpoint tone in dark ramps (100 / 0 = white / black).
 */
export function ramps(data, mode) {
    return Object.fromEntries(Object.entries(data.schemes[mode]).map(([name, ramp]) => [name, ramp.map((sw) => trimColor(sw.css))]));
}
/** Semantic variables per scheme: ramp variables plus roles that point at them. */
export function roleVariables(data, roles, mode, solidSteps = {}) {
    const vars = {};
    for (const [role, entry] of Object.entries(ROLE_STEPS)) {
        const { family, step, alpha } = roleStep(entry, mode);
        vars[`--colors-${role}`] = withAlpha(`var(${rampVar(roles[family], step)})`, alpha);
    }
    // An anchored role's solid follows its anchor (applyAnchors): solid at the anchored step, hover one
    // darker (one lighter at step 12, the darkest).
    for (const [role, s] of Object.entries(solidSteps)) {
        if (!SCALE_ROLES.includes(role))
            continue;
        vars[`--colors-${role}-solid`] = `var(${rampVar(roles[role], s)})`;
        vars[`--colors-${role}-solid-hover`] = `var(${rampVar(roles[role], s === 12 ? 11 : s + 1)})`;
    }
    if (data.subtle && data.subtle[mode]) vars['--colors-fg-subtle'] = data.subtle[mode].replace(/oklch\(([\d.]+) ([\d.]+) ([\d.]+)\)/, (m, a, b, c) => 'oklch(' + (+(+a).toFixed(4)) + ' ' + (+(+b).toFixed(4)) + ' ' + (+(+c).toFixed(4)) + ')');
    // Text on a primary solid: the engine's APCA choice for the solid step (9 unless anchored).
    vars['--colors-fg-on-solid'] = data.schemes[mode][roles.primary][(solidSteps.primary ?? 9) - 1].apca.css;
    // White and black: neutral step 3 of the light and dark ramps, the same in both schemes; fg.strong
    // (headings, titles) is black in light, white in dark. endpointVars maps them to another family.
    Object.assign(vars, endpointVars(data, roles));
    vars['--colors-fg-strong'] = data.strongInk?.[mode] ? `var(${rampVar(roles.neutral, 12)})` : mode === 'dark' ? 'var(--colors-white)' : 'var(--colors-black)';
    // The selection fills follow the theme's emphasis (selectionVars).
    for (const [k, v] of Object.entries(selectionVars(mode)))
        vars[`--colors-${k}`] = v;
    return vars;
}
/**
 * White and black (`--colors-white`, `--colors-black`), the same in both schemes. By default they are the two ends of
 * the system, past every step and short of pure: white halfway in lightness from the light page (light step 1) to pure
 * white, black at ENDPOINT_BLACK of the dark page's lightness (dark step 1), each keeping the neutral's hue, and never
 * inside the ramps of either scheme. A request
 * may name a step of the neutral ramp (white from the light ramp, black from the dark one) or 'pure' (#fff, #000).
 */
export const ENDPOINT_WHITE = 0.5, ENDPOINT_BLACK = 0.6;
export function endpointVars(data, roles, map = {}) {
    const ramp = (mode) => data.schemes[mode][roles.neutral];
    const css = ([l, c, h]) => `oklch(${+l.toFixed(4)} ${+c.toFixed(4)} ${+(c < 1e-4 || !Number.isFinite(h) ? 0 : h).toFixed(4)})`;
    // Never inside the ramps: where a step of either scheme is already lighter or darker (a contrast mode's pure ink, a
    // white page), the endpoint takes that lightness, without chroma once it is pure.
    const every = ['light', 'dark'].flatMap((mode) => Object.values(data.schemes[mode]).flatMap((steps) => steps.map((s) => s.oklch[0])));
    const clamp = (l, c, h, edge) => { const x = edge === 1 ? Math.min(1, Math.max(l, ...every)) : Math.max(0, Math.min(l, ...every)); return css([x, x > 0.9999 || x < 0.0001 ? 0 : c, h]); };
    const end = { white: () => { const [l, c, h] = ramp('light')[0].oklch; return clamp(l + (1 - l) * ENDPOINT_WHITE, c * (1 - ENDPOINT_WHITE), h, 1); },
        black: () => { const [l, c, h] = ramp('dark')[0].oklch; return clamp(l * ENDPOINT_BLACK, c, h, 0); } };
    const pick = (name, want, mode, pure) => want === 'pure' ? pure : want == null ? end[name]() : ramp(mode)[want - 1].css;
    return { '--colors-white': pick('white', map.white, 'light', '#fff'), '--colors-black': pick('black', map.black, 'dark', '#000') };
}
const block = (sel, vars) => `${sel} {\n${Object.entries(vars).map(([k, v]) => `  ${k}: ${v};`).join('\n')}\n}`;
/**
 * CSS that applies the ramps over the kit's semantic colors, mirroring the kit's scheme
 * structure: light by default, dark under prefers-color-scheme, .light/.dark to force. Emit it
 * after the kit stylesheet; selectors match the kit's own so each rule wins its counterpart.
 * Variable names match the kit's tokens (--colors-{family}-{1..12}, --colors-{role}).
 */
export function spectrumCSS(data, roles, scope, solidSteps = { light: {}, dark: {} }) {
    const light = roleVariables(data, roles, 'light', solidSteps.light), dark = roleVariables(data, roles, 'dark', solidSteps.dark);
    const rampVars = (mode) => Object.fromEntries(Object.entries(ramps(data, mode)).flatMap(([name, steps]) => steps.map((css, i) => [rampVar(name, i + 1), css])));
    // Scoped: everything is declared on the scope element itself, so it re-resolves there and
    // nothing outside it changes; .light/.dark on the scope element force a scheme.
    const sel = scope
        ? { base: scope, light: `${scope}.light`, dark: `${scope}.dark`, auto: `${scope}:not(.light)` }
        : { base: ':where(:root)', light: '.light', dark: '.dark', auto: ':where(:root)' };
    return [
        block(sel.base, { ...rampVars('light'), ...light }),
        block(sel.light, { ...rampVars('light'), ...light }),
        `@media (prefers-color-scheme: dark) {\n${block(sel.auto, { ...rampVars('dark'), ...dark })}\n}`,
        block(sel.dark, { ...rampVars('dark'), ...dark }),
    ].join('\n');
}
// ── Diagnostics ──
/** CAM16 unique hues: hue angle h, eccentricity e, quadrature H (red, yellow, green, blue, red). */
const UNIQUE = { h: [20.14, 90.0, 164.25, 237.53, 380.14], e: [0.8, 0.7, 1.0, 1.2, 0.8], H: [0, 100, 200, 300, 400] };
export const UNIQUE_HUES = [{ name: 'R', h: 20.14, H: 0 }, { name: 'Y', h: 90, H: 100 }, { name: 'G', h: 164.25, H: 200 }, { name: 'B', h: 237.53, H: 300 }];
/** CAM16 hue quadrature H (0–400) for a hue angle h. */
export function hueQuadrature(h) {
    const hp = h < UNIQUE.h[0] ? h + 360 : h;
    let i = 0;
    while (i < 3 && hp >= UNIQUE.h[i + 1])
        i++;
    const a = (hp - UNIQUE.h[i]) / UNIQUE.e[i], b = (UNIQUE.h[i + 1] - hp) / UNIQUE.e[i + 1];
    return UNIQUE.H[i] + (100 * a) / (a + b);
}
/**
 * What shaped this generation: the peak tone T* (the weakest hue's chroma peak), the shared peak
 * chroma C* and the accent that limits it, the primary's contrast checks, each accent's position in
 * hue quadrature, and the max in-gamut chroma per accent by tone (20–92).
 */
export function spectrumDiagnostics(data, roles, step = 2) {
    const accents = families(data).accents;
    const light = data.schemes.light, target = data.settings.target;
    const oklch = data.settings.generator === 'oklch';
    const boundary = oklch ? oklchBoundary : gamutBoundary, quadrature = oklch ? quadratureOf : hueQuadrature;
    const peakTone = data.checks?.light.peakTone ?? light[accents[0]][8].hct[2];
    const rows = accents.map((name) => {
        const h = light[name][8].hct[0];
        const curve = [];
        for (let T = 20; T <= 92; T += step)
            curve.push([T, boundary(h, T, target)]);
        return { name, color: light[name][8].css, h, H: quadrature(h), curve, atPeak: boundary(h, peakTone, target) };
    });
    const limiting = rows.reduce((a, b) => (b.atPeak < a.atPeak ? b : a));
    const weakest = rows[0].curve.map(([T], i) => [T, Math.min(...rows.map((r) => r.curve[i][1]))]);
    const check = (mode) => data.checks?.[mode].rows[roles.primary]?.roles ?? { r11: NaN, r12: NaN };
    return {
        peakTone,
        peakChroma: Math.min(...accents.map((a) => light[a][8].hct[1])),
        limitedBy: limiting.name,
        target,
        primary: { name: roles.primary, light: check('light'), dark: check('dark') },
        accents: rows.map(({ atPeak: _p, ...r }) => r),
        weakest,
        tones: [20, 92],
    };
}
// Solids that carry text are solved to the label's contrast (WCAG 2, 4.6:1 = 4.5 + a margin for 8-bit rounding):
// each family's step 9 keeps its hue and chroma and lowers lightness until the fixed light label (light neutral 1)
// reaches the target; step 10 (hover) moves further from the label by the ramp's own 9→10 gap, darker in both modes.
// Idempotent: a solid already at or above target is untouched.
const SOLID_TARGET = 4.6;
function okToLinear(L, C, H) { const a = C * Math.cos(H * Math.PI / 180), b = C * Math.sin(H * Math.PI / 180);
    const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3;
    return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s].map(v => Math.min(1, Math.max(0, v))); }
function wcagY(L, C, H) { const [r, g, b] = okToLinear(L, C, H); return 0.2126 * r + 0.7152 * g + 0.0722 * b; }
function wcagRatio(a, b) { const x = wcagY(...a), y = wcagY(...b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
function parseOk(css) { const m = /oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)/.exec(css || ''); return m ? [+m[1], +m[2], +m[3]] : null; }
function okCss(L, C, H) { return 'oklch(' + (+L.toFixed(4)) + ' ' + (+C.toFixed(4)) + ' ' + (+H.toFixed(4)) + ')'; }
function setSwatch(sw, L, C, H) { sw.css = okCss(L, C, H); if (Array.isArray(sw.oklch)) sw.oklch = [L, C, H]; }
function solveSolids(data, solidSteps, roles) {
    const lab = parseOk(((data.schemes.light.neutral || [])[0] || {}).css); if (!lab) return data;
    // fg-subtle reads neutral step 10 as text; keep its unsolved value before the hover step moves.
    data.subtle = data.subtle || { light: ((data.schemes.light.neutral || [])[9] || {}).css, dark: ((data.schemes.dark.neutral || [])[9] || {}).css };
    for (const mode of ['light', 'dark']) for (const [fam, ramp] of Object.entries(data.schemes[mode] || {})) {
        // the solid step: 9, or an anchored role's step (its hover is the next step, or 11 under a step-12 solid)
        const sts = [9]; for (const [role, s] of Object.entries((solidSteps && solidSteps[mode]) || {})) if (roles && roles[role] === fam && s !== 9) sts.push(s);
        for (const st of sts) {
        const s9 = ramp[st - 1], s10 = ramp[st === 12 ? 10 : st], p9 = parseOk(s9 && s9.css), p10 = parseOk(s10 && s10.css); if (!p9 || !p10) continue;
        const gap = Math.max(0.03, Math.abs(p10[0] - p9[0])); let L = p9[0];
        if (wcagRatio([L, p9[1], p9[2]], lab) < SOLID_TARGET) { let lo = 0, hi = L; for (let i = 0; i < 30; i++) { const mid = (lo + hi) / 2; if (wcagRatio([mid, p9[1], p9[2]], lab) >= SOLID_TARGET) lo = mid; else hi = mid; } L = lo; setSwatch(s9, L, p9[1], p9[2]); }
        const hL = Math.min(p10[0], L - gap); if (hL < p10[0] || p10[0] > L) setSwatch(s10, Math.max(0, hL), p10[1], p10[2]);
        }
    }
    // control-border (neutral step 8) is a control's only edge: ≥ 3:1 against bg and bg-subtle (steps 1, 2) in each scheme.
    for (const mode of ['light', 'dark']) { const n = data.schemes[mode].neutral; if (!n) continue; const e = parseOk(n[7].css), g1 = parseOk(n[0].css), g2 = parseOk(n[1].css); if (!e || !g1 || !g2) continue;
        const okE = L => Math.min(wcagRatio([L, e[1], e[2]], g1), wcagRatio([L, e[1], e[2]], g2)) >= 3.05; if (okE(e[0])) continue;
        const dir = mode === 'light' ? -1 : 1; let L = e[0]; for (let i = 0; i < 200 && !okE(L) && L > 0 && L < 1; i++) L += dir * 0.005; setSwatch(n[7], Math.min(1, Math.max(0, L)), e[1], e[2]); }
    return data;
}

/**
 * Ramps with a theme's anchors applied (anchors.ts): each anchor's family re-shaped and its step
 * overridden, the roles (a role whose family another anchor claimed moves to a free family), and the
 * solid step per anchored role. The key intensity and depth apply here, around the pins, with or without
 * anchors, so read a theme's ramps from this. Use the returned roles.
 */
export function anchoredSpectrum(data, roles, anchors = []) {
    if (!anchors.length)
        return { data: solveSolids(shapeKeys(data)), roles, report: [], solidSteps: { light: {}, dark: {} } };
    const targets = { light: data.settings.targetsLight ?? [...DEFAULT_TARGETS.light], dark: data.settings.targetsDark ?? [...DEFAULT_TARGETS.dark] };
    const r = applyAnchors(data, roles, anchors, targets);
    const SK = deriveKeys(shapeKeys(r.data, r.pins), r.pins), DN = deriveNeutral;
    return { data: solveSolids(anchors.some(a => a.role === 'ground' || a.role === 'ink') && !anchors.some(a => a.role === 'neutral') ? DN(SK, r.roles.neutral) : SK, r.solidSteps, r.roles), roles: r.roles, report: r.report, solidSteps: r.solidSteps };
}
