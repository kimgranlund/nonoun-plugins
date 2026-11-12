// Contrast-targeted ramps (the Leonardo model): each step's tone is solved from a contrast target
// against the page, per scheme. Step 1 is the page itself (the light or dark page tone); steps 2–12
// take APCA Lc targets. The engine still decides hue, chroma, gamut and neutrals; only where each
// step sits in lightness comes from here (index.ts passes the tones through the engine's tone map).
/** Relative luminance from an HCT tone (CIE L*). */
export const luminance = (tone) => (tone > 8 ? ((tone + 16) / 116) ** 3 : tone / 903.2963);
/**
 * APCA Lc magnitude of a tone against a background tone, achromatic and without APCA's low-contrast
 * clamp (so it stays monotonic down to the faintest surface steps).
 */
export function apcaLc(textTone, bgTone) {
    const clamp = (y) => (y > 0.022 ? y : y + (0.022 - y) ** 1.414);
    const yt = clamp(luminance(textTone)), yb = clamp(luminance(bgTone));
    return Math.abs(yb > yt ? (yb ** 0.56 - yt ** 0.57) * 114 : (yb ** 0.65 - yt ** 0.62) * 114);
}
/** The tone reaching `lc` against the page: darker than a light page, lighter than a dark one (bisection). */
export function toneForLc(page, lc, mode) {
    let lo = mode === 'light' ? 0 : page, hi = mode === 'light' ? page : 100;
    for (let i = 0; i < 40; i++) {
        const mid = (lo + hi) / 2, c = apcaLc(mid, page);
        // Light: contrast grows as the tone falls; dark: as it rises.
        if (mode === 'light' ? c > lc : c < lc)
            lo = mid;
        else
            hi = mid;
    }
    return (lo + hi) / 2;
}
/** The 12 step tones of a scheme: the page, then one tone per target (steps 2–12), kept strictly ordered. */
export function stepTones(page, targets, mode) {
    const tones = [page, ...targets.map((lc) => toneForLc(page, lc, mode))];
    for (let i = 1; i < tones.length; i++) {
        const min = 0.01;
        if (mode === 'light' ? tones[i] > tones[i - 1] - min : tones[i] < tones[i - 1] + min)
            tones[i] = tones[i - 1] + (mode === 'light' ? -min : min);
    }
    return tones;
}
/** The least Lc between step 9 and step 8, and between step 9 and step 12, when depth moves the run. */
const DEPTH_GAP = { base: 1, top: 6 };
/**
 * Targets with the run of steps 9–12 moved by `depth`, in Lc at step 9: positive is a darker solid in
 * both schemes, which is where the gamut has room for more chroma. Step 12 stays and steps 10–11 follow
 * in proportion, except that step 11, the text step, only ever gains contrast. Steps 2–8 don't move, so step 8 is the limit toward the page.
 */
export function deepenKeys(targets, depth, mode) {
    const t8 = targets[6], t9 = targets[7], t12 = targets[10], want = t9 + (mode === 'light' ? depth : -depth);
    const moved = Math.min(Math.max(want, t8 + DEPTH_GAP.base), t12 - DEPTH_GAP.top);
    return targets.map((t, i) => {
        if (i < 7)
            return t;
        const placed = moved + ((t - t9) * (t12 - moved)) / (t12 - t9);
        return i === 9 ? Math.max(t, placed) : placed; // step 11 is body text: it never gives up contrast
    });
}
/**
 * Default targets (steps 2–12, APCA Lc against the page): a gap curve, each step's gap a fixed amount wider
 * than the last (light from 5.5, dark from 3), so no step jumps at either end. Step 11 clears body text (75).
 */
export const DEFAULT_TARGETS = {
    light: [5.5, 11.6, 18.4, 25.8, 33.8, 42.4, 51.7, 61.6, 72.1, 83.2, 95],
    dark: [3, 7.1, 12.2, 18.4, 25.7, 34.1, 43.5, 54, 65.6, 78.3, 92],
};
export const TARGET_MAX = 108;
