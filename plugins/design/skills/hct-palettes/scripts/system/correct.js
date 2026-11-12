// Hue correction for dark yellows (Material Color Utilities' DislikeAnalyzer, adapted to ramps).
// Contrast targets give every hue the same tone per step, and yellow only reaches high chroma at high
// tone, so its solids and text (9–12) read olive. Two fixes, weighted by closeness to yellow
// (HCT hue ~100, fading to 0 by ~70 and ~130 so amber and lime move less and orange/green not at all):
//   yellowLift (0–100 %): lifts step 9 toward tone 70, as fixIfDisliked does for a disliked key color
//     (HCT hue 90–111, chroma > 16, tone < 65); steps 10–11 follow by ¾ and ¼, and steps 9–11 gain up to
//     35 % chroma (a lighter yellow holds more). In light mode step 8 moves up with step 9 to keep order.
//   warmShift (0–30°): rotates the family toward the warm side (lower OKLCH hue, toward amber): steps
//     1–8 by 0.6, steps 9–12 by 0.5, 0.65, 0.8 and all of the shift, at constant luminance, so dark yellows read warm brown, not khaki.
import { clampChroma, css, onFill, linearY, toneOfY, solveLightness } from './anchors.js';
import { luminance } from './contrast.js';
const CENTER = 100, HALF = 30;
const parse = (sw) => sw.oklch ?? (sw.css.match(/oklch\(([\d.]+) ([\d.]+) ([\d.]+)\)/) || []).slice(1, 4).map(Number);
export const yellowWeight = (hctHue) => { const d = Math.abs(((hctHue - CENTER + 540) % 360) - 180); return d >= HALF ? 0 : Math.cos((Math.PI / 2) * (d / HALF)) ** 2; };
function place(sw, tone, hue, gamut, dh = 0, boost = 1) {
    const C = parse(sw)[1] * boost, L = solveLightness(luminance(tone), C, hue, gamut), lch = [+L.toFixed(4), +clampChroma(L, C, hue, gamut).toFixed(4), +hue.toFixed(4)];
    sw.oklch = lch; sw.css = css(lch); sw.apca = onFill(lch);
    if (sw.hct) sw.hct = [(sw.hct[0] + dh + 360) % 360, sw.hct[1], toneOfY(linearY(lch))];
}
export function correctHues(data, s = {}) {
    const lift = (s.yellowLift ?? 0) / 100, warm = s.warmShift ?? 0, gamut = String(s.target ?? data.settings?.target ?? 'display-p3');
    data.settings = { ...data.settings, yellowLift: s.yellowLift ?? 0, warmShift: warm };
    if (!lift && !warm) return data;
    const accents = data.metadata?.light.accents ?? Object.keys(data.schemes.light);
    for (const mode of ['light', 'dark']) for (const name of accents) {
        const r = data.schemes[mode][name], w = yellowWeight(r[8].hct ? r[8].hct[0] : parse(r[8])[2] - 5);
        if (!w) continue;
        const tone = (i) => r[i].hct ? r[i].hct[2] : toneOfY(linearY(parse(r[i])));
        const t8 = tone(7), t9 = tone(8), dir = mode === 'light' ? -1 : 1;
        const d9 = lift && t9 < 65 ? (70 - t9) * lift * w : 0, boost = 1 + 0.35 * lift * w;
        // Light mode: step 8 moves up with step 9 so the ramp keeps its order (step 7 is its ceiling).
        if (d9 && dir < 0 && t8 < t9 + d9 + 3) place(r[7], Math.min(tone(6) - 1.5, t9 + d9 + 3), parse(r[7])[2], gamut, 0, 1 + 0.2 * lift * w);
        // Tints and borders (1–8) read greenish at high tone: they take 60 % of the shift.
        for (let i = 0; i < 8; i++) if (warm) place(r[i], tone(i), (parse(r[i])[2] - warm * w * 0.6 + 360) % 360, gamut, -warm * w * 0.6);
        [[8, d9, 0.5, boost], [9, d9 * 0.75, 0.65, boost], [10, d9 * 0.25, 0.8, 1 + 0.15 * lift * w], [11, 0, 1, 1]].forEach(([i, dt, k, bo]) => {
            const dh = -warm * w * k; if (!dt && !dh && bo === 1) return;
            place(r[i], tone(i) + dt, (parse(r[i])[2] + dh + 360) % 360, gamut, dh, bo);
        });
    }
    return data;
}
