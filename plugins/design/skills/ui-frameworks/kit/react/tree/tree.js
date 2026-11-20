// @ts-check
/**
 * tree.js: a tree, for React (docs/specs/targets.md; rules J32 to J35 of docs/specs/patterns.md).
 *
 * The root is a <div role="tree">. It never takes focus itself: its items do. It mounts roving focus, which keeps
 * one item that shows (every item around it is expanded) in the Tab order and moves focus with ArrowDown, ArrowUp,
 * Home and End without wrapping, and typeahead, which moves focus to the item whose label starts with what is
 * typed. Its own keys go through React's onKeyDown on the root: ArrowRight and ArrowLeft open and close an item
 * or move to its first child or its parent (swapped in a right-to-left scope), and Enter and Space select. None of
 * them is a key the behaviours act on: roving focus is vertical, so it leaves the inline arrows alone, and
 * typeahead leaves Space and every key whose name is longer than one letter. A click on an item's label selects
 * the item, and opens or closes it when it has a group; a press on a disabled item gives focus to nothing.
 *
 * It coordinates its items through React context, which this module exports for them. The selected value is
 * controlled (value with onChange) or uncontrolled (defaultValue). With neither, it is the value of the first item
 * marked `selected`, read from the elements it is given when it first renders, or else from the items as they
 * mount. Of two items with the same value, the one the user or a mark picked is selected, or else the first in
 * the document. onChange(value, event) is called once the user selects another item, after the items are written
 * when the value is uncontrolled (J34). It is not called when the value prop changes, nor for a mark.
 *
 * Into the DOM, only where they differ, after each render and on each change of its subtree, it writes
 * `aria-setsize` and `aria-posinset` on its items: their siblings are in groups the author writes, which React
 * cannot count before they are in the page. Each item renders its own `aria-level`, `aria-selected`,
 * `aria-expanded` and `aria-disabled`.
 */
import { Children, Fragment, createContext, createElement, isValidElement, useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { typeahead } from '../../behaviours/typeahead.js';
import { role } from '../../components/tree/tree.props.js';

/**
 * What an item gives its tree, read at the moment the tree needs it.
 * @typedef {{
 *   key: string, value: () => string, hasGroup: () => boolean, expanded: () => boolean,
 *   expand: (open: boolean, event: import('react').SyntheticEvent) => void,
 * }} ItemEntry
 * @typedef {{
 *   selects: (key: string, value: string) => boolean,
 *   register: (el: HTMLElement, entry: ItemEntry) => () => void,
 *   mark: (key: string, value: string, on: boolean, mounting: boolean) => void,
 *   renamed: (key: string, from: string, to: string) => void,
 *   refresh: () => void,
 * }} TreeState
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'defaultValue'> & {
 *   value?: string, defaultValue?: string,
 *   onChange?: (value: string, event: import('react').SyntheticEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} TreeProps
 */

/** What the items of the nearest tree read. @type {import('react').Context<TreeState | null>} */
export const TreeContext = /* @__PURE__ */ createContext(/** @type {TreeState | null} */ (null));
/** The level an item renders: 1 at the top of a tree, one more inside each item. @type {import('react').Context<number>} */
export const LevelContext = /* @__PURE__ */ createContext(0);

export const ITEM = '[role="treeitem"]';
export const GROUP = ':scope > [data-part="group"]';
export const LABEL = ':scope > [data-part="label"]';
const TREE = '[role="tree"]';

/** @param {Element} el */
export const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
export const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/** The items of a tree, and not of another tree nested in one, in document order. @param {Element} tree */
const ownOf = (tree) => /** @type {HTMLElement[]} */ ([...tree.querySelectorAll(ITEM)].filter((item) => item.closest(TREE) === tree));
/** The item whose group holds this one, or null at the top of the tree. @param {Element} tree @param {Element} item @returns {HTMLElement | null} */
const parentIn = (tree, item) => {
  const parent = /** @type {HTMLElement | null} */ (item.parentElement?.closest(ITEM) ?? null);
  return parent && parent.closest(TREE) === tree ? parent : null;
};
/** Whether an item shows: every item around it is expanded. @param {Element} tree @param {Element} item */
const showsIn = (tree, item) => {
  for (let parent = parentIn(tree, item); parent; parent = parentIn(tree, parent)) if (parent.getAttribute('aria-expanded') !== 'true') return false;
  return true;
};

/** The role a component of this family renders, so that the walk below knows it without importing it. @param {unknown} node */
const roleOf = (node) => (isValidElement(node) && typeof node.type === 'function' ? /** @type {any} */ (node.type).kitRole : undefined);

/** The text of React children, as far as they are strings. @param {import('react').ReactNode} children @returns {string} */
const textOf = (children) => {
  let text = '';
  Children.forEach(children, (child) => {
    if (typeof child === 'string' || typeof child === 'number') text += String(child);
    else if (isValidElement(child)) text += textOf(/** @type {any} */ (child.props).children);
  });
  return text;
};

/**
 * An item's direct child marked as a part, through fragments, among React children.
 * @param {import('react').ReactNode} children @param {string} part @returns {any}
 */
export function partOf(children, part) {
  /** @type {any} */
  let found = null;
  Children.forEach(children, (child) => {
    if (found || !isValidElement(child)) return;
    const props = /** @type {any} */ (child.props);
    if (child.type === Fragment) found = partOf(props.children, part);
    else if (props['data-part'] === part) found = child;
  });
  return found;
}

/** An item's value as its props give it: `value`, or else the trimmed text of its label. @param {any} props */
export const valueOfProps = (props) => props.value ?? textOf(partOf(props.children, 'label')?.props.children).trim();

/** The value of the first item marked selected among React children, in document order, not inside a nested tree. @param {import('react').ReactNode} children @returns {string | undefined} */
function marked(children) {
  /** @type {string | undefined} */
  let found;
  Children.forEach(children, (child) => {
    if (found !== undefined || !isValidElement(child)) return;
    const props = /** @type {any} */ (child.props);
    const kind = roleOf(child);
    if (kind === 'tree') return;
    if (kind === 'treeitem' && props.selected) {
      const value = valueOfProps(props);
      if (value !== '') { found = value; return; }
    }
    found = marked(props.children);
  });
  return found;
}

/** @param {TreeProps} props */
function TreeRoot({ value, defaultValue, onChange, onKeyDown, onClick, onMouseDown, children, ref, ...rest }) {
  const [own, setOwn] = useState(() => defaultValue ?? marked(children) ?? '');
  const controlled = value !== undefined;
  const current = controlled ? value : own;
  /** @type {[{ key: string, value: string } | null, (next: { key: string, value: string } | null) => void]} The item last picked by the user or a mark, which wins over another item of the same value. */
  const [picked, setPicked] = useState(/** @type {{ key: string, value: string } | null} */ (null));
  /** @type {[{ key: string | null, value: string } | null, (next: { key: string | null, value: string } | null) => void]} The first item in the document with the value, once the items are in the page. */
  const [first, setFirst] = useState(/** @type {{ key: string | null, value: string } | null} */ (null));
  const target = picked && picked.value === current ? picked.key : first && first.value === current ? first.key : null;

  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ current, controlled, onChange, picked, first, target, hasDefault: defaultValue !== undefined || controlled });
  latest.current = { current, controlled, onChange, picked, first, target, hasDefault: defaultValue !== undefined || controlled };
  /** @type {import('react').RefObject<Map<HTMLElement, ItemEntry>>} */
  const items = useRef(new Map());
  /** Whether the tree has once settled, after which a mark is taken only when it is made. */
  const settled = useRef(false);
  /** Whether a mark among the first items has already given the value. */
  const adopted = useRef(false);

  const ownItems = useCallback(() => (root.current ? ownOf(root.current) : []), []);
  const parentOf = useCallback((/** @type {Element} */ item) => (root.current ? parentIn(root.current, item) : null), []);

  /** Writes the items' position among their siblings, and finds the first item of the value. Writes nothing when they are up to date. */
  const sync = useCallback(() => {
    const all = ownItems();
    /** @type {Map<HTMLElement | null, HTMLElement[]>} */
    const siblings = new Map();
    for (const item of all) {
      const parent = parentOf(item);
      siblings.set(parent, [...(siblings.get(parent) ?? []), item]);
    }
    for (const item of all) {
      const set = /** @type {HTMLElement[]} */ (siblings.get(parentOf(item)));
      put(item, 'aria-setsize', String(set.length));
      put(item, 'aria-posinset', String(set.indexOf(item) + 1));
    }
    const now = latest.current;
    if (now.current === '' || (now.picked && now.picked.value === now.current)) return null;
    const found = all.find((item) => items.current.get(item)?.value() === now.current);
    const key = found ? /** @type {ItemEntry} */ (items.current.get(found)).key : null;
    return now.first && now.first.value === now.current && now.first.key === key ? null : { key, value: now.current };
  }, [ownItems, parentOf]);

  /** @type {TreeState['selects']} */
  const selects = (key, v) => current !== '' && v === current && (target === null || target === key);

  const register = useCallback((/** @type {HTMLElement} */ el, /** @type {ItemEntry} */ entry) => {
    items.current.set(el, entry);
    return () => { if (items.current.get(el) === entry) items.current.delete(el); };
  }, []);

  /** Holds a value and the item that has it, and keeps `latest` in step, so that marks made in one commit read each other. */
  const hold = useCallback((/** @type {string} */ v, /** @type {{ key: string, value: string } | null} */ p) => {
    setOwn(v);
    setPicked(p);
    latest.current = { ...latest.current, current: v, picked: p, target: p ? p.key : null };
  }, []);

  const mark = useCallback((/** @type {string} */ key, /** @type {string} */ v, /** @type {boolean} */ on, /** @type {boolean} */ mounting) => {
    const now = latest.current;
    if (now.controlled) return;
    if (on) {
      if (v === '') return;
      if (mounting && !settled.current) {
        // The first items: a value the tree was given wins, and the first marked item holds the value.
        if (adopted.current || (now.hasDefault && now.current !== v)) return;
        adopted.current = true;
        hold(v, { key, value: v });
        return;
      }
      if (now.target === key && now.current === v) return;
      // A mark made later, or an item that arrives carrying one: that item is now the value.
      hold(v, { key, value: v });
    } else if (now.target === key && now.current === v) {
      // The selected item's mark was cleared: nothing is selected.
      hold('', null);
    }
  }, [hold]);

  const renamed = useCallback((/** @type {string} */ key, /** @type {string} */ from, /** @type {string} */ to) => {
    const now = latest.current;
    // A new value on the selected item becomes the tree's.
    if (now.controlled || now.current !== from || (now.target !== null && now.target !== key) || to === '') return;
    hold(to, { key, value: to });
  }, [hold]);

  const refresh = useCallback(() => {
    const next = sync();
    if (next) setFirst(next);
  }, [sync]);

  /** Selects an item because the user asked, then tells onChange, which finds the items already written. @param {HTMLElement} item @param {import('react').SyntheticEvent} event */
  const choose = (item, event) => {
    const entry = items.current.get(item);
    if (!entry) return;
    const now = latest.current;
    const v = entry.value();
    if (now.target === entry.key || (now.target === null && now.current === v && ownItems().find((el) => items.current.get(el)?.value() === v) === item)) return;
    // A controlled value waits for its owner: the value held here is then never read.
    flushSync(() => {
      setPicked({ key: entry.key, value: v });
      setOwn(v);
    });
    now.onChange?.(v, event);
  };

  /** @param {import('react').KeyboardEvent<HTMLDivElement>} event */
  const keyDown = (event) => {
    onKeyDown?.(event);
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    // Focus is on an item itself. A key from inside an item's label, or from an item of another tree, is not
    // this tree's: and the item is the target, so a key is handled once, for it.
    const item = /** @type {HTMLElement} */ (event.target);
    if (!ownItems().includes(item)) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      choose(item, event);
      return;
    }
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    const entry = items.current.get(item);
    const rtl = getComputedStyle(/** @type {HTMLDivElement} */ (root.current)).direction === 'rtl';
    const opening = (event.key === 'ArrowRight') !== rtl;
    const group = entry?.hasGroup() ?? false;
    event.preventDefault();
    if (opening) {
      if (!group || !entry) return;
      if (!entry.expanded()) { entry.expand(true, event); return; }
      ownItems().find((child) => parentOf(child) === item && !disabled(child))?.focus();
    } else {
      if (group && entry?.expanded()) { entry.expand(false, event); return; }
      parentOf(item)?.focus(); // a disabled parent has no tabindex, so it takes no focus
    }
  };

  /** A press on a disabled item gives focus to nothing, not to the item around it. @param {import('react').MouseEvent<HTMLDivElement>} event */
  const mouseDown = (event) => {
    onMouseDown?.(event);
    const item = event.target instanceof Element ? event.target.closest(ITEM) : null;
    if (item && item.closest(TREE) === root.current && disabled(item)) event.preventDefault();
  };

  /** A click on an item's label selects the item, and opens or closes it. @param {import('react').MouseEvent<HTMLDivElement>} event */
  const click = (event) => {
    onClick?.(event);
    if (event.defaultPrevented) return;
    const label = event.target instanceof Element ? event.target.closest('[data-part="label"]') : null;
    const item = /** @type {HTMLElement | null} */ (label?.parentElement ?? null);
    if (!label || !item || !ownItems().includes(item) || disabled(item)) return;
    // The press already gave the item focus: it is the focusable element around its label.
    choose(item, event);
    const entry = items.current.get(item);
    if (entry?.hasGroup()) entry.expand(!entry.expanded(), event);
  };

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    // The behaviours read the element they were given, so that only their cleanup ends them.
    const showing = () => ownOf(el).filter((item) => showsIn(el, item));
    const stops = [
      rovingFocus(el, {
        items: showing,
        orientation: () => 'vertical',
        wrap: false,
        current: () => ownOf(el).find((item) => item.getAttribute('aria-selected') === 'true' && showsIn(el, item)),
        skip: disabled,
        watch: ['aria-expanded', 'aria-selected'],
      }),
      typeahead(el, {
        items: showing,
        skip: disabled,
        text: (/** @type {HTMLElement} */ item) => item.querySelector(LABEL)?.textContent ?? '',
        onMatch: (/** @type {HTMLElement} */ item) => item.focus(),
      }),
    ];
    // Items that come, go or move in the page: their positions, and the first item of the value.
    const observer = new MutationObserver(() => {
      const next = sync();
      if (next) flushSync(() => setFirst(next));
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role'] });
    settled.current = true;
    return () => { observer.disconnect(); for (const stop of stops) stop(); };
  }, [sync]);
  // After each render: an item's value or the tree's may have changed.
  useLayoutEffect(refresh);
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** @type {TreeState} */
  const state = { selects, register, mark, renamed, refresh };
  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, role, 'data-ui': 'tree', onKeyDown: keyDown, onClick: click, onMouseDown: mouseDown }),
    createElement(TreeContext.Provider, { value: state }, createElement(LevelContext.Provider, { value: 1 }, children)));
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Tree = /* @__PURE__ */ Object.assign(TreeRoot, { kitRole: role, displayName: 'Tree' });
