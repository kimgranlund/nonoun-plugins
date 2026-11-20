// @ts-check
/**
 * tree.context.js: the contexts the Svelte tree gives its items (docs/specs/targets.md, V4).
 *
 * An item registers itself with the nearest tree when it is created, which is in document order on the server and
 * in the browser alike, so the tree knows the first item marked selected while the items render. The level is a
 * second context: the tree gives 1, and each item one more to the items inside it, so an item knows its level
 * while it renders and the server markup carries it. A tree nested in an item gives 1 again.
 */

/** The key of the tree's context. */
export const TREE = Symbol('tree');
/** The key of the level an item renders. */
export const LEVEL = Symbol('tree-level');

/**
 * @typedef {{
 *   readonly el: HTMLElement | null,
 *   readonly selected: boolean,
 *   own: () => string | undefined,
 *   read: () => string,
 *   hasGroup: () => boolean,
 *   expanded: () => boolean,
 *   expand: (open: boolean, event: Event) => void,
 * }} TreeEntry
 *   An item as its tree sees it: `el` its root once mounted, `selected` its mark, `own` its value as it renders
 *   (undefined until it has read its label in the page, when it has no value prop), `read` its value as the page
 *   has it now, and its group and expanded state.
 * @typedef {{
 *   selects: (entry: TreeEntry) => boolean,
 *   add: (entry: TreeEntry) => void,
 *   remove: (entry: TreeEntry) => void,
 *   early: (entry: TreeEntry) => boolean,
 *   mark: (entry: TreeEntry, on: boolean) => void,
 *   renamed: (entry: TreeEntry, from: string, to: string) => void,
 * }} TreeContext
 *   `early` says whether the item was created with the tree, before it settled: the tree takes those marks itself.
 */
