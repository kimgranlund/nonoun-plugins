// Alpha ramps (Radix's transparent scales): for every family and step, the most transparent color that,
// composited over the scheme's page (neutral step 1), reproduces the solid step exactly. Over the page it
// is identical to the solid; over anything else it tints. Solved per channel in gamma-encoded sRGB, the
// space browsers composite in: each channel moves toward 0 or 1, the alpha is the largest any channel
// needs (rounded up to 1/1000), and the color is then solved for that alpha.
const cbrt3 = (x) => x * x * x;
export function oklchToSrgb([L, C, h]) {
    const a = C * Math.cos((h * Math.PI) / 180), b = C * Math.sin((h * Math.PI) / 180);
    const l = cbrt3(L + 0.3963377774 * a + 0.2158037573 * b), m = cbrt3(L - 0.1055613458 * a - 0.0638541728 * b), s = cbrt3(L - 0.0894841775 * a - 1.291485548 * b);
    const lin = [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s];
    return lin.map((c) => { c = Math.min(1, Math.max(0, c)); return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055; });
}
export function alphaOver(target, bg) {
    let a = 0;
    for (let i = 0; i < 3; i++) { const t = target[i], b = bg[i]; const need = t < b ? (b - t) / b : t > b ? (t - b) / (1 - b) : 0; if (need > a) a = need; }
    a = Math.min(1, Math.ceil(a * 1000) / 1000);
    if (a === 0) return { rgb: [0, 0, 0], alpha: 0 };
    const rgb = target.map((t, i) => Math.min(1, Math.max(0, bg[i] + (t - bg[i]) / a)));
    return { rgb, alpha: a };
}
const r4 = (x) => Math.round(x * 1e4) / 1e4;
export const alphaCss = ({ rgb, alpha }) => 'color(srgb ' + rgb.map(r4).join(' ') + ' / ' + alpha + ')';
/** { light: { family: [12 × { rgb, alpha, css }] }, dark: {…} } */
export function alphaRamps(data, page = 'neutral') {
    const out = {};
    for (const mode of ['light', 'dark']) {
        const sc = data.schemes[mode], bg = oklchToSrgb(sc[page][0].oklch);
        out[mode] = Object.fromEntries(Object.entries(sc).map(([f, ramp]) => [f, ramp.map((sw) => { const x = alphaOver(oklchToSrgb(sw.oklch), bg); return { ...x, css: alphaCss(x) }; })]));
    }
    return out;
}
