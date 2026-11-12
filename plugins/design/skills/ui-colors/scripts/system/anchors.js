// Color anchors (docs/reports/2026-11-03-color-anchoring-spike.md): a brand's exact colors placed in
// the generated ramps. Per anchor, on its role's family:
//   1. pin the hue: every step of the family takes the anchor's OKLCH hue (light and dark ramps);
//   2. re-shape the chroma, split by `reach`, so a strong key color does not tint the whole system.
//      The ratio is anchor chroma / the anchored step's chroma. `key` (the default, except on neutral
//      families): the solid and text steps (9–12, or from the anchored step if it is lighter) take
//      chroma × ratio, capped at the anchor's chroma so no step outshouts the brand (a dark anchor's
//      low chroma never pulls a step under its generated chroma); the steps below
//      keep the generated chroma, or lose it with a ratio under 1, so a muted anchor still mutes its
//      tints. `ramp` (the default on neutral families): every step takes chroma × ratio. Both are
//      clamped into the target gamut;
//   3. override the anchored step with the exact color (light ramp). The step is the one whose
//      contrast target is nearest the anchor's Lc against the light page, unless the anchor names one;
//   4. the role's solid follows the anchored step when the anchor lands on 8–12 (solidSteps.light): a
//      brand's main color is usually its darkest solid.
// An anchor may give its own `dark` color: it is placed in the dark ramp the same way (against the
// dark page, the dark targets) and moves the dark solid (solidSteps.dark). Without one, the dark ramp
// takes the hue and chroma only and the dark solid stays at step 9.
// An exact color rarely sits where the generator put that step, so the ramp settles around it. The
// solids and text (9–12) are one run: a pin at 10–12 spreads its lightness offset evenly back to step
// 9, which stays put, and chroma runs straight from 9 to the pin; steps past a pin ease back to their
// own lightness. A surface pin also carries its hue along that run, and a page pin eases lightness,
// chroma over steps 2–4 and carries its hue on to step 9. Steps 5–8 keep their lightness, and so does
// everything for an anchor below 9.
// Two surface anchors pin the ends of the neutral ramp instead of a role's family: `ground` is the
// light page (step 1) and the dark ink (step 12); `ink` is the light ink (step 12) and the dark page
// (step 1). `dark` gives the color for the dark scheme; without one the same color is used.
import { apcaLc, deepenKeys, DEFAULT_TARGETS, luminance, stepTones } from './contrast.js';
/** How far an anchor's chroma reaches: the solid and text steps only (`key`), or every step (`ramp`). */
export const ANCHOR_REACHES = ['key', 'ramp'];
/** The first step of the solids and text, where a `key` anchor's chroma starts. */
const KEY_FROM = 9;
/** The first step a page pin leaves alone. */
const BASE_TO = 5;
/** Below this chroma a color has no hue worth carrying. */
const HUELESS = 0.01;
// ── sRGB / Display P3 ↔ OKLab ──
const lin = (c) => (Math.abs(c) <= 0.04045 ? c / 12.92 : Math.sign(c) * ((Math.abs(c) + 0.055) / 1.055) ** 2.4);
// ── Anchor colors: any CSS color in a wide or device space, not only hex ──
// Accepts oklch(), oklab(), color(srgb | srgb-linear | display-p3 | xyz | xyz-d65 …), rgb() and #rrggbb.
// Everything goes to linear sRGB (unclamped, so P3 and XYZ colors outside sRGB keep their values) and then to OKLab.
const M_P3_XYZ = [[0.4865709486, 0.2656676932, 0.1982172852], [0.2289745641, 0.6917385218, 0.0792869141], [0, 0.0451133819, 1.0439443689]];
const M_XYZ_SRGB = [[3.2409699419, -1.5373831776, -0.4986107603], [-0.9692436363, 1.8759675015, 0.0415550574], [0.0556300797, -0.2039769589, 1.0569715142]];
const M_SRGB_LMS = [[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]];
const M_LAB_LMS = [[1, 0.3963377774, 0.2158037573], [1, -0.1055613458, -0.0638541728], [1, -0.0894841775, -1.291485548]];
const M_LMS_SRGB = [[4.0767416621, -3.3077115913, 0.2309699292], [-1.2684380046, 2.6097574011, -0.3413193965], [-0.0041960863, -0.7034186147, 1.707614701]];
const mul3 = (m, v) => m.map((r) => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]);
const num = (t, scale = 1) => { const s = String(t).trim(); return s.endsWith('%') ? parseFloat(s) / 100 * scale : parseFloat(s); };
const labOfLinear = (rgb) => mul3([[0.2104542553, 0.793617785, -0.0040720468], [1.9779984951, -2.428592205, 0.4505937099], [0.0259040371, 0.7827717662, -0.808675766]], mul3(M_SRGB_LMS, rgb).map(Math.cbrt));
const linearOfLab = (lab) => mul3(M_LMS_SRGB, mul3(M_LAB_LMS, lab).map((x) => x * x * x));
function anchorLab(v) {
    const s = String(v || '').trim().toLowerCase();
    let m = s.match(/^#([0-9a-f]{6})$/);
    if (m) return labOfLinear([0, 2, 4].map((i) => lin(parseInt(m[1].slice(i, i + 2), 16) / 255)));
    m = s.match(/^(oklch|oklab|rgba?|color)\(\s*(.*?)\s*\)$/); if (!m) return null;
    const fn = m[1], parts = m[2].split('/')[0].trim().split(/[\s,]+/);
    if (fn === 'oklch') { const L = num(parts[0], 1), C = num(parts[1], 0.4), H = parseFloat(parts[2]) * Math.PI / 180; return [L, C * Math.cos(H), C * Math.sin(H)]; }
    if (fn === 'oklab') return [num(parts[0], 1), num(parts[1], 0.4), num(parts[2], 0.4)];
    if (fn === 'rgb' || fn === 'rgba') return labOfLinear(parts.slice(0, 3).map((p) => lin(num(p, 255) / 255)));
    const space = parts[0], c = parts.slice(1, 4).map((p) => num(p, 1));
    if (space === 'srgb') return labOfLinear(c.map(lin));
    if (space === 'srgb-linear') return labOfLinear(c);
    if (space === 'display-p3') return labOfLinear(mul3(M_XYZ_SRGB, mul3(M_P3_XYZ, c.map(lin))));
    if (space === 'xyz' || space === 'xyz-d65') return labOfLinear(mul3(M_XYZ_SRGB, c));
    return null;
}
/** OKLCH and relative luminance Y of an anchor color string, or null if it can't be read. */
export function parseAnchorColor(v) {
    const lab = anchorLab(v); if (!lab || lab.some((x) => !isFinite(x))) return null;
    const [L, a, b] = lab, C = Math.hypot(a, b), H = ((Math.atan2(b, a) * 180) / Math.PI + 360) % 360, rgb = linearOfLab(lab);
    return { oklch: [L, C, H], y: Math.max(0, 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) };
}
export const isAnchorColor = (v) => typeof v === 'string' && parseAnchorColor(v) !== null;
const LMS_TO_LAB = [[0.2104542553, 0.793617785, -0.0040720468], [1.9779984951, -2.428592205, 0.4505937099], [0.0259040371, 0.7827717662, -0.808675766]];
const mul = (m, v) => m.map((r) => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]);
function srgbToOklch(color) {
    // Name kept for the callers; takes any anchor color (see parseAnchorColor).
    const p = parseAnchorColor(color);
    if (!p) throw new Error('anchor color not readable: ' + color);
    return p.oklch;
}
/** OKLCH → linear RGB in sRGB or Display P3 primaries. */
function oklchToLinear([L, C, h], gamut) {
    const a = C * Math.cos((h * Math.PI) / 180), b = C * Math.sin((h * Math.PI) / 180);
    const lms = [L + 0.3963377774 * a + 0.2158037573 * b, L - 0.1055613458 * a - 0.0638541728 * b, L - 0.0894841775 * a - 1.291485548 * b].map((x) => x ** 3);
    const srgb = mul([[4.0767416621, -3.3077115913, 0.2309699292], [-1.2684380046, 2.6097574011, -0.3413193965], [-0.0041960863, -0.7034186147, 1.707614701]], lms);
    return gamut === 'display-p3' ? mul([[0.8224621, 0.177538, 0], [0.0331941, 0.9668058, 0], [0.0170827, 0.0723974, 0.9105199]], srgb) : srgb;
}
const inGamut = (lch, gamut) => oklchToLinear(lch, gamut).every((c) => c >= -1e-4 && c <= 1 + 1e-4);
/** The largest chroma ≤ C at this lightness and hue inside the gamut. */
export function clampChroma(L, C, h, gamut) {
    if (inGamut([L, C, h], gamut))
        return C;
    let lo = 0, hi = C;
    for (let i = 0; i < 24; i++) {
        const mid = (lo + hi) / 2;
        if (inGamut([L, mid, h], gamut))
            lo = mid;
        else
            hi = mid;
    }
    return lo;
}
/** Relative luminance (Y) of an OKLCH color, via sRGB (the APCA input). */
const yOf = (lch) => { const [r, g, b] = oklchToLinear(lch, 'srgb').map((c) => Math.min(1, Math.max(0, c))); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
/** Relative luminance (Y) of an OKLCH color, unclamped, so a color outside sRGB keeps its true luminance. */
export const linearY = (lch) => { const [r, g, b] = oklchToLinear(lch, 'srgb'); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
export const toneOfY = (Y) => (Y > 0.008856 ? 116 * Math.cbrt(Y) - 16 : 903.3 * Y);
const okLab = ([L, C, h]) => [L, C * Math.cos((h * Math.PI) / 180), C * Math.sin((h * Math.PI) / 180)];
const deltaE = (p, q) => { const [a, b] = [okLab(p), okLab(q)]; return 100 * Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]); };
/** A swatch's tone: the engine's, or from its color (pure gray ramps carry no HCT). */
const toneOf = (sw) => sw.hct?.[2] ?? toneOfY(yOf(sw.oklch));
export const css = ([L, C, h]) => `oklch(${L} ${C} ${h})`;
/** Text on a fill: white or the darkest ink, whichever has the larger APCA Lc. */
export function onFill(lch) {
    const t = toneOfY(yOf(lch));
    const white = apcaLc(100, t), black = apcaLc(0, t);
    return white >= black ? { name: 'white', css: '#fff', lc: -white, ok: white >= 60 } : { name: 'black', css: '#000', lc: black, ok: black >= 60 };
}
function setSwatch(sw, lch) {
    sw.oklch = lch;
    sw.css = css(lch);
    sw.apca = onFill(lch);
}
/** Move a swatch, keeping the tone contrast reads in step with it. */
function moveSwatch(sw, lch, gamut) {
    setSwatch(sw, [lch[0], clampChroma(lch[0], Math.max(0, lch[1]), lch[2], gamut), lch[2]]);
    if (sw.hct)
        sw.hct[2] = toneOfY(yOf(sw.oklch));
}
/** The L that puts this hue and chroma (capped by the gamut) on a luminance: luminance rises with L. */
export function solveLightness(Y, C, h, gamut) {
    let lo = 0, hi = 1;
    for (let i = 0; i < 26; i++) {
        const L = (lo + hi) / 2;
        if (linearY([L, clampChroma(L, C, h, gamut), h]) < Y)
            lo = L;
        else
            hi = L;
    }
    return (lo + hi) / 2;
}
const mix = (a, b, t) => a + (b - a) * t;
const mixHue = (a, b, t) => (a + ((((b - a) % 360) + 540) % 360 - 180) * t + 360) % 360;
/**
 * Settle steps 9–12 around a color about to be pinned at `step`, so the run stays one curve. Run
 * before the pin: it reads the step's generated lightness. `withHue` carries the pin's hue along the
 * run, for a surface pin, whose family keeps its own hue.
 */
function settleKey(ramp, step, want, gamut, withHue = false) {
    if (step < KEY_FROM)
        return;
    // Only ever away from the page: a pin brighter than its step must not cost the text steps contrast.
    const offset = want[0] - ramp[step - 1].oklch[0], awayFromPage = Math.sign(ramp[11].oklch[0] - ramp[0].oklch[0]);
    const shift = offset * awayFromPage > 0 ? offset : 0, from = ramp[KEY_FROM - 1].oklch[1];
    for (let n = KEY_FROM; n <= 12; n++) {
        if (n === step)
            continue;
        const sw = ramp[n - 1], [L, C, h] = sw.oklch, inRun = n < step;
        const t = inRun ? (n - KEY_FROM) / (step - KEY_FROM) : (12 - n) / (12 - step);
        moveSwatch(sw, [L + shift * t, inRun ? mix(from, want[1], t) : C, withHue && inRun && want[1] > HUELESS ? mixHue(h, want[2], t) : h], gamut);
    }
}
/**
 * Ease the base range toward a color about to be pinned as the page (step 1): lightness and chroma
 * over steps 2–4, and a tinted page's hue on to step 9, with steps 5–8 held at step 4's chroma or
 * their own so the tint doesn't dip on its way to the solids.
 */
function settleBase(ramp, want, gamut) {
    const [L1, C1] = ramp[0].oklch, tinted = want[1] > HUELESS;
    let floor = 0;
    for (let n = 2; n < KEY_FROM; n++) {
        const sw = ramp[n - 1], [L, C, h] = sw.oklch, t = Math.max(0, (BASE_TO - n) / (BASE_TO - 1));
        const nextC = n < BASE_TO ? C + (want[1] - C1) * t : tinted ? Math.max(C, floor) : C;
        floor = nextC;
        moveSwatch(sw, [L + (want[0] - L1) * t, nextC, tinted ? mixHue(h, want[2], (KEY_FROM - n) / (KEY_FROM - 1)) : h], gamut);
    }
}
const neutralFamiliesOf = (data) => new Set(data.metadata?.light.neutrals ?? Object.keys(data.schemes.light).filter((n) => /neutral|gray|mauve|slate|sage|olive|sand/i.test(n)));
/**
 * The dials for steps 9–12 of every accent family, after the generator and the anchors; neutrals keep
 * theirs, since their 9–12 are text. `keyDepth` moves each step's tone (deepenKeys), `keyIntensity`
 * scales its chroma (% of generated), and intensity alone keeps the luminance, so contrast holds. The
 * gamut caps the chroma, with no step passing step 9. A pin stays exact: both ease out to it, so the
 * run stays one curve. Returns `data` itself with both at rest.
 */
export function shapeKeys(data, pins = { light: {}, dark: {} }) {
    const scale = Number(data.settings.keyIntensity ?? 100) / 100, depth = Number(data.settings.keyDepth ?? 0), lead_ = Math.max(0, Math.min(KEY_FROM - 2, Math.round(Number(data.settings.keyRamp ?? 0))));
    if (scale === 1 && !depth)
        return data;
    const out = structuredClone(data);
    const gamut = String(data.settings.target ?? 'display-p3'), neutrals = neutralFamiliesOf(data);
    for (const mode of ['light', 'dark']) {
        const targets = (mode === 'light' ? data.settings.targetsLight : data.settings.targetsDark) ?? DEFAULT_TARGETS[mode];
        const placed = deepenKeys(targets, depth, mode);
        for (const [family, ramp] of Object.entries(out.schemes[mode])) {
            if (neutrals.has(family))
                continue;
            const pin = pins[mode][family], span = pin ? Math.max(pin - KEY_FROM, 12 - pin) : 1;
            const tones = stepTones(toneOf(ramp[0]), placed, mode);
            const lc = (sw) => apcaLc(toneOf(sw), toneOf(ramp[0])), before = Object.fromEntries(ramp.map((sw) => [sw.step, lc(sw)]));
            let peak = Infinity;
            // keyRamp eases intensity in over the steps before 9 (¼, ½, ¾ for 3), so chroma builds instead of jumping at 9.
            for (const sw of ramp.slice(KEY_FROM - 1 - lead_)) {
                if (sw.step === pin)
                    continue;
                const lead = sw.step < KEY_FROM, ease = lead ? (sw.step - (KEY_FROM - 1 - lead_)) / (lead_ + 1) : 1;
                const reach = (pin ? Math.abs(sw.step - pin) / span : 1) * ease, [, C, h] = sw.oklch;
                const was = linearY(sw.oklch), Y = depth && !lead ? luminance(mix(toneOfY(was), tones[sw.step - 1], reach)) : was;
                // The gamut stops a solid first. Without a pin no step passes it, so step 9 stays the run's peak.
                const lifted = C * mix(1, scale, reach), wanted = pin || lead ? lifted : Math.min(lifted, peak);
                const L = solveLightness(Y, wanted, h, gamut);
                setSwatch(sw, [L, clampChroma(L, wanted, h, gamut), h]);
                if (sw.hct)
                    sw.hct[2] = toneOfY(linearY(sw.oklch));
                if (!lead)
                    peak = sw.oklch[1];
            }
            // Ramp-in never passes the solid: a lead step capped at step 9's chroma (yellows, whose 9 is lifted light, would otherwise peak at 8).
            if (lead_) {
                const top = ramp[KEY_FROM - 1].oklch[1];
                for (const sw of ramp.slice(KEY_FROM - 1 - lead_, KEY_FROM - 1))
                    if (sw.step !== pin && sw.oklch[1] > top) {
                        const h = sw.oklch[2], L = solveLightness(linearY(sw.oklch), top, h, gamut);
                        setSwatch(sw, [L, clampChroma(L, top, h, gamut), h]);
                        if (sw.hct)
                            sw.hct[2] = toneOfY(linearY(sw.oklch));
                    }
            }
            // The check the lint reads, shifted by what depth moved: the generator's Lc is its own measure.
            const row = out.checks?.[mode].rows[family];
            if (row && depth) {
                const shift = (n) => lc(ramp[n - 1]) - before[n];
                row.roles = { ...row.roles, r11: row.roles.r11 + shift(11), r12: row.roles.r12 + shift(12) };
                row.passes = { ...row.passes, r11: row.roles.r11 >= 60, r12: row.roles.r12 >= 75 };
            }
        }
    }
    return out;
}
/**
 * Apply anchors to generated ramps (a copy is returned). `roles` maps each role to its family.
 * Returns the report per anchor and the solid step per anchored role.
 */
export function applyAnchors(data, roles, anchors, targets) {
    const out = structuredClone(data);
    const gamut = String(data.settings.target ?? 'display-p3');
    const report = [];
    const solidSteps = { light: {}, dark: {} };
    const pins = { light: {}, dark: {} };
    // Each anchor claims its family. Roles often share one (primary and data 1 both default to indigo),
    // so a second anchor on a claimed family moves its role to the nearest free family by hue: first a
    // family no role uses, else one no anchor has claimed.
    const outRoles = { ...roles };
    const claimed = new Map();
    const neutralFamilies = neutralFamiliesOf(data);
    const hueGap = (a, b) => { const d = Math.abs(a - b) % 360; return Math.min(d, 360 - d); };
    // Claim in role order (brand, feedback, then data), so a brand role keeps its family whatever order
    // the anchors were written in.
    const order = Object.keys(roles);
    const sorted = [...anchors].sort((a, b) => order.indexOf(a.role) - order.indexOf(b.role));
    for (const anchor of sorted) {
        let family = outRoles[anchor.role];
        if (!family || !out.schemes.light[family])
            continue;
        const want = srgbToOklch(anchor.value);
        if (claimed.has(family) && claimed.get(family) !== anchor.role) {
            const isNeutral = neutralFamilies.has(family);
            const pool = Object.keys(out.schemes.light).filter((f) => neutralFamilies.has(f) === isNeutral && !claimed.has(f));
            const used = new Set(Object.values(outRoles));
            const byHue = (f) => hueGap(out.schemes.light[f][8].oklch[2], want[2]);
            const free = pool.filter((f) => !used.has(f));
            const pick = (free.length ? free : pool).sort((a, b) => byHue(a) - byHue(b))[0];
            if (!pick)
                continue;
            family = pick;
            outRoles[anchor.role] = family;
        }
        claimed.set(family, anchor.role);
        const lightRamp = out.schemes.light[family];
        const page = toneOf(lightRamp[0]);
        const lc = apcaLc(toneOfY(yOfHex(anchor.value)), page);
        // The step whose target is nearest the anchor's Lc (steps 2–12), unless the anchor names one.
        const step = anchor.step ?? 2 + targets.light.reduce((best, t, i) => (Math.abs(t - lc) < Math.abs(targets.light[best] - lc) ? i : best), 0);
        const at = lightRamp[step - 1];
        const before = deltaE(want, at.oklch);
        const ratio = at.oklch[1] > 1e-4 ? want[1] / at.oklch[1] : 1;
        // The dark color's step and chroma, when given: `key` reaches from there and is capped there.
        const darkRamp = out.schemes.dark[family];
        const wantD = anchor.dark ? srgbToOklch(anchor.dark) : undefined;
        const lcD = anchor.dark ? apcaLc(toneOfY(yOfHex(anchor.dark)), toneOf(darkRamp[0])) : 0;
        const stepD = anchor.dark ? anchor.darkStep ?? 2 + targets.dark.reduce((best, t, i) => (Math.abs(t - lcD) < Math.abs(targets.dark[best] - lcD) ? i : best), 0) : undefined;
        const reach = anchor.reach ?? (neutralFamilies.has(family) ? 'ramp' : 'key');
        const chroma = (C, n, anchored, cap) => {
            if (reach === 'ramp')
                return C * ratio;
            return n >= Math.min(KEY_FROM, anchored) ? Math.min(C * ratio, Math.max(cap, C)) : C * Math.min(1, ratio);
        };
        for (const sw of lightRamp)
            if (sw.step !== 1)
                setSwatch(sw, [sw.oklch[0], clampChroma(sw.oklch[0], chroma(sw.oklch[1], sw.step, step, want[1]), want[2], gamut), want[2]]); // the page keeps its tone and tint
        for (const sw of darkRamp)
            if (sw.step !== 1)
                setSwatch(sw, [sw.oklch[0], clampChroma(sw.oklch[0], chroma(sw.oklch[1], sw.step, stepD ?? KEY_FROM, wantD?.[1] ?? want[1]), wantD?.[2] ?? want[2], gamut), wantD?.[2] ?? want[2]]); // a dark color carries its own hue through the dark ramp
        settleKey(lightRamp, step, want, gamut);
        setSwatch(lightRamp[step - 1], want);
        if (step >= KEY_FROM)
            pins.light[family] = step;
        const below = step > 2 ? targets.light[step - 3] : 0, above = step < 12 ? targets.light[step - 1] : Infinity;
        // The dark color, when given: exact at its own step in the dark ramp.
        let dark;
        if (anchor.dark && wantD && stepD) {
            settleKey(darkRamp, stepD, wantD, gamut);
            setSwatch(darkRamp[stepD - 1], wantD);
            if (stepD >= KEY_FROM)
                pins.dark[family] = stepD;
            const lo = stepD > 2 ? targets.dark[stepD - 3] : 0, hi = stepD < 12 ? targets.dark[stepD - 1] : Infinity;
            dark = { value: anchor.dark, step: stepD, lc: Math.round(lcD * 10) / 10, target: targets.dark[stepD - 2], inOrder: lcD > lo && lcD < hi };
            if (stepD >= 8)
                solidSteps.dark[anchor.role] = stepD;
        }
        report.push({
            role: anchor.role, family, value: anchor.value, step, lc: Math.round(lc * 10) / 10, target: targets.light[step - 2],
            below, above, inOrder: lc > below && lc < above, inRange: lc <= targets.light[10] + 10 && lc >= targets.light[0] / 2,
            dE: Math.round(before * 10) / 10, ...(dark ? { dark } : {}),
        });
        if (step >= 8)
            solidSteps.light[anchor.role] = step;
    }
    // Surface anchors, last: the neutral family's ends, after any neutral anchor re-shaped it.
    const neutral = out.schemes.light[outRoles.neutral] ? outRoles.neutral : undefined;
    for (const anchor of anchors) {
        if (anchor.role !== 'ground' && anchor.role !== 'ink')
            continue;
        if (!neutral)
            continue;
        const [lightStep, darkStep] = anchor.role === 'ground' ? [1, 12] : [12, 1];
        const page = toneOf(data.schemes.light[neutral][0]);
        const lc = apcaLc(toneOfY(yOfHex(anchor.value)), page);
        const pin = (mode, step, hex) => {
            const ramp = out.schemes[mode][neutral], sw = ramp[step - 1], want = srgbToOklch(hex);
            if (step === 1)
                settleBase(ramp, want, gamut);
            else
                settleKey(ramp, step, want, gamut, true);
            setSwatch(sw, want);
            if (sw.hct)
                sw.hct[2] = toneOfY(yOf(want)); // the tone contrast reads
        };
        const before = deltaE(srgbToOklch(anchor.value), data.schemes.light[neutral][lightStep - 1].oklch);
        pin('light', lightStep, anchor.value);
        pin('dark', darkStep, anchor.dark ?? anchor.value);
        (out.strongInk ??= {})[anchor.role === 'ink' ? 'light' : 'dark'] = true; // headings use the brand's text color too
        report.push({
            role: anchor.role, family: neutral, value: anchor.value, step: lightStep, lc: Math.round(lc * 10) / 10, target: 0, below: 0, above: Infinity, inOrder: true, inRange: true,
            dE: Math.round(before * 10) / 10, dark: { value: anchor.dark ?? anchor.value, step: darkStep, lc: 0, target: 0, inOrder: true },
        });
    }
    return { data: out, roles: outRoles, report, solidSteps, pins };
}
/**
 * Steps between a pinned solid (9 or 10) and step 12 are derived from those two, not solved on their own:
 * an even blend (L and chroma linear, the pinned hue), so hover and text read as the same color moving toward 12,
 * never as a lighter, warmer hue (a dark-mode red drifting to coral). Runs last, after shapeKeys.
 */
export function deriveKeys(data, pins) {
    const gamut = data.settings?.target ?? 'display-p3';
    for (const mode of ['light', 'dark']) for (const [family, p] of Object.entries(pins?.[mode] || {})) {
        if (!(p >= KEY_FROM && p <= 10)) continue;
        const ramp = data.schemes[mode][family], a0 = ramp[p - 1].oklch, z = ramp[11].oklch, n = 12 - p;
        for (let k = 1; k < n; k++) { const t = k / n, L = a0[0] + (z[0] - a0[0]) * t, C = a0[1] + (z[1] - a0[1]) * t;
            setSwatch(ramp[p - 1 + k], [L, clampChroma(L, C, a0[2], gamut), a0[2]]); }
    }
    return data;
}
/**
 * With a ground or ink anchor, the neutral's middle steps (2–11) take their tint from those two colors instead of
 * from the tint source: each step keeps its solved lightness and blends the ground's and the ink's OKLab a/b by
 * where that lightness falls between them. The page, every surface and every text step then read as one family.
 */
export function deriveNeutral(data, family) {
    const gamut = data.settings?.target ?? 'display-p3';
    for (const mode of ['light', 'dark']) {
        const ramp = data.schemes[mode]?.[family]; if (!ramp) continue;
        const [La, Ca, Ha] = ramp[0].oklch, [Lz, Cz, Hz] = ramp[11].oklch, rad = Math.PI / 180;
        const aa = Ca * Math.cos(Ha * rad), ba = Ca * Math.sin(Ha * rad), az = Cz * Math.cos(Hz * rad), bz = Cz * Math.sin(Hz * rad);
        for (let s = 1; s < 11; s++) { const L = ramp[s].oklch[0], t = Math.min(1, Math.max(0, (L - La) / ((Lz - La) || 1)));
            const a = aa + (az - aa) * t, b = ba + (bz - ba) * t, C = Math.hypot(a, b), H = C < 1e-4 ? ramp[s].oklch[2] : ((Math.atan2(b, a) / rad) + 360) % 360;
            setSwatch(ramp[s], [L, clampChroma(L, C, H, gamut), H]); }
    }
    return data;
}
function yOfHex(color) {
    const p = parseAnchorColor(color);
    return p ? p.y : 0;
}
