// @ts-check
/**
 * listbox.context.js: the context the Svelte listbox gives its options (docs/specs/targets.md, V4).
 *
 * It serves the first render only, on the server and at mount: an option registers itself as it is created, in
 * document order, with its value prop and the `selected` it starts with, so that the listbox can render the hidden
 * inputs of a value that is known before the DOM is, and an option can render its first aria-selected. Once
 * mounted the DOM decides, as on the Web Component: the listbox reads its options' values and `selected` from the
 * DOM, whoever wrote them (a script, a combobox, a select).
 */

/** The key of the listbox's context. */
export const LISTBOX = Symbol('listbox');

/**
 * @typedef {{ readonly value?: string, readonly selected: boolean }} ListboxEntry
 *   An option as the listbox sees it before the DOM is read: a getter over its value prop, and the selected it
 *   started with.
 * @typedef {{
 *   given: () => boolean,
 *   chosen: () => string[],
 *   add: (entry: ListboxEntry) => void,
 *   remove: (entry: ListboxEntry) => void,
 * }} ListboxContext
 *   `given` says whether the listbox's value is known (given as a prop, or taken from the DOM once mounted);
 *   `chosen` returns the values it names.
 */
