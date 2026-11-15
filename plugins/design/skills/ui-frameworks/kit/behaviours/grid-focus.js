// @ts-check
/** What can take focus inside a cell. A match counts only when `usable()` says so too. */
const CONTROL = 'a[href], area[href], button, input:not([type="hidden"]), select, textarea, iframe, summary, [contenteditable]:not([contenteditable="false"]), [tabindex]';
/** The inputs whose arrow keys move a caret or a value, not focus. */
const TEXT_INPUT = 'input:not([type="checkbox"], [type="radio"], [type="button"], [type="submit"], [type="reset"], [type="image"], [type="file"], [type="color"])';
/** The roles of a component that takes text or uses the arrow keys itself (J79). */
const KEEPS_KEYS = '[role="textbox"], [role="combobox"], [role="spinbutton"], [role="slider"], [role="listbox"]';

/**
 * The tabindex each element had before gridFocus first wrote one, or null when it had none: what the element is
 * given back when it stops being a stop of the grid. Shared by every grid, so a grid that is mounted again keeps
 * the author's value and not its own.
 * @type {WeakMap<Element, string | null>}
 */
const before = new WeakMap();

/** The tabindex an element has, as the author or its own component wrote it. @param {Element} el */
const authored = (el) => (before.has(el) ? before.get(el) ?? null : el.getAttribute('tabindex'));

/** A control that can take focus now: not disabled, not inside something hidden or inert, and not put out of reach by its author. @param {Element} el */
const usable = (el) => {
  if (el.matches(':disabled, [disabled]') || el.closest('[hidden], [inert]')) return false;
  const value = authored(el);
  return value === null || !(Number(value) < 0);
};

/** The controls in a cell that can take focus now, in document order. @param {HTMLElement} cell @returns {HTMLElement[]} */
const controlsOf = (cell) => /** @type {HTMLElement[]} */ ([...cell.querySelectorAll(CONTROL)].filter(usable));

/**
 * Whether an element keeps the arrow keys for itself: a text field, a text area, a select, editable text, or a
 * component with the textbox, combobox, spinbutton, slider or listbox role (J79).
 * @param {Element} el
 */
export const textEntry = (el) => el.matches(`${TEXT_INPUT}, textarea, select, [contenteditable]:not([contenteditable="false"]), ${KEEPS_KEYS}`);

/**
 * The element that stands for a cell in the grid: the one control in it that can take focus, when it holds exactly
 * one and that control does not keep the arrow keys for itself, or else the cell itself (B20, J69, J79).
 * @param {HTMLElement} cell @returns {HTMLElement}
 */
export function representative(cell) {
  const controls = controlsOf(cell);
  return controls.length === 1 ? (textEntry(controls[0]) ? cell : controls[0]) : cell;
}

/**
 * The controls of a cell that the user enters with Enter or F2 (J79): those of a cell that stands for itself and
 * holds a control. Empty for any other cell.
 * @param {HTMLElement} cell @param {HTMLElement} target the cell's representative
 */
const entered = (cell, target) => (target === cell ? controlsOf(cell) : []);

/**
 * gridFocus: makes a grid one stop in the Tab order, and moves focus from cell to cell with the arrow keys.
 * A behaviour: it imports nothing, takes a root and options, and returns its cleanup (D12).
 *
 * Rules: docs/specs/foundation.md, B19 and B20; docs/specs/patterns.md, J79 (D105).
 *
 * - A cell is represented by the one control in it that can take focus, when it holds exactly one and that control
 *   does not keep the arrow keys for itself, such as a link, a button or a checkbox; any other cell by itself
 *   (`representative()`).
 * - A cell that stands for itself and holds controls, several, or one that takes text or uses the arrow keys
 *   (`textEntry()`), is entered (J79). Its controls have `tabindex="-1"`, so the grid stays one stop. Enter or F2
 *   on the cell moves focus to its first control that takes it. While focus is inside the cell, Tab and Shift+Tab
 *   move among its controls and wrap, Escape or F2 moves focus back to the cell, and every other key is left to
 *   the control: the grid's keys do not act. The cell carries `data-editing` while focus is inside it, and loses
 *   it when focus leaves it by any means.
 * - One representative has `tabindex="0"`: the stop. Every other one has `tabindex="-1"`. With `rowFocus`, a row
 *   it names is a target as well and joins the same accounting; the keys on a row are the component's.
 *   `tabindex` and `data-editing` are the only attributes this behaviour writes, and only when they differ. An
 *   element that stops being a target or an entered control, because its row was hidden or its cell gained or
 *   lost a control, is given back the tabindex it had before this behaviour wrote one.
 * - While focus is inside the root, the stop is the target that has focus, or the cell focus is inside. While it is
 *   outside, the stop stays where focus last was, in the same cell when that cell is now represented differently;
 *   when that cell is gone or hidden, the stop is the first cell.
 * - On a representative, the arrow keys move focus one cell and stop at the edges; ArrowLeft and ArrowRight follow
 *   the writing direction. Home and End go to the first and the last cell of the row; with Control, to the first
 *   cell of the first row and the last cell of the last row. PageDown and PageUp move by `page()` rows. Up, down
 *   and by a page keep the column, or take the row's last cell when the row is shorter. The default action of each
 *   of these keys is prevented, also at an edge, so that the page does not scroll.
 * - A key pressed with Alt, Meta or Shift, Control with any key but Home and End, a key whose default a listener
 *   before this one has prevented, and every key in a text field, a text area, a select or editable text, are
 *   left alone.
 * - A click on a control of an entered cell focuses that control, also in an engine that gives a clicked button no
 *   focus. Any other click in a cell that leaves focus outside it, such as one on the padding of a cell whose
 *   control takes the focus, moves focus to the cell's representative.
 * - The DOM is the source. `rows()` and `cells(row)` are read again at every event, and an observer brings the
 *   stop up to date when rows or cells come or go, are hidden, or gain or lose a control.
 *
 * @param {HTMLElement} root
 * @param {{
 *   rows: () => HTMLElement[],
 *   cells: (row: HTMLElement) => HTMLElement[],
 *   page?: () => number,
 *   rowFocus?: (row: HTMLElement) => boolean,
 *   watch?: string[],
 * }} options  `rows` returns the rows the keys walk, in order, leaving out a hidden row; `cells` a row's cells in
 *   order. `page` is the number of rows PageDown and PageUp move; the default is 10. `rowFocus` names the rows
 *   that take focus themselves, as in a treegrid. `watch` lists attributes, beyond hidden, tabindex, disabled,
 *   href, contenteditable, inert and role, whose change can alter what `rows`, `cells` or `rowFocus` answer.
 * @returns {() => void}
 */
export function gridFocus(root, options) {
  const off = new AbortController();
  const listen = { signal: off.signal };
  /** @type {Set<HTMLElement>} The elements whose tabindex this behaviour now keeps. */
  const managed = new Set();
  /** @type {HTMLElement | null} The stop when sync() last ran. */
  let last = null;
  /** @type {HTMLElement | null} The cell that stop stands for, or null for a row. */
  let lastCell = null;
  /** @type {HTMLElement | null} The cell marked data-editing. */
  let editing = null;

  /** The grid as the component gives it now: each row with its representatives. */
  const layout = () => options.rows().map((row) => {
    const cells = options.cells(row);
    return { row, cells, targets: cells.map(representative) };
  });

  /** @param {HTMLElement} el @param {string | null} value */
  const put = (el, value) => {
    if (el.getAttribute('tabindex') === value) return;
    if (value === null) el.removeAttribute('tabindex');
    else el.setAttribute('tabindex', value);
  };
  /** Makes an element a target: remembers what it had, the first time. @param {HTMLElement} el @param {string} value */
  const keep = (el, value) => {
    if (!before.has(el)) before.set(el, el.getAttribute('tabindex'));
    managed.add(el);
    put(el, value);
  };
  /** Gives an element back the tabindex it had. @param {HTMLElement} el */
  const release = (el) => {
    managed.delete(el);
    const value = before.get(el) ?? null;
    before.delete(el);
    put(el, value);
  };

  /**
   * Marks with data-editing the entered cell that holds focus, inside it and not on it, and unmarks any other.
   * @param {Element | null} focused the element that has focus, or is about to @param {ReturnType<typeof layout>} grid
   */
  const mark = (focused, grid) => {
    let cell = null;
    if (focused && root.contains(focused)) {
      for (const { cells, targets } of grid) {
        const n = cells.findIndex((c) => c !== focused && c.contains(focused));
        if (n >= 0) { if (entered(cells[n], targets[n]).length) cell = cells[n]; break; }
      }
    }
    if (cell === editing) return;
    editing?.removeAttribute('data-editing');
    editing = cell;
    editing?.setAttribute('data-editing', '');
  };

  const sync = () => {
    /** @type {{ el: HTMLElement, cell: HTMLElement | null }[]} */
    const entries = [];
    /** @type {HTMLElement[]} The controls of entered cells. */
    const inner = [];
    const grid = layout();
    for (const { row, cells, targets } of grid) {
      if (options.rowFocus?.(row)) entries.push({ el: row, cell: null });
      targets.forEach((el, n) => entries.push({ el, cell: cells[n] }));
      cells.forEach((cell, n) => inner.push(...entered(cell, targets[n])));
    }
    const active = root.ownerDocument.activeElement;
    const stop = (active && root.contains(active) ? entries.find((e) => e.el === active) ?? entries.find((e) => e.cell?.contains(active)) : undefined)
      ?? entries.find((e) => e.el === last || (lastCell !== null && e.cell === lastCell))
      ?? entries[0];
    last = stop?.el ?? null;
    lastCell = stop?.cell ?? null;
    const now = new Set([...entries.map((e) => e.el), ...inner]);
    for (const el of [...managed]) if (!now.has(el)) release(el);
    for (const { el } of entries) keep(el, el === last ? '0' : '-1');
    for (const el of inner) keep(el, '-1');
    mark(active, grid);
  };

  /**
   * The keys of an entered cell (J79): Enter or F2 on it, and Escape, F2, Tab and Shift+Tab inside it. Returns
   * true when it handled the key. Every other key inside the cell is the control's: the grid's keys act only on a
   * target, and a control of an entered cell is none.
   * @param {KeyboardEvent} event
   */
  const cellKeys = (event) => {
    if (event.altKey || event.metaKey || event.ctrlKey || event.defaultPrevented) return false;
    const target = /** @type {HTMLElement} */ (event.target);
    for (const { cells, targets } of layout()) {
      const n = cells.findIndex((c) => c.contains(target));
      if (n < 0) continue;
      const cell = cells[n];
      const controls = entered(cell, targets[n]);
      if (!controls.length) return false;
      if (target === cell) {
        if (event.shiftKey || (event.key !== 'Enter' && event.key !== 'F2')) return false;
        event.preventDefault();
        controls.some((c) => { c.focus(); return c.contains(root.ownerDocument.activeElement); });
        return true;
      }
      if (event.key === 'Escape' || (event.key === 'F2' && !event.shiftKey)) {
        event.preventDefault();
        cell.focus();
      } else if (event.key === 'Tab') {
        event.preventDefault();
        const at = controls.reduce((found, c, i) => (c.contains(target) ? i : found), -1);
        const by = event.shiftKey ? -1 : 1;
        controls[at < 0 ? (by > 0 ? 0 : controls.length - 1) : (at + by + controls.length) % controls.length].focus();
      } else return false;
      return true;
    }
    return false;
  };

  root.addEventListener('keydown', (event) => {
    if (cellKeys(event)) return;
    if (event.defaultPrevented || event.altKey || event.metaKey || event.shiftKey) return;
    if (event.ctrlKey && event.key !== 'Home' && event.key !== 'End') return;
    const target = /** @type {HTMLElement} */ (event.target);
    const grid = layout().map((r) => r.targets).filter((targets) => targets.length);
    const r = grid.findIndex((targets) => targets.includes(target));
    if (r < 0 || textEntry(target)) return;
    const c = grid[r].indexOf(target);
    const forward = getComputedStyle(root).direction === 'rtl' ? -1 : 1;
    const page = Math.max(1, options.page?.() ?? 10);
    const lastRow = grid.length - 1;
    /** @type {[number, number] | null} */
    let to = null;
    if (event.key === 'ArrowRight') to = [r, c + forward];
    else if (event.key === 'ArrowLeft') to = [r, c - forward];
    else if (event.key === 'ArrowDown') to = [r + 1, c];
    else if (event.key === 'ArrowUp') to = [r - 1, c];
    else if (event.key === 'PageDown') to = [r + page, c];
    else if (event.key === 'PageUp') to = [r - page, c];
    else if (event.key === 'Home') to = event.ctrlKey ? [0, 0] : [r, 0];
    else if (event.key === 'End') to = event.ctrlKey ? [lastRow, Infinity] : [r, Infinity];
    if (!to) return;
    event.preventDefault();
    const row = Math.min(lastRow, Math.max(0, to[0]));
    // A step past an edge stays at the edge, and a shorter row gives its last cell.
    const col = Math.min(grid[row].length - 1, Math.max(0, to[1]));
    grid[row][col].focus();
  }, listen);

  root.addEventListener('click', (event) => {
    if (!(event.target instanceof Element)) return;
    const active = root.ownerDocument.activeElement;
    for (const { cells, targets } of layout()) {
      const n = cells.findIndex((cell) => cell.contains(/** @type {Node} */ (event.target)));
      if (n < 0) continue;
      const control = entered(cells[n], targets[n]).filter((c) => c.contains(/** @type {Node} */ (event.target))).pop();
      if (control) {
        if (!control.contains(active)) control.focus();
        return;
      }
      if (!(active && cells[n].contains(active))) targets[n].focus();
      return;
    }
  }, listen);

  root.addEventListener('focusin', () => sync(), listen);
  // Focus that leaves an entered cell, to anywhere or to nothing, unmarks it; focusin marks the next one.
  root.addEventListener('focusout', (event) => mark(/** @type {Element | null} */ (event.relatedTarget), layout()), listen);

  const observer = new MutationObserver(() => sync());
  observer.observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['hidden', 'tabindex', 'disabled', 'href', 'contenteditable', 'inert', 'role', ...(options.watch ?? [])] });
  sync();

  return () => { off.abort(); observer.disconnect(); mark(null, []); };
}
