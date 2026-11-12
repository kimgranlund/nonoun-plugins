// Color roles and the semantic steps, shadows and selection fills built on them: plain data, no
// generation engine, so a module that only names roles never loads the engine's 264 KB runtime.
export const BRAND_ROLES = ['primary', 'secondary', 'neutral'];
export const FEEDBACK_ROLES = ['critical', 'warning', 'success', 'info'];
export const DATA_ROLES = ['data1', 'data2', 'data3', 'data4', 'data5', 'data6'];
export const ROLE_NAMES = [...BRAND_ROLES, ...FEEDBACK_ROLES, ...DATA_ROLES];
/** Anchors that pin the neutral ramp's ends instead of a role's family: the page (step 1) and the ink (step 12). */
export const SURFACE_ROLES = ['ground', 'ink'];
export const ANCHOR_ROLES = [...ROLE_NAMES, ...SURFACE_ROLES];
export const DEFAULT_ROLES = {
    primary: 'indigo', secondary: 'amber', neutral: 'neutral',
    critical: 'red', warning: 'yellow', success: 'green', info: 'cyan',
    data1: 'indigo', data2: 'cyan', data3: 'grass', data4: 'amber', data5: 'tomato', data6: 'plum',
};
/** A ramp family's token name: its own, except the neutral family, since `neutral` names the role (--colors-neutral-12 aliases a ramp step). */
export const rampName = (family) => (family === 'neutral' ? 'gray' : family);
/** The CSS variable of a ramp step, as `var()`-less text. */
export const rampVar = (family, step) => `--colors-${rampName(family)}-${step}`;
/** Round the numbers in a color string to 4 decimals (well below a visible difference). */
export const trimColor = (css) => css.replace(/-?\d*\.\d+/g, (n) => String(Number(Number(n).toFixed(4))));
/** Brand and feedback roles: each gets the same semantic steps and its whole ramp. */
export const SCALE_ROLES = [...BRAND_ROLES, ...FEEDBACK_ROLES];
/** Semantic steps every scale role carries (Radix step semantics). */
export const SEMANTIC_STEPS = { solid: 9, 'solid-hover': 10, subtle: 3, 'subtle-hover': 4, border: 7, fg: 11 };
const UNIFORM_STEPS = Object.fromEntries(SCALE_ROLES.flatMap((role) => [
    ...Object.entries(SEMANTIC_STEPS).map(([name, step]) => [`${role}-${name}`, [role, step]]),
    ...Array.from({ length: 12 }, (_, i) => [`${role}-${i + 1}`, [role, i + 1]]),
]));
/**
 * Role -> [family role, step], Radix step semantics. Shared by the kit tokens and spectrumCSS.
 * One name per role: <role>-solid, -solid-hover, -subtle, -subtle-hover, -border, -fg and <role>-1…12
 * for primary, secondary, neutral, critical, warning, success and info; data-1…6; plus the page roles.
 */
export const ROLE_STEPS = {
    'bg': ['neutral', 1], 'bg-subtle': ['neutral', 2], 'bg-muted': ['neutral', 3],
    'bg-muted-hover': ['neutral', 4], 'bg-muted-active': ['neutral', 5],
    // Control fills (the neutral button): neutral 12 as a translucent layer, so a control reads on any
    // surface (page, muted panel, card). On the page tone they match neutral 3 / 4 / 5.
    'bg-control': ['neutral', 12, { alpha: 0.12, darkAlpha: 0.2 }],
    'bg-control-hover': ['neutral', 12, { alpha: 0.19, darkAlpha: 0.29 }],
    'bg-control-active': ['neutral', 12, { alpha: 0.25, darkAlpha: 0.39 }],
    // Floating layers (menus, popovers, dialogs, drawers): the page tone in light, one step up in dark,
    // where shadows barely read. Tooltips invert; the backdrop dims the page in both schemes.
    // The selected option of a listbox or segmented control: the lightest neutral in light, the primary
    // solid in dark (its text is fg-selected: neutral 12 in light, the solid's contrast color in dark).
    'bg-selected': ['neutral', 1, { dark: 9, darkFamily: 'primary' }],
    'bg-inverse': ['neutral', 12], 'fg-inverse': ['neutral', 1],
    'bg-backdrop': ['neutral', 12, { dark: 1, alpha: 0.4, darkAlpha: 0.7 }],
    'fg': ['neutral', 12], 'fg-muted': ['neutral', 11],
    // Placeholders and other hints that must read as absent content: well below muted text.
    'fg-subtle': ['neutral', 10],
    'border': ['neutral', 6], 'border-strong': ['neutral', 7],
    // The edge of an outline or filled control: its only boundary, so ≥ 3:1 on the ground (WCAG 1.4.11).
    'control-border': ['neutral', 8],
    ...UNIFORM_STEPS,
    // The scheme's shadow color (shadows.sm, shadows.md mix it with transparent): neutral 12 in light,
    // the darkest neutral in dark, where the shadow alphas are stronger.
    'shadow': ['neutral', 12, { dark: 1, alpha: 0.14, darkAlpha: 0.6 }], // pre-mixed alpha: `0 2px 8px var(--colors-shadow)` is a soft lift, never a solid edge
    // Data series: the step-9 solid of each data family.
    'data-1': ['data1', 9], 'data-2': ['data2', 9], 'data-3': ['data3', 9], 'data-4': ['data4', 9], 'data-5': ['data5', 9], 'data-6': ['data6', 9],
    // One ring everywhere (toned and invalid controls too): primary step 11, ≥ 3:1 on the ground in both schemes.
    'focus-ring': ['primary', 11],
};
/**
 * Compound shadows (Material's key-light umbra and penumbra plus an ambient layer), continuous in the
 * elevation e (dp): each layer's offset, blur and spread are px per dp, fitted to Material's tables
 * at 2, 8 and 24dp, so any elevation is valid. Colored by the `shadow` role (neutral 12 in light, the
 * darkest neutral in dark: tinted, never black) at a per-scheme alpha, stronger in dark where a
 * shadow has less page to darken.
 */
export const SHADOW_LAYERS = {
    umbra: { y: 0.5, blur: 0.6, spread: -0.3, light: 0.14, dark: 0.5 },
    penumbra: { y: 1, blur: 1.6, spread: 0.125, light: 0.1, dark: 0.36 },
    ambient: { y: 0.4, blur: 1.9, spread: 0.33, light: 0.08, dark: 0.3 },
};
/** The base shadows' elevations (small lifts inside components: a selected option, a range thumb). */
export const SHADOW_DP = { sm: 1, md: 3 };
/** The three layers at elevation e: px offsets, blur and spread, and the per-scheme alphas. */
export const shadowAt = (e) => Object.entries(SHADOW_LAYERS).map(([layer, l]) => ({ layer, y: l.y * e, blur: l.blur * e, spread: l.spread * e, light: e > 0 ? l.light : 0, dark: e > 0 ? l.dark : 0 }));
/** The base shadows as layers (the DTCG export). */
export const SHADOWS = { sm: shadowAt(SHADOW_DP.sm), md: shadowAt(SHADOW_DP.md) };
/** Family, step and alpha (1 = opaque) of a role in one scheme. */
export function roleStep(entry, mode) {
    const [family, step, o = {}] = entry;
    const dark = mode === 'dark';
    return { family: (dark && o.darkFamily) || family, step: (dark && o.dark) || step, alpha: (dark ? o.darkAlpha ?? o.alpha : o.alpha) ?? 1 };
}
/** CSS for a role from a ramp-step reference (a var() or a token reference). */
export const withAlpha = (ref, alpha) => alpha === 1 ? ref : `color-mix(in oklch, ${ref} ${Math.round(alpha * 100)}%, transparent)`;
/**
 * The selection fills (bg-selected, fg-selected) follow the theme's emphasis (--ui-emphasis 0–2),
 * mixed in CSS from role variables so a theme or scope changes them live. Light: neutral 3 (quiet),
 * neutral 1 (balanced), primary 3 (loud), text neutral 12. Dark: neutral 4 with neutral 12 text
 * (quiet), else the primary solid with its contrast text. `ref(role)` names a role variable.
 */
export function selectionVars(mode, ref = (r) => `var(--colors-${r})`) {
    const e = 'var(--ui-emphasis, 1)';
    const low = `calc(clamp(0, ${e}, 1) * 100%)`, high = `calc(clamp(0, ${e} - 1, 1) * 100%)`;
    return mode === 'light'
        ? { 'bg-selected': `color-mix(in oklch, color-mix(in oklch, ${ref('neutral-3')}, ${ref('neutral-1')} ${low}), ${ref('primary-3')} ${high})`, 'fg-selected': ref('neutral-12') }
        // The primary solid (an anchored role's solid step, else 9), so its contrast text (fg-on-solid) matches.
        : { 'bg-selected': `color-mix(in oklch, ${ref('neutral-4')}, ${ref('primary-solid')} ${low})`, 'fg-selected': `color-mix(in oklch, ${ref('neutral-12')}, ${ref('fg-on-solid')} ${low})` };
}
/** The neutral step white and black take by default. */
export const DEFAULT_ENDPOINT = 3;
