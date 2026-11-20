// @ts-check
/**
 * tree-item.js: one item of a tree, for React (docs/specs/targets.md; rules J32 to J35 of docs/specs/patterns.md).
 *
 * The root is a <div role="treeitem">; it takes focus, and the tree's roving focus writes its tabindex, which it
 * never renders. Its row is the author's child marked `data-part="label"`, and the items inside it are in the
 * author's child marked `data-part="group"`; both are rendered as the author writes them, never cloned or
 * wrapped. It renders `aria-selected` ("true" or "false") from its tree's value, `aria-expanded` while it has a
 * group, `aria-disabled` and `aria-level`, so the server markup paints every state.
 *
 * `expanded` is controlled (expanded with onExpandedChange) or uncontrolled (defaultExpanded).
 * onExpandedChange(expanded, event) is called once when the user opens or closes the item, after the item is
 * written when it is uncontrolled. `selected` marks the item: it is read for the tree's first value, and a mark
 * that comes or goes later selects the item or clears the tree's value, as a script's mark does on the Web
 * Component. The tree's value decides which item is selected.
 *
 * Into the DOM, after each render and whenever its children change, and only where it differs, it writes what
 * belongs to the author's parts: the group role on a group that has no role, an id on a label that has none, and
 * `aria-labelledby` naming the label unless the author named the item: without it, the item's name would include
 * the text of every item in its group.
 */
import { createElement, useCallback, useContext, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { TreeContext, LevelContext, GROUP, LABEL, partOf, put, valueOfProps } from '../tree/tree.js';
import { role } from '../../components/tree-item/tree-item.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'defaultValue'> & {
 *   value?: string, selected?: boolean, expanded?: boolean, defaultExpanded?: boolean, disabled?: boolean,
 *   onExpandedChange?: (expanded: boolean, event: import('react').SyntheticEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} TreeItemProps
 */

/** @param {TreeItemProps} props */
function TreeItemRoot({ value, selected = false, expanded, defaultExpanded = false, onExpandedChange, disabled = false, children, ref, ...rest }) {
  const tree = useContext(TreeContext);
  const level = useContext(LevelContext);
  const key = useId();
  const [ownOpen, setOwnOpen] = useState(defaultExpanded);
  const controlled = expanded !== undefined;
  const isOpen = controlled ? expanded : ownOpen;
  // What the children say, then what the page says once they are in it: a part an author's component renders
  // is not among the children.
  const groupInChildren = Boolean(partOf(children, 'group'));
  const textInChildren = valueOfProps({ children });
  /** @type {[boolean | null, (next: boolean | null) => void]} */
  const [domGroup, setDomGroup] = useState(/** @type {boolean | null} */ (null));
  /** @type {[string | null, (next: string | null) => void]} */
  const [domText, setDomText] = useState(/** @type {string | null} */ (null));
  const hasGroup = domGroup ?? groupInChildren;
  const own = value ?? domText ?? textInChildren;
  const isSelected = tree ? tree.selects(key, own) : selected;

  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ value, isOpen, controlled, onExpandedChange, hasGroup, groupInChildren, textInChildren, domGroup, domText });
  latest.current = { value, isOpen, controlled, onExpandedChange, hasGroup, groupInChildren, textInChildren, domGroup, domText };
  /** @type {import('react').RefObject<string | null>} The aria-labelledby value this item wrote, so that it never replaces an author's. */
  const named = useRef(/** @type {string | null} */ (null));

  /** The item's value as the page has it: `value`, or else the trimmed text of its label. */
  const valueNow = useCallback(() => latest.current.value ?? (root.current?.querySelector(LABEL)?.textContent ?? '').trim(), []);

  /** Writes the author's parts' role, id and name, and reads the group and the label text back. */
  const sync = useCallback(() => {
    const el = root.current;
    if (!el) return;
    const group = el.querySelector(GROUP);
    if (group && !group.hasAttribute('role')) group.setAttribute('role', 'group');
    // A name the author gave stays (A2). One this item gave follows the label.
    const name = el.getAttribute('aria-labelledby');
    if (name === null || name === named.current) {
      const label = el.hasAttribute('aria-label') ? null : el.querySelector(LABEL);
      if (label && !label.id) label.id = `${key}label`;
      named.current = label ? label.id : null;
      put(el, 'aria-labelledby', named.current);
    }
    const now = latest.current;
    const wantGroup = Boolean(group) === now.groupInChildren ? null : Boolean(group);
    const text = (el.querySelector(LABEL)?.textContent ?? '').trim();
    const wantText = text === now.textInChildren ? null : text;
    return wantGroup !== now.domGroup || wantText !== now.domText ? { wantGroup, wantText } : undefined;
  }, [key]);

  // Opens or closes the item because the user asked, through the tree's keys or a click on the label.
  const expand = useCallback((/** @type {boolean} */ next, /** @type {import('react').SyntheticEvent} */ event) => {
    const now = latest.current;
    if (now.controlled) now.onExpandedChange?.(next, event);
    else {
      flushSync(() => setOwnOpen(next));
      now.onExpandedChange?.(next, event);
    }
  }, []);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const off = tree?.register(el, {
      key, value: valueNow, expand,
      hasGroup: () => el.querySelector(GROUP) !== null,
      expanded: () => latest.current.isOpen,
    });
    // The children change without a render of this item: an author's component, or a script.
    const observer = new MutationObserver(() => {
      const want = sync();
      if (want) flushSync(() => { setDomGroup(want.wantGroup); setDomText(want.wantText); });
    });
    observer.observe(el, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['data-part', 'id', 'aria-label', 'aria-labelledby'] });
    return () => { observer.disconnect(); off?.(); };
  }, [tree?.register, key, valueNow, expand, sync]);
  useLayoutEffect(() => {
    const want = sync();
    if (want) { setDomGroup(want.wantGroup); setDomText(want.wantText); }
  });

  // A mark: on the first render it may give the tree its first value; later it selects the item or clears it.
  const mounted = useRef(false);
  useLayoutEffect(() => {
    const mounting = !mounted.current;
    mounted.current = true;
    if (mounting && !selected) return;
    tree?.mark(key, valueNow(), selected, mounting);
  }, [selected]); // eslint-disable-line react-hooks/exhaustive-deps

  // A new value: the tree looks again for the item it selects.
  const before = useRef(/** @type {string | null} */ (null));
  useLayoutEffect(() => {
    if (before.current !== null && before.current !== own) tree?.renamed(key, before.current, own);
    if (before.current !== own) tree?.refresh();
    before.current = own;
  }, [own]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'tree-item',
    'aria-selected': String(isSelected),
    'aria-expanded': hasGroup ? String(isOpen) : undefined,
    'aria-disabled': disabled ? 'true' : undefined,
    'aria-level': tree && level ? String(level) : undefined,
  }), createElement(LevelContext.Provider, { value: level + 1 }, children));
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const TreeItem = /* @__PURE__ */ Object.assign(TreeItemRoot, { kitRole: role, displayName: 'TreeItem' });
