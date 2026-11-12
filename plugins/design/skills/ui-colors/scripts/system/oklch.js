// The OKLCH generator (color.spectrum.generator: 'oklch'): the same ramps the HCT engine produces,
// with none of its runtime. Twelve hues sit every 33.3 units of hue quadrature from the first hue, each
// at one OKLCH hue angle. Chroma follows one envelope, peaking at step 9 and shared by every hue: the
// requested chroma, capped by what the weakest hue can reach there. Lightness keeps the kit's contrast
// model: each step's L is solved per hue and chroma to land on that step's tone (contrast.ts), so a
// step has the same APCA contrast in every family, as it does under HCT.
import { clampChroma, css, linearY, onFill, solveLightness, toneOfY } from './anchors.js';
import { apcaLc, luminance, stepTones } from './contrast.js';
/** CAM16 unique hues measured in OKLCH: hue angle h, eccentricity e, quadrature H (red … red). */
const UNIQUE = [{ h: 21.8, e: 0.8, H: 0 }, { h: 88.8, e: 0.7, H: 100 }, { h: 160.6, e: 1, H: 200 }, { h: 237.5, e: 1.2, H: 300 }, { h: 381.8, e: 0.8, H: 400 }];
/** Family names, in hue order from the first hue: the HCT engine's, so roles resolve the same way. */
const FAMILIES = ['cyan', 'indigo', 'plum', 'crimson', 'tomato', 'orange', 'amber', 'yellow', 'lime', 'grass', 'jade', 'teal'];
/** The neutral's chroma at full tint, as a share of the accents'. */
const NEUTRAL_SHARE = 0.2;
/** Hue quadrature H (0–400) of an OKLCH hue angle. */
export function quadratureOf(h) {
    const hp = h < UNIQUE[0].h ? h + 360 : h;
    let i = 0;
    while (i < 3 && hp >= UNIQUE[i + 1].h)
        i++;
    const a = (hp - UNIQUE[i].h) / UNIQUE[i].e, b = (UNIQUE[i + 1].h - hp) / UNIQUE[i + 1].e;
    return UNIQUE[i].H + (100 * a) / (a + b);
}
function hueOfQuadrature(H) {
    const q = ((H % 400) + 400) % 400, i = Math.min(3, Math.floor(q / 100));
    const { h: hi, e: ei, H: Hi } = UNIQUE[i], { h: hj, e: ej } = UNIQUE[i + 1];
    const h = ((q - Hi) * (ej * hi - ei * hj) - 100 * hi * ej) / ((q - Hi) * (ej - ei) - 100 * ej);
    return ((h % 360) + 360) % 360;
}
/** The OKLCH L of a gray at this tone. */
const grayL = (tone) => Math.cbrt(luminance(tone));
/** Max in-gamut OKLCH chroma at a hue, at the L of a gray of this tone. */
export const oklchBoundary = (hue, tone, target) => clampChroma(grayL(tone), 0.5, hue, target);
/** The L that puts this hue and chroma on a tone. */
const solveL = (tone, C, h, gamut) => solveLightness(luminance(tone), C, h, gamut);
/** The most chroma a hue can hold on a tone: the solved L shifts with chroma, so the two are found together. */
function reachOnTone(tone, h, gamut) {
    let lo = 0, hi = 0.5;
    for (let i = 0; i < 16; i++) {
        const C = (lo + hi) / 2;
        if (clampChroma(solveL(tone, C, h, gamut), C, h, gamut) >= C - 1e-5)
            lo = C;
        else
            hi = C;
    }
    return lo;
}
export function generateOklch(s) {
    const gamut = String(s.target);
    const H0 = quadratureOf(s.hue);
    const accents = FAMILIES.map((name, i) => ({ name, h: hueOfQuadrature(H0 + (i * 400) / 12) }));
    const tones = { light: stepTones(s.toneMax, s.targetsLight, 'light'), dark: stepTones(s.darkTone, s.targetsDark, 'dark') };
    const peak = { light: tones.light[8], dark: tones.dark[8] };
    const shared = Math.min(s.oklchChroma, ...accents.map((a) => reachOnTone(peak.light, a.h, gamut)));
    const tint = s.mat === 'tinted' ? (s.tint / 100) * NEUTRAL_SHARE : 0;
    const neutral = { name: 'neutral', h: accents[s.neutralFrom].h };
    /** The envelope at a step: 1 at the peak, falling to 0 at the page and at the far end of the scale. */
    const envelope = (mode, i) => {
        const t = tones[mode][i], p = peak[mode], page = tones[mode][0];
        const end = i < 8 ? page : mode === 'light' ? 0 : 100;
        return 1 - (Math.abs(t - p) / Math.abs(end - p)) ** s.falloff;
    };
    const ramp = (family, base, mode) => tones[mode].map((tone, i) => {
        const C = shared * base * envelope(mode, i);
        const L = solveL(tone, C, family.h, gamut);
        const lch = [L, clampChroma(L, C, family.h, gamut), family.h];
        return { step: i + 1, stop: i + 1, css: css(lch), oklch: lch, hct: [family.h, lch[1], toneOfY(linearY(lch))], apca: onFill(lch) };
    });
    const scheme = (mode) => Object.fromEntries([
        ...accents.map((a) => [a.name, ramp(a, 1, mode)]),
        [neutral.name, ramp(neutral, tint, mode)],
    ]);
    const schemes = { light: scheme('light'), dark: scheme('dark') };
    const checks = (mode) => ({
        peakTone: peak[mode],
        rows: Object.fromEntries(Object.entries(schemes[mode]).map(([name, r]) => {
            const lc = (n) => Math.round(apcaLc(r[n - 1].hct[2], r[0].hct[2]) * 10) / 10;
            const roles = { r11: lc(11), r12: lc(12) };
            return [name, { roles, passes: { r11: roles.r11 >= 60, r12: roles.r12 >= 75 } }];
        })),
    });
    const names = accents.map((a) => a.name);
    return {
        settings: { ...s },
        schemes,
        checks: { light: checks('light'), dark: checks('dark') },
        metadata: { light: { accents: names, neutrals: [neutral.name], pairs: Object.fromEntries(names.map((n) => [n, { accent: n, neutral: neutral.name }])) } },
    };
}
