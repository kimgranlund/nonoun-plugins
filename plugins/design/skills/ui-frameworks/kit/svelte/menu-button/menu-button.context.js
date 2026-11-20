// @ts-check
/**
 * menu-button.context.js: what a Svelte menu button gives the menu inside it (docs/specs/targets.md, V4).
 *
 * The menu button sets it with setContext(KEY, …); its menu reads it with getContext(KEY). `open` is a getter
 * over the menu button's $bindable prop, so reading it in an effect tracks it.
 */

/**
 * @typedef {{
 *   readonly open: boolean,
 *   setOpen: (open: boolean) => void,
 *   trigger: () => HTMLElement | null,
 * }} MenuButtonState
 */

/** The context key of the menu button family. */
export const KEY = Symbol('menu-button');
