<script lang="ts">
  // grid.svelte: a grid, and with `tree` a treegrid, for Svelte (docs/specs/targets.md, V1 to V7; rules J68 to J71
  // and J79 of docs/specs/patterns.md, B19 and B20 of docs/specs/foundation.md).
  //
  // The root is a <div>, a block around the author's own native table, the child marked data-part="table". The table
  // is the author's: this component never clones, wraps or renders it. It finds it in the DOM, as the Web Component
  // and the React grid do, and writes on it and its rows, only where they differ, in an effect after mount, again
  // when `tree` or `expanded` changes, and on each change in its subtree (an observer, since the author's markup
  // re-renders without this component): the grid role, or treegrid, aria-rowcount, aria-colcount, each row's
  // aria-rowindex, and with `tree` each row's aria-level from its data-level and `hidden` on every row below a closed
  // row. It never shows a row the author hid. It mounts gridFocus with the class's options, which writes the cells'
  // tabindex and data-editing (J79). None of it is rendered, so the server markup carries none of it.
  //
  // The treegrid's own keys (J70) go through onkeydowncapture on the root. gridFocus listens on the root in the bubble
  // phase, and a delegated onkeydown would run after it; the capture phase runs first, so these keys are handled and
  // their default prevented before gridFocus, which passes over a key whose default is already prevented. That is the
  // order the class has.
  //
  // Which rows are open is the author's aria-expanded on a row that has child rows, as on the Web Component. With no
  // `expanded`, the author's value is where the row starts, and the grid writes aria-expanded when the user opens or
  // closes a row. `expanded`, the ids of the open rows, is $bindable: given, the grid writes aria-expanded on every row
  // that carries it from that list; a plain value only starts it, `bind:expanded` follows the user, and a binding whose
  // setter keeps its value decides alone. onexpandedchange(expanded, event) is called once each time the user opens or
  // closes a row, with the ids of the rows that would then be open, after the rows are written. A row is named by its
  // `id`; a row with no id cannot be opened through `expanded`.
  import { flushSync, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { gridFocus, representative, textEntry } from '../../behaviours/grid-focus.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    tree?: boolean;
    /** The ids of the open rows, for `bind:expanded`; none, and the author's aria-expanded holds them. */
    expanded?: string[];
    onexpandedchange?: (expanded: string[], event: KeyboardEvent) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { tree = false, expanded = $bindable(), onexpandedchange, onkeydowncapture, ref = $bindable(null), children, ...rest }: Props = $props();

  type State = { tree: boolean, expanded: string[] | undefined };

  /** The rows PageDown and PageUp move, as on the Web Component. */
  const PAGE = 5;
  const TABLE = ':scope > [data-part="table"]';

  /** Sets or removes an attribute, only when it differs. The observers then see nothing when nothing changes. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };
  /** A row's level: its data-level when that is a whole number of 1 or more, or else 1. */
  const levelOf = (row: Element) => {
    const level = Number(row.getAttribute('data-level'));
    return Number.isInteger(level) && level >= 1 ? level : 1;
  };
  /** The author's table: the child marked data-part="table", when it is a table. */
  const tableOf = (root: HTMLElement) => {
    const table = root.querySelector(TABLE);
    return table instanceof HTMLTableElement ? table : null;
  };
  /** Every row of the table, its header and footer rows included, in order. */
  const allRows = (root: HTMLElement) => [...(tableOf(root)?.rows ?? [])];
  /** The rows that show. */
  const shownRows = (root: HTMLElement) => allRows(root).filter((row) => !row.hidden);
  /** Whether a row takes focus itself: a body row of a treegrid. */
  const rowFocusOf = (isTree: boolean, row: HTMLElement) => isTree && row.parentElement?.localName !== 'thead';
  /** The row a row belongs to: the nearest row before it of a lower level. */
  const parentOf = (root: HTMLElement, row: HTMLTableRowElement) => {
    const all = allRows(root);
    const level = levelOf(row);
    for (let n = all.indexOf(row) - 1; n >= 0; n--) if (levelOf(all[n]) < level) return all[n];
    return null;
  };

  /** The rows this grid hid, so that it never shows one the author hid. */
  const hid = new WeakSet<HTMLTableRowElement>();
  /** The props as they are now, read where no effect tracks them. */
  const now = (): State => ({ tree: !!tree, expanded });

  /**
   * Writes the roles, the counts, the levels, which rows are open when `expanded` is given, and which rows show.
   * Writes nothing when they are already right.
   */
  const sync = (root: HTMLElement, { tree: isTree, expanded: open }: State) => {
    const table = tableOf(root);
    if (!table) return;
    const rows = [...table.rows];
    put(table, 'role', isTree ? 'treegrid' : 'grid');
    put(table, 'aria-rowcount', String(rows.length));
    put(table, 'aria-colcount', String(Math.max(0, ...rows.map((row) => [...row.cells].reduce((sum, cell) => sum + cell.colSpan, 0)))));
    /** The rows above this one that have child rows. */
    const above: { level: number, open: boolean }[] = [];
    rows.forEach((row, n) => {
      put(row, 'aria-rowindex', String(n + 1));
      const level = levelOf(row);
      put(row, 'aria-level', isTree && row.hasAttribute('data-level') ? String(level) : null);
      if (open && row.hasAttribute('aria-expanded')) put(row, 'aria-expanded', String(row.id !== '' && open.includes(row.id)));
      while (above.length && above[above.length - 1].level >= level) above.pop();
      const shut = isTree && above.some((a) => !a.open);
      if (shut && !row.hidden) { row.hidden = true; hid.add(row); }
      else if (!shut && hid.has(row)) { hid.delete(row); row.hidden = false; }
      const state = row.getAttribute('aria-expanded');
      if (state === 'true' || state === 'false') above.push({ level, open: state === 'true' });
    });
  };

  // gridFocus, mounted once with the class's options. `ref` is read untracked: a parent's function binding re-reads
  // it whenever the parent's own state changes, and a rerun would lose what the behaviour holds. When `tree` changes
  // the table's role changes, which the behaviour watches (J79).
  $effect(() => untrack(() => {
    const el = ref;
    if (!el) return;
    return gridFocus(el, {
      rows: () => shownRows(el),
      cells: (row: HTMLElement) => [...(row as HTMLTableRowElement).cells],
      page: () => PAGE,
      rowFocus: (row: HTMLElement) => rowFocusOf(!!tree, row),
    });
  }));

  // The observer, mounted once: the author's rows change without this component rendering.
  $effect(() => untrack(() => {
    const el = ref;
    if (!el) return;
    const observer = new MutationObserver(() => sync(el, now()));
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'data-level', 'aria-expanded', 'colspan', 'hidden'] });
    sync(el, now());
    return () => observer.disconnect();
  }));

  // When tree or expanded changes, in the same flush, so a script reads the roles and the rows that show as soon as
  // the change is flushed.
  $effect(() => {
    const state = { tree: !!tree, expanded: expanded ? [...expanded] : undefined };
    untrack(() => { if (ref) sync(ref, state); });
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });

  /** Opens or closes a row because the user asked for it. */
  const expand = (root: HTMLElement, row: HTMLTableRowElement, open: boolean, event: KeyboardEvent) => {
    const given = expanded;
    const ids = given ?? allRows(root).filter((r) => r.id !== '' && r.getAttribute('aria-expanded') === 'true').map((r) => r.id);
    const next = row.id === '' ? ids : open ? [...ids.filter((id) => id !== row.id), row.id] : ids.filter((id) => id !== row.id);
    if (given === undefined) {
      put(row, 'aria-expanded', String(open));
      // The rows below it show or hide before onexpandedchange is called.
      sync(root, now());
    } else {
      // Held or bound: the effect above writes the rows from the new value. A binding that keeps its value decides.
      expanded = next;
      flushSync();
    }
    onexpandedchange?.(next, event);
  };

  /** The treegrid's keys (J70), before gridFocus's. */
  const keys = (event: KeyboardEvent & { currentTarget: EventTarget & HTMLDivElement }) => {
    onkeydowncapture?.(event);
    const el = ref;
    if (!el || !tree || event.defaultPrevented || event.altKey || event.metaKey || event.shiftKey) return;
    const target = event.target as HTMLElement;
    const rows = shownRows(el);
    const rtl = getComputedStyle(el).direction === 'rtl';
    const forward = rtl ? 'ArrowLeft' : 'ArrowRight';
    const back = rtl ? 'ArrowRight' : 'ArrowLeft';
    const row = rows.find((r) => r === target);
    if (row && rowFocusOf(true, row)) {
      if (event.ctrlKey && event.key !== 'Home' && event.key !== 'End') return;
      const walk = rows.filter((r) => rowFocusOf(true, r));
      const at = walk.indexOf(row);
      const step = (by: number) => walk[Math.min(walk.length - 1, Math.max(0, at + by))];
      const open = row.getAttribute('aria-expanded');
      let next: HTMLElement | null | undefined = null;
      if (event.key === forward) {
        if (open === 'false') expand(el, row, true, event);
        else next = row.cells.length ? representative(row.cells[0]) : null;
      } else if (event.key === back) {
        if (open === 'true') expand(el, row, false, event);
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
    if (!owner || !rowFocusOf(true, owner)) return;
    event.preventDefault();
    owner.focus();
  };
</script>

<div
  {...rest}
  bind:this={ref}
  data-ui="grid"
  onkeydowncapture={keys}
>{@render children?.()}</div>
