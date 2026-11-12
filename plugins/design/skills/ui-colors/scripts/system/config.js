import { DEFAULT_TARGETS, TARGET_MAX } from './contrast.js';
export const SPECTRUM_FIELDS = [
    { key: 'generator', label: 'Generator', group: 'Generator', options: ['hct', 'oklch'], labels: ['HCT', 'OKLCH'], value: 'hct' },
    { key: 'oklchChroma', label: 'OKLCH chroma', group: 'Generator', min: 0, max: 0.37, step: 0.005, value: 0.3 },
    { key: 'hueSet', label: 'Hues', group: 'Hues', options: ['quad', 'radix'], labels: ['Unique', 'Radix 25'], value: 'quad' },
    { key: 'quadStart', label: 'Unique start', group: 'Hues', options: ['radix', 'hue'], labels: ['Radix fit', 'First hue'], value: 'hue' },
    { key: 'hue', label: 'First hue', group: 'Hues', min: 0, max: 359, step: 1, value: 225 },
    { key: 'chroma', label: 'Requested chroma', group: 'Chroma', min: 4, max: 120, step: 1, value: 120 },
    { key: 'base', label: 'Base chroma %', group: 'Chroma', min: 0, max: 100, step: 1, value: 100 },
    { key: 'keyIntensity', label: 'Key intensity %', group: 'Chroma', min: 0, max: 300, step: 5, value: 100 },
    { key: 'keyDepth', label: 'Key depth (Lc)', group: 'Chroma', min: -30, max: 30, step: 1, value: 0 },
    { key: 'keyRamp', label: 'Key ramp-in (steps before 9)', group: 'Chroma', min: 0, max: 4, step: 1, value: 0 },
    { key: 'falloff', label: 'Chroma falloff', group: 'Chroma', min: 0.2, max: 5, step: 0.1, value: 1 },
    { key: 'keyC', label: 'Chroma distribution', group: 'Chroma', options: ['shared', 'radix'], labels: ['Shared', 'Radix'], value: 'radix' },
    { key: 'hb', label: 'Hue balance', group: 'Chroma', options: [0, 1], labels: ['Off', 'On'], value: 1 },
    { key: 'rc', label: 'Chroma origin', group: 'Chroma', options: [0, 1], labels: ['HCT zero', 'True gray'], value: 0 },
    // Hue correction (correct.ts): Material's DislikeAnalyzer lift and a warm hue shift for dark yellows.
    { key: 'yellowLift', label: 'Yellow lift %', group: 'Hue correction', min: 0, max: 100, step: 5, value: 0 },
    { key: 'warmShift', label: 'Warm shift °', group: 'Hue correction', min: 0, max: 30, step: 1, value: 0 },
    // Contrast (the Leonardo model, contrast.ts): the page tone per scheme (step 1) and an APCA Lc
    // target per step 2–12 against it; each step's tone is solved from its target.
    { key: 'darkTone', label: 'Dark page', group: 'Contrast', min: 0, max: 20, step: 0.5, value: 5 },
    { key: 'toneMax', label: 'Light page', group: 'Contrast', min: 80, max: 100, step: 0.5, value: 97.5 },
    { key: 'targetsLight', label: 'Light targets (Lc, steps 2–12)', group: 'Contrast', list: 11, min: 0, max: TARGET_MAX, step: 0.1, value: [...DEFAULT_TARGETS.light] },
    { key: 'targetsDark', label: 'Dark targets (Lc, steps 2–12)', group: 'Contrast', list: 11, min: 0, max: TARGET_MAX, step: 0.1, value: [...DEFAULT_TARGETS.dark] },
    // Legacy tone placement, superseded by the targets: a theme that sets them (and no targets) has its
    // targets measured from the ramp they produce (generateSpectrum).
    { key: 'ptAuto', label: 'Peak tone (legacy)', group: 'Legacy', options: [1, 0], labels: ['Auto', 'Manual'], value: 0, legacy: true },
    { key: 'pt', label: 'Manual peak tone (legacy)', group: 'Legacy', min: 20, max: 92, step: 0.5, value: 62, legacy: true },
    { key: 'ladder', label: 'Scale (legacy)', group: 'Legacy', options: ['even', 'radix'], labels: ['050–700', 'Radix 1–12'], value: 'even', legacy: true },
    { key: 'mat', label: 'Tinted neutral', group: 'Neutrals', options: ['none', 'tinted'], labels: ['Off', 'On'], value: 'tinted' },
    { key: 'tint', label: 'Neutral tint', group: 'Neutrals', min: 0, max: 100, step: 1, value: 75 },
    { key: 'neutralFrom', label: 'Neutral hue source', group: 'Neutrals', options: Array.from({ length: 12 }, (_, i) => i), value: 0 },
    { key: 'grays', label: 'Additional grays', group: 'Neutrals', options: ['Gray', 'Mauve', 'Slate', 'Sage', 'Olive', 'Sand'], multiple: true, value: [] },
    { key: 'radixGrays', label: 'Radix grays', group: 'Neutrals', options: ['Gray', 'Mauve', 'Slate', 'Sage', 'Olive', 'Sand'], multiple: true, value: ['Gray', 'Mauve', 'Slate', 'Sage', 'Olive', 'Sand'] },
    { key: 'harmony', label: 'Harmony', group: 'Harmony', options: ['off', 'analogous', 'complementary', 'split', 'triadic'], value: 'off' },
    { key: 'primary', label: 'Harmony primary', group: 'Harmony', options: Array.from({ length: 25 }, (_, i) => i), value: 0 },
    { key: 'secondary', label: 'Secondary accent', group: 'Harmony', options: Array.from({ length: 27 }, (_, i) => i - 2), value: -1 },
    { key: 'cvd', label: 'Vision simulation', group: 'Output', options: ['none', 'protan', 'deutan', 'tritan'], value: 'none' },
    { key: 'target', label: 'Gamut', group: 'Output', options: ['srgb', 'display-p3'], labels: ['sRGB', 'P3'], value: 'display-p3' },
];
export const SPECTRUM_DEFAULTS = Object.fromEntries(SPECTRUM_FIELDS.map((f) => [f.key, structuredClone(f.value)]));
/** Fixed engine parameters (not editable). */
export const SPECTRUM_FIXED = { peak: 400, lc: 100 };
const valid = (f, v) => f.list
    ? Array.isArray(v) && v.length === f.list && v.every((x) => typeof x === 'number' && Number.isFinite(x) && x >= f.min && x <= f.max)
    : f.multiple
        ? Array.isArray(v) && new Set(v).size === v.length && v.every((x) => f.options.includes(x))
        : f.options ? f.options.includes(v)
            : typeof v === 'number' && Number.isFinite(v) && v >= f.min && v <= f.max && Math.abs((v - f.min) / f.step - Math.round((v - f.min) / f.step)) < 1e-7;
/** Defaults + overrides, validated field by field. Unknown keys and invalid values throw. */
export function normalizeSpectrum(raw = {}) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw))
        throw new Error('Color settings must be an object');
    const out = { ...structuredClone(SPECTRUM_DEFAULTS) };
    for (const [k, v] of Object.entries(raw)) {
        const f = SPECTRUM_FIELDS.find((x) => x.key === k);
        if (!f)
            throw new Error(`Unknown spectrum setting: ${k}`);
        if (!valid(f, v))
            throw new Error(`Invalid spectrum setting: ${k}`);
        out[k] = v;
    }
    return out;
}
/** Only the settings that differ from the defaults (what a saved theme needs to keep). */
export const spectrumOverrides = (s) => Object.fromEntries(Object.entries(s).filter(([k, v]) => JSON.stringify(v) !== JSON.stringify(SPECTRUM_DEFAULTS[k])));
/** HCT hue of each Radix family at step 9, used to resolve a requested family by hue. */
export const RADIX_HUES = {
    gold: 79, bronze: 43, brown: 59, yellow: 101, amber: 84, orange: 44, tomato: 31, red: 20, ruby: 12, crimson: 2, pink: 349, plum: 328,
    purple: 312, violet: 295, iris: 286, indigo: 275, blue: 258, cyan: 224, teal: 184, jade: 173, green: 160, grass: 149, lime: 127, mint: 181, sky: 218,
};
