// @ts-check
/**
 * grid.js: a grid, and with `tree` a treegrid, for React (docs/specs/targets.md; rules J68 to J71 and J79 of
 * docs/specs/patterns.md, B19 and B20 of docs/specs/foundation.md).
 *
 * The root is a <div>, a block around the author's own native table, the child marked `data-part="table"`. The
 * table is the author's: this component never clones, wraps or renders it. It finds it in the DOM, as the Web
 * Component does, and writes on it and its rows, only where they differ, after each render and on each change
 * in its subtree, what the class writes: the grid role, or treegrid, `aria-rowcount`, `aria-colcount`, each
 * row's `aria-rowindex`, and with `tree` each row's `aria-level` from its `data-level` and `hidden` on every row
 * below a closed row. It never shows a row the author hid. It mounts gridFocus with the class's options, which
 * writes the cells' `tabindex` and `data-editing` (J79).
 *
 * The treegrid's own keys (J70) go through React's onKeyDownCapture on the root. gridFocus listens natively on
 * the root, in the bubble phase; React's bubble-phase onKeyDown is dispatched from the React root's container,
 * after the event has left this root, so gridFocus would see every key first and take the back key on a first
 * cell for itself. React's capture phase is dispatched from the container on the way down, before the event
 * reaches the root: these keys are handled first and their default prevented, and gridFocus, like rovingFocus,
 * passes over a key whose default is already prevented. That is the order the class has, where this listener is
 * added before the behaviour's.
 *
 * Which rows are open is the author's `aria-expanded` on a row that has child rows, as on the Web Component.
 * Uncontrolled, the author's value is where the row starts (or `defaultExpanded`, the ids of the rows that start
 * open), and the grid writes `aria-expanded` when the user opens or closes a row. Controlled, `expanded` holds the
 * ids of the open rows: the grid writes `aria-expanded` on every row that carries it from that list, and a key
 * only asks the owner. onExpandedChange(expanded, event) is called once each time the user opens or closes a row,
 * with the ids of the rows that would then be open, after the rows are written when uncontrolled. A row is named
 * by its `id`; a row with no id cannot be opened by a controlled grid.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import { gridFocus, representative, textEntry } from '../../behaviours/grid-focus.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'defaultValue'> & {
 *   tree?: boolean,
 *   expanded?: string[], defaultExpanded?: string[],
 *   onExpandedChange?: (expanded: string[], event: import('react').KeyboardEvent<HTMLDivElement>) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} GridProps
 * @typedef {{ tree: boolean, expanded: string[] | undefined }} GridState
 */

/** The rows PageDown and PageUp move, as on the Web Component. */
const PAGE = 5;
const TABLE = ':scope > [data-part="table"]';

/**
 * Sets or removes an attribute, only when it differs. The observers then see nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/** A row's level: its data-level when that is a whole number of 1 or more, or else 1. @param {Element} row */
const levelOf = (row) => {
  const level = Number(row.getAttribute('data-level'));
  return Number.isInteger(level) && level >= 1 ? level : 1;
};

/** The author's table: the child marked data-part="table", when it is a table. @param {HTMLElement} root */
const tableOf = (root) => {
  const table = root.querySelector(TABLE);
  return table instanceof HTMLTableElement ? table : null;
};
/** Every row of the table, its header and footer rows included, in order. @param {HTMLElement} root */
const allRows = (root) => [...(tableOf(root)?.rows ?? [])];
/** The rows that show. @param {HTMLElement} root */
const shownRows = (root) => allRows(root).filter((row) => !row.hidden);
/** Whether a row takes focus itself: a body row of a treegrid. @param {boolean} tree @param {HTMLElement} row */
const rowFocusOf = (tree, row) => tree && row.parentElement?.localName !== 'thead';

/** The row a row belongs to: the nearest row before it of a lower level. @param {HTMLElement} root @param {HTMLTableRowElement} row */
const parentOf = (root, row) => {
  const all = allRows(root);
  const level = levelOf(row);
  for (let n = all.indexOf(row) - 1; n >= 0; n--) if (levelOf(all[n]) < level) return all[n];
  return null;
};

/**
 * Writes the roles, the counts, the levels, which rows are open when controlled, and which rows show. Writes
 * nothing when they are already right.
 * @param {HTMLElement} root @param {GridState} state @param {WeakSet<HTMLTableRowElement>} hid the rows this grid hid
 */
const sync = (root, { tree, expanded }, hid) => {
  const table = tableOf(root);
  if (!table) return;
  const rows = [...table.rows];
  put(table, 'role', tree ? 'treegrid' : 'grid');
  put(table, 'aria-rowcount', String(rows.length));
  put(table, 'aria-colcount', String(Math.max(0, ...rows.map((row) => [...row.cells].reduce((sum, cell) => sum + cell.colSpan, 0)))));
  /** @type {{ level: number, open: boolean }[]} The rows above this one that have child rows. */
  const above = [];
  rows.forEach((row, n) => {
    put(row, 'aria-rowindex', String(n + 1));
    const level = levelOf(row);
    put(row, 'aria-level', tree && row.hasAttribute('data-level') ? String(level) : null);
    if (expanded && row.hasAttribute('aria-expanded')) put(row, 'aria-expanded', String(row.id !== '' && expanded.includes(row.id)));
    while (above.length && above[above.length - 1].level >= level) above.pop();
    const shut = tree && above.some((a) => !a.open);
    if (shut && !row.hidden) { row.hidden = true; hid.add(row); }
    else if (!shut && hid.has(row)) { hid.delete(row); row.hidden = false; }
    const open = row.getAttribute('aria-expanded');
    if (open === 'true' || open === 'false') above.push({ level, open: open === 'true' });
  });
};

/** @param {GridProps} props */
export function Grid({ tree = false, expanded, defaultExpanded, onExpandedChange, onKeyDownCapture, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  /** @type {import('react').RefObject<GridState & { onExpandedChange: GridProps['onExpandedChange'] }>} */
  const latest = useRef({ tree: !!tree, expanded, onExpandedChange });
  latest.current = { tree: !!tree, expanded, onExpandedChange };
  /** @type {import('react').RefObject<WeakSet<HTMLTableRowElement>>} */
  const hid = useRef(new WeakSet());
  const startOpen = useRef(defaultExpanded);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    // The rows that start open, when the author lists them: once, as an uncontrolled input takes its default.
    if (startOpen.current && !latest.current.expanded) {
      const ids = startOpen.current;
      for (const row of allRows(el)) if (row.hasAttribute('aria-expanded')) put(row, 'aria-expanded', String(row.id !== '' && ids.includes(row.id)));
    }
    const stop = gridFocus(el, {
      rows: () => shownRows(el),
      cells: (/** @type {HTMLElement} */ row) => [.../** @type {HTMLTableRowElement} */ (row).cells],
      page: () => PAGE,
      rowFocus: (/** @type {HTMLElement} */ row) => rowFocusOf(latest.current.tree, row),
      // When tree changes the table's role changes, which the behaviour watches (J79), so nothing is listed here.
    });
    const observer = new MutationObserver(() => sync(el, latest.current, hid.current));
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'data-level', 'aria-expanded', 'colspan', 'hidden'] });
    sync(el, latest.current, hid.current);
    return () => { observer.disconnect(); stop(); };
  }, []);
  // After each render: tree or expanded may have changed, and the author's rows with them. In the same commit, so
  // a script reads the roles and the rows that show as soon as the render returns.
  useLayoutEffect(() => { if (root.current) sync(root.current, latest.current, hid.current); });
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /**
   * Opens or closes a row because the user asked for it.
   * @param {HTMLTableRowElement} row @param {boolean} open @param {import('react').KeyboardEvent<HTMLDivElement>} event
   */
  const expand = (row, open, event) => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const now = latest.current;
    const ids = now.expanded ?? allRows(el).filter((r) => r.id !== '' && r.getAttribute('aria-expanded') === 'true').map((r) => r.id);
    const next = row.id === '' ? ids : open ? [...ids.filter((id) => id !== row.id), row.id] : ids.filter((id) => id !== row.id);
    if (!now.expanded) {
      put(row, 'aria-expanded', String(open));
      // The rows below it show or hide before onExpandedChange is called.
      sync(el, now, hid.current);
    }
    now.onExpandedChange?.(next, event);
  };

  /** The treegrid's keys (J70), before gridFocus's. @param {import('react').KeyboardEvent<HTMLDivElement>} event */
  const keys = (event) => {
    onKeyDownCapture?.(event);
    const el = /** @type {HTMLDivElement} */ (root.current);
    const { tree: isTree } = latest.current;
    if (!isTree || event.nativeEvent.defaultPrevented || event.altKey || event.metaKey || event.shiftKey) return;
    const target = /** @type {HTMLElement} */ (event.target);
    const rows = shownRows(el);
    const rtl = getComputedStyle(el).direction === 'rtl';
    const forward = rtl ? 'ArrowLeft' : 'ArrowRight';
    const back = rtl ? 'ArrowRight' : 'ArrowLeft';
    const row = /** @type {HTMLTableRowElement | undefined} */ (rows.find((r) => r === target));
    if (row && rowFocusOf(isTree, row)) {
      if (event.ctrlKey && event.key !== 'Home' && event.key !== 'End') return;
      const walk = rows.filter((r) => rowFocusOf(isTree, r));
      const at = walk.indexOf(row);
      const step = (/** @type {number} */ by) => walk[Math.min(walk.length - 1, Math.max(0, at + by))];
      const open = row.getAttribute('aria-expanded');
      /** @type {HTMLElement | null | undefined} */
      let next = null;
      if (event.key === forward) {
        if (open === 'false') expand(row, true, event);
        else next = row.cells.length ? representative(row.cells[0]) : null;
      } else if (event.key === back) {
        if (open === 'true') expand(row, false, event);
        else next = parentOf(el, row);
      } else if (event.key === 'ArrowDown') next = step(1);
      else if (event.key === 'ArrowUp') next = step(-1);
      else if (event.key === 'PageDown') next = step(PAGE);
      else if (event.key === 'PageUp') next = step(-PAGE);
      else if (event.key === 'Home') next = walk[0];
      else if (event.key === 'End') next = walk[walk.length - 1];
      else return;
      event.preventDefault();
      next?.focus();
      return;
    }
    // The back key on a first cell moves to its row.
    if (event.key !== back || event.ctrlKey || textEntry(target)) return;
    const owner = rows.find((r) => r.cells.length && representative(r.cells[0]) === target);
    if (!owner || !rowFocusOf(isTree, owner)) return;
    event.preventDefault();
    owner.focus();
  };

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'grid', onKeyDownCapture: keys }), children);
}
