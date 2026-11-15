// @ts-check
/**
 * grid.class.js: the class of a grid, and with `tree` of a treegrid. Importing it defines no element; grid.js does that.
 *
 * The grid wraps a native table the author writes, its child marked `data-part="table"`. It never moves a row or
 * a cell. On the table it writes the grid role, or treegrid, and `aria-rowcount` and `aria-colcount`; on each row
 * `aria-rowindex`. gridFocus makes the cells one stop in the Tab order and moves focus among them; a cell that
 * holds exactly one plain control is represented by that control. A cell with several controls, or with one that
 * takes text or uses the arrow keys, is entered with Enter or F2 and left with Escape or F2, and carries
 * `data-editing` while focus is inside it (J79): gridFocus does that, for a treegrid's cells as well, because it
 * is the one that decides what stands for a cell.
 *
 * With `tree`, a row's level is its `data-level`, which the grid copies to `aria-level`, and a row with child rows
 * carries `aria-expanded` as the author wrote it. The grid hides, with `hidden`, every row below a closed row whose
 * level is higher, down to the next row of that row's level or lower; it shows them again when the row opens, and
 * never shows a row the author hid. The body rows then take focus too, and their keys are this component's own
 * (J70): ArrowRight opens a closed row and moves from an open row or a leaf row to its first cell; ArrowLeft
 * closes an open row and moves from any other row to its parent row, and from a first cell to its row. Both
 * follow the writing direction. ArrowDown, ArrowUp, Home, End, PageDown and PageUp move from row to row.
 *
 * Rules: docs/specs/patterns.md, J68 to J71 and J79; docs/specs/foundation.md, B19 and B20.
 */
import { UIElement } from '../../foundation/element.js';
import { gridFocus, representative, textEntry } from '../../behaviours/grid-focus.js';
import { props, role, tabindex } from './grid.props.js';

/** The rows PageDown and PageUp move. */
const PAGE = 5;

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

export class UIGrid extends UIElement {
  static props = props;
  static role = role;
  static tabindex = tabindex;

  /** @type {WeakSet<HTMLTableRowElement>} The rows this grid hid, so that it never shows one the author hid. */
  #hid = new WeakSet();

  /** The author's table: the child marked data-part="table", when it is a table. @returns {HTMLTableElement | null} */
  #table() {
    const table = this.ensurePart('table');
    return table instanceof HTMLTableElement ? table : null;
  }

  /** Every row of the table, its header and footer rows included, in order. */
  #all() { return [...(this.#table()?.rows ?? [])]; }

  /** The rows that show. */
  #rows() { return this.#all().filter((row) => !row.hidden); }

  /** Whether a row takes focus itself: a body row of a treegrid. @param {HTMLElement} row */
  #rowFocus(row) { return /** @type {any} */ (this).tree && row.parentElement?.localName !== 'thead'; }

  /** The row a row belongs to: the nearest row before it of a lower level. @param {HTMLTableRowElement} row */
  #parent(row) {
    const all = this.#all();
    const level = levelOf(row);
    for (let n = all.indexOf(row) - 1; n >= 0; n--) if (levelOf(all[n]) < level) return all[n];
    return null;
  }

  /** Writes the roles, the counts, the levels and which rows show. Writes nothing when they are already right. */
  #sync() {
    const table = this.#table();
    if (!table) return;
    const tree = /** @type {any} */ (this).tree;
    const rows = this.#all();
    put(table, 'role', tree ? 'treegrid' : 'grid');
    put(table, 'aria-rowcount', String(rows.length));
    put(table, 'aria-colcount', String(Math.max(0, ...rows.map((row) => [...row.cells].reduce((sum, cell) => sum + cell.colSpan, 0)))));
    /** @type {{ level: number, open: boolean }[]} The rows above this one that have child rows. */
    const above = [];
    rows.forEach((row, n) => {
      put(row, 'aria-rowindex', String(n + 1));
      const level = levelOf(row);
      put(row, 'aria-level', tree && row.hasAttribute('data-level') ? String(level) : null);
      while (above.length && above[above.length - 1].level >= level) above.pop();
      const shut = tree && above.some((a) => !a.open);
      if (shut && !row.hidden) { row.hidden = true; this.#hid.add(row); }
      else if (!shut && this.#hid.has(row)) { this.#hid.delete(row); row.hidden = false; }
      const expanded = row.getAttribute('aria-expanded');
      if (expanded === 'true' || expanded === 'false') above.push({ level, open: expanded === 'true' });
    });
  }

  /**
   * Opens or closes a row because the user asked for it. The observer then shows or hides the rows below it, before
   * the key's event has finished.
   * @param {HTMLTableRowElement} row @param {boolean} open
   */
  #expand(row, open) { put(row, 'aria-expanded', String(open)); }

  /** @param {string} [name] */
  changed(name) {
    if (name === 'tree' && this.isConnected) this.#sync();
  }

  connected() {
    // Before gridFocus, so that a key this handles is not handled again: the behaviour leaves alone a key whose
    // default is already prevented.
    this.listen(this, 'keydown', (/** @type {KeyboardEvent} */ event) => {
      if (!(/** @type {any} */ (this).tree) || event.defaultPrevented || event.altKey || event.metaKey || event.shiftKey) return;
      const target = /** @type {HTMLElement} */ (event.target);
      const rows = this.#rows();
      const rtl = getComputedStyle(this).direction === 'rtl';
      const forward = rtl ? 'ArrowLeft' : 'ArrowRight';
      const back = rtl ? 'ArrowRight' : 'ArrowLeft';
      const row = /** @type {HTMLTableRowElement | undefined} */ (rows.find((r) => r === target));
      if (row && this.#rowFocus(row)) {
        if (event.ctrlKey && event.key !== 'Home' && event.key !== 'End') return;
        const walk = rows.filter((r) => this.#rowFocus(r));
        const at = walk.indexOf(row);
        const step = (/** @type {number} */ by) => walk[Math.min(walk.length - 1, Math.max(0, at + by))];
        const expanded = row.getAttribute('aria-expanded');
        /** @type {HTMLElement | null | undefined} */
        let next = null;
        if (event.key === forward) {
          if (expanded === 'false') this.#expand(row, true);
          else next = row.cells.length ? representative(row.cells[0]) : null;
        } else if (event.key === back) {
          if (expanded === 'true') this.#expand(row, false);
          else next = this.#parent(row);
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
      if (!owner || !this.#rowFocus(owner)) return;
      event.preventDefault();
      owner.focus();
    });
    this.use(gridFocus, {
      rows: () => this.#rows(),
      cells: (/** @type {HTMLTableRowElement} */ row) => [...row.cells],
      page: () => PAGE,
      rowFocus: (/** @type {HTMLElement} */ row) => this.#rowFocus(row),
      // When tree changes the table's role changes, which the behaviour watches (J79), so nothing is listed here.
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its cleanup
    // disconnects.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'data-level', 'aria-expanded', 'colspan', 'hidden'] });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
