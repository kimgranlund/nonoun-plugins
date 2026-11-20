// @ts-check
/**
 * menu-group.context.js: what a Svelte menu group gives the radio items inside it (docs/specs/targets.md, V4).
 *
 * The group sets it with setContext(GROUP, …); a radio item reads it with getContext(GROUP) and adds itself.
 * When the user chooses a radio item, the item tells the group, which turns every other radio item it holds off
 * (J22). A nested group sets its own; a submenu sets it to null, so the radio items of its menu belong to no group
 * around it.
 */

/**
 * @typedef {{ off: () => void }} MenuGroupEntry  A radio item as its group sees it: a way to turn it off.
 * @typedef {{
 *   add: (entry: MenuGroupEntry) => () => void,
 *   choose: (entry: MenuGroupEntry) => void,
 * }} MenuGroupState
 *   `add` returns the entry's removal; `choose` turns every entry but the one given off.
 */

/** The context key of the menu group. */
export const GROUP = Symbol('menu-group');
