// HCT and OKLCH of an sRGB hex, for named.mjs. HCT is CAM16 hue and chroma under the default viewing conditions (D65,
// 200/pi * Y(L* 50) / 100 adapting luminance, L* 50 background, average surround, no discounting) with CIE L* as tone,
// the HCT definition the vendored engine uses; the engine itself exposes no hex-to-HCT function.
const WHITE = [95.047, 100, 108.883];
const SRGB2XYZ = [[0.41233895, 0.35762064, 0.18051042], [0.2126, 0.7152, 0.0722], [0.01932141, 0.11916382, 0.95034478]];
const XYZ2CAT = [[0.401288, 0.650173, -0.051461], [-0.250268, 1.204414, 0.045854], [-0.002079, 0.048952, 0.953127]];
const M3 = (M, v) => M.map((r) => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]);
const labInvf = (ft) => { const e = 216 / 24389, k = 24389 / 27, f3 = ft ** 3; return f3 > e ? f3 : (116 * ft - 16) / k; };
const labF = (t) => { const e = 216 / 24389, k = 24389 / 27; return t > e ? Math.cbrt(t) : (k * t + 16) / 116; };
const yFromLstar = (L) => 100 * labInvf((L + 16) / 116);
const VC = (() => {
  const La = (200 / Math.PI) * yFromLstar(50) / 100, f = 1, c = 0.69, nc = f;
  const w = M3(XYZ2CAT, WHITE), d = Math.min(1, Math.max(0, f * (1 - (1 / 3.6) * Math.exp((-La - 42) / 92))));
  const rgbD = w.map((x) => d * (100 / x) + 1 - d), k = 1 / (5 * La + 1), k4 = k ** 4, k4F = 1 - k4;
  const fl = k4 * La + 0.1 * k4F * k4F * Math.cbrt(5 * La), n = yFromLstar(50) / WHITE[1], z = 1.48 + Math.sqrt(n), nbb = 0.725 / n ** 0.2;
  const rgbA = w.map((x, i) => { const p = (fl * rgbD[i] * x / 100) ** 0.42; return 400 * p / (p + 27.13); });
  return { c, nc, rgbD, fl, n, z, nbb, ncb: nbb, aw: (2 * rgbA[0] + rgbA[1] + 0.05 * rgbA[2]) * nbb };
})();
export const parseHex = (hex) => { const m = /^#?([0-9a-f]{6})$/i.exec(hex); if (!m) throw new Error(`not a 6-digit hex: ${hex}`); return [0, 2, 4].map((i) => parseInt(m[1].slice(i, i + 2), 16) / 255); };
const lin = (v) => (v <= 0.040449936 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
/** [hue 0-360, chroma, tone 0-100] of an sRGB hex. */
export function hctOfHex(hex) {
  const xyz = M3(SRGB2XYZ, parseHex(hex).map((v) => lin(v) * 100)), { rgbD, fl, nbb, ncb, aw, c, z, nc, n } = VC;
  const rA = M3(XYZ2CAT, xyz).map((x, i) => { const v = rgbD[i] * x, p = (fl * Math.abs(v) / 100) ** 0.42; return Math.sign(v) * 400 * p / (p + 27.13); });
  const a = (11 * rA[0] - 12 * rA[1] + rA[2]) / 11, b = (rA[0] + rA[1] - 2 * rA[2]) / 9;
  const u = (20 * rA[0] + 20 * rA[1] + 21 * rA[2]) / 20, p2 = (40 * rA[0] + 20 * rA[1] + rA[2]) / 20;
  let hue = Math.atan2(b, a) * 180 / Math.PI; hue = ((hue % 360) + 360) % 360;
  const j = 100 * ((p2 * nbb) / aw) ** (c * z), hp = hue < 20.14 ? hue + 360 : hue, eHue = 0.25 * (Math.cos(hp * Math.PI / 180 + 2) + 3.8);
  const t = (50000 / 13) * eHue * nc * ncb * Math.hypot(a, b) / (u + 0.305), chroma = t ** 0.9 * (1.64 - 0.29 ** n) ** 0.73 * Math.sqrt(j / 100);
  return [hue, chroma, 116 * labF(xyz[1] / 100) - 16];
}
/** [L 0-1, C, H 0-360] of an sRGB hex (OKLab, Ottosson's matrices). */
export function oklchOfHex(hex) {
  const [r, g, b] = parseHex(hex).map(lin);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b), m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b), s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s, A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s, B = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
  const C = Math.hypot(A, B); let H = Math.atan2(B, A) * 180 / Math.PI; if (H < 0) H += 360;
  return [L, C, C < 1e-4 ? 0 : H];
}
