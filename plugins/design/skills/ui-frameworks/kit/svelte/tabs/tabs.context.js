// @ts-check
/**
 * tabs.context.js: the context the Svelte tabs element gives its tab list, tabs and panels (docs/specs/targets.md, V4).
 *
 * A tab or a panel registers itself with the nearest tabs element when it is created, which is in document order
 * on the server and in the browser alike, so its position among its kind is known while it renders. A tab or a
 * panel with no value has that position as its value, as on the Web Component and in React.
 */

/** The key of the tabs element's context. */
export const TABS = Symbol('tabs');

/**
 * @typedef {{ readonly value?: string, readonly disabled?: boolean, readonly id?: string }} TabsEntry
 *   A tab or a panel as the tabs element sees it: getters over the component's own props.
 * @typedef {'tab' | 'tabpanel'} TabsKind
 * @typedef {{
 *   value: () => string,
 *   activation: () => 'automatic' | 'manual',
 *   choose: (value: string, event: Event) => void,
 *   add: (kind: TabsKind, entry: TabsEntry) => void,
 *   remove: (kind: TabsKind, entry: TabsEntry) => void,
 *   valueOf: (kind: TabsKind, entry: TabsEntry) => string,
 *   tabId: (value: string) => string, panelId: (value: string) => string,
 *   hasTab: (value: string) => boolean, hasPanel: (value: string) => boolean,
 * }} TabsContext
 */
