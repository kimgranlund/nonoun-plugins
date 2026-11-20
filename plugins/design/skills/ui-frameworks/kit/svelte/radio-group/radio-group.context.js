// @ts-check
/**
 * radio-group.context.js: the context the Svelte radio group gives its radios (docs/specs/targets.md, V4).
 *
 * A radio registers itself with the nearest radio group when it is created, which is in document order on the
 * server and in the browser alike, so its position among the group's radios is known while it renders. A radio
 * with no value has that position as its value, as on the Web Component and in React.
 */

/** The key of the radio group's context. */
export const RADIO_GROUP = Symbol('radio-group');

/**
 * @typedef {{ readonly value?: string, readonly checked?: boolean }} RadioEntry
 *   A radio as the group sees it: getters over the radio's own props.
 * @typedef {{
 *   name: () => string,
 *   anonymous: () => boolean,
 *   value: () => string,
 *   disabled: () => boolean,
 *   required: () => boolean,
 *   add: (entry: RadioEntry) => void,
 *   remove: (entry: RadioEntry) => void,
 *   valueOf: (entry: RadioEntry) => string,
 *   input: (value: string, event: Event) => void,
 *   change: (value: string, event: Event) => void,
 *   invalid: (event: Event) => void,
 * }} RadioGroupContext
 */
