// @ts-check
/**
 * toaster.context.js: the context the Svelte toaster gives the toasts inside it (docs/specs/targets.md, V4).
 *
 * The toaster finds its toasts in the DOM by role, as the Web Component and React do, and a MutationObserver
 * tells it of every change; but an observer reports after the task. A Svelte toast inside a toaster therefore
 * asks it to look again in the same flush, once its own `open` is in the page and when it goes, as React's
 * toaster looks again after each render of its children. The context carries nothing else: the toaster decides
 * from the DOM alone.
 */

/** The key of the toaster's context. */
export const TOASTER = Symbol('toaster');

/**
 * @typedef {{ look: () => void }} ToasterContext
 *   `look` shows the toaster while one of its children is an open toast, and hides it when none is.
 */
