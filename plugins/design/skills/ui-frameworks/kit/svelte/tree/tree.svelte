<script lang="ts">
  // tree.svelte: a tree, for Svelte (docs/specs/targets.md, V1 to V7; rules J32 to J35 of docs/specs/patterns.md).
  //
  // The root is a <div role="tree">. It never takes focus itself: its items do. It mounts roving focus, which keeps
  // one item that shows (every item around it is expanded) in the Tab order and moves focus with ArrowDown, ArrowUp,
  // Home and End without wrapping, and typeahead, which moves focus to the item whose label starts with what is
  // typed. Both write the DOM when they mount, so they are mounted in effects. Its own keys go through onkeydown on
  // the root, which Svelte runs after the behaviours' listeners: ArrowRight and ArrowLeft open and close an item or
  // move to its first child or its parent (swapped in a right-to-left scope), and Enter and Space select. No key is
  // shared: roving focus is vertical, so it leaves the inline arrows alone, and typeahead leaves Space and every key
  // whose name is longer than one letter. A click on an item's label selects the item, and opens or closes it when
  // it has a group; a press on a disabled item gives focus to nothing. As the React tree.
  //
  // It coordinates its items through context (tree.context.js). `value` is $bindable: `bind:value` holds it, a plain
  // `value` only starts it. With none, it is the value of the first item marked `selected`; items register as they
  // are created, so the server markup already selects that item. Of two items with the same value, the one the user
  // or a mark picked is selected, or else the first in the document. A mark that comes later selects its item, and
  // clearing the selected item's mark clears the value, as a script's mark does on the Web Component.
  // onchange(value, event) is called once the user selects another item, after the items are written (J34); never
  // for a change of the value prop, nor for a mark.
  //
  // Into the DOM, only where they differ, after each change and on each change of its subtree, it writes
  // `aria-setsize` and `aria-posinset` on its items: their siblings are in groups the author writes, which the tree
  // cannot count while it renders. Each item renders its own `aria-level`, `aria-selected`, `aria-expanded` and
  // `aria-disabled`.
  import { flushSync, setContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { rovingFocus } from '../../behaviours/roving-focus.js';
  import { typeahead } from '../../behaviours/typeahead.js';
  import { TREE, LEVEL, type TreeContext, type TreeEntry } from './tree.context.js';
  import { role } from '../../components/tree/tree.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'onchange' | 'role'> & {
    value?: string;
    onchange?: (value: string, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { value = $bindable(), onchange, onkeydown, onclick, onmousedown, ref = $bindable(null), children, ...rest }: Props = $props();

  const ITEM = '[role="treeitem"]';
  const TREES = '[role="tree"]';
  const LABEL = ':scope > [data-part="label"]';

  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, name: string, to: string | null) => {
    if (el.getAttribute(name) === to) return;
    if (to === null) el.removeAttribute(name);
    else el.setAttribute(name, to);
  };
  /** The items of a tree, and not of another tree nested in one, in document order. */
  const ownOf = (tree: Element) => [...tree.querySelectorAll<HTMLElement>(ITEM)].filter((item) => item.closest(TREES) === tree);
  /** The item whose group holds this one, or null at the top of the tree. */
  const parentIn = (tree: Element, item: Element) => {
    const parent = item.parentElement?.closest<HTMLElement>(ITEM) ?? null;
    return parent && parent.closest(TREES) === tree ? parent : null;
  };
  /** Whether an item shows: every item around it is expanded. */
  const showsIn = (tree: Element, item: Element) => {
    for (let parent = parentIn(tree, item); parent; parent = parentIn(tree, parent)) if (parent.getAttribute('aria-expanded') !== 'true') return false;
    return true;
  };

  type Pick = { entry: TreeEntry | null, value: string };
  /** The items as they registered: in document order while they are created. */
  let entries: TreeEntry[] = $state.raw([]);
  /** Whether the tree has taken the marks of the items created with it. */
  let settled = $state(false);
  /** The item last picked by the user or a mark, which wins over another item of the same value. */
  let picked: Pick | null = $state.raw(null);
  /** The first item in the document with the value, once the items are in the page. */
  let first: Pick | null = $state.raw(null);
  /** The items created before the tree settled: their marks are the tree's to take. */
  const early = new Set<TreeEntry>();
  /** The root, kept after unmount, so that a listener that outlived it would still act, and be seen. */
  let node: HTMLDivElement | null = null;

  const ownItems = () => (node ? ownOf(node) : []);
  const entryOf = (item: Element) => entries.find((e) => e.el === item);
  /** The item that holds the value when two have it, or null when any item of the value may. */
  const target = () => (picked && picked.value === value ? picked.entry : first && first.value === value ? first.entry : null);
  /** The first item marked selected, as the items registered. */
  const marked = () => entries.find((e) => e.selected);
  const hold = (v: string, entry: TreeEntry | null) => {
    value = v;
    picked = entry ? { entry, value: v } : null;
  };

  setContext<TreeContext>(TREE, {
    // A function of the tree's state, not $derived: on the server a derived keeps the value it first had.
    selects(entry) {
      if (value === undefined) return !settled && entry === marked();
      if (value === '' || entry.own() !== value) return false;
      const t = target();
      return t === null || t === entry;
    },
    add(entry) {
      if (!settled) early.add(entry);
      entries = [...entries, entry];
    },
    remove(entry) {
      early.delete(entry);
      entries = entries.filter((e) => e !== entry);
    },
    early: (entry) => early.has(entry),
    mark(entry, on) {
      const v = entry.read();
      if (on) {
        if (v === '' || (picked?.entry === entry && value === v)) return;
        // A mark made later, or an item that arrives carrying one: that item is now the value.
        hold(v, entry);
      } else if (target() === entry && value === v) {
        // The selected item's mark was cleared: nothing is selected.
        hold('', null);
      }
    },
    renamed(entry, from, to) {
      // A new value on the selected item becomes the tree's.
      const t = target();
      if (value !== from || (t !== null && t !== entry) || to === '') return;
      hold(to, entry);
    },
  });

  /** Writes the items' position among their siblings, and finds the first item of the value. Writes nothing when they are up to date. */
  const sync = () => {
    const all = ownItems();
    const siblings = new Map<HTMLElement | null, HTMLElement[]>();
    for (const item of all) {
      const parent = parentIn(node!, item);
      siblings.set(parent, [...(siblings.get(parent) ?? []), item]);
    }
    for (const item of all) {
      const set = siblings.get(parentIn(node!, item))!;
      put(item, 'aria-setsize', String(set.length));
      put(item, 'aria-posinset', String(set.indexOf(item) + 1));
    }
    if (value === undefined || value === '' || (picked && picked.value === value)) return;
    const found = all.find((item) => entryOf(item)?.read() === value);
    const entry = found ? entryOf(found) ?? null : null;
    if (!(first && first.value === value && first.entry === entry)) first = { entry, value };
  };

  /** Selects an item because the user asked, then tells onchange, which finds the items already written. */
  const choose = (item: HTMLElement, event: Event) => {
    const entry = entryOf(item);
    if (!entry) return;
    const v = entry.read();
    // The item that holds the value already: once the page is read, the picked item or the first of the value.
    if (target() === entry) return;
    picked = { entry, value: v };
    value = v;
    flushSync();
    onchange?.(v, event);
  };

  const keydown = (event: KeyboardEvent & { currentTarget: HTMLDivElement }) => {
    onkeydown?.(event);
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    // Focus is on an item itself. A key from inside an item's label, or from an item of another tree, is not this
    // tree's: and the item is the target, so a key is handled once, for it.
    const item = event.target as HTMLElement;
    if (!ownItems().includes(item)) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      choose(item, event);
      return;
    }
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    const entry = entryOf(item);
    const rtl = getComputedStyle(node!).direction === 'rtl';
    const opening = (event.key === 'ArrowRight') !== rtl;
    const group = entry?.hasGroup() ?? false;
    event.preventDefault();
    if (opening) {
      if (!group || !entry) return;
      if (!entry.expanded()) { entry.expand(true, event); return; }
      ownItems().find((child) => parentIn(node!, child) === item && !disabled(child))?.focus();
    } else {
      if (group && entry?.expanded()) { entry.expand(false, event); return; }
      parentIn(node!, item)?.focus(); // a disabled parent has no tabindex, so it takes no focus
    }
  };

  /** A press on a disabled item gives focus to nothing, not to the item around it. */
  const mousedown = (event: MouseEvent & { currentTarget: HTMLDivElement }) => {
    onmousedown?.(event);
    const item = event.target instanceof Element ? event.target.closest(ITEM) : null;
    if (item && item.closest(TREES) === node && disabled(item)) event.preventDefault();
  };

  /** A click on an item's label selects the item, and opens or closes it. */
  const click = (event: MouseEvent & { currentTarget: HTMLDivElement }) => {
    onclick?.(event);
    if (event.defaultPrevented) return;
    const label = event.target instanceof Element ? event.target.closest('[data-part="label"]') : null;
    const item = (label?.parentElement ?? null) as HTMLElement | null;
    if (!label || !item || !ownItems().includes(item) || disabled(item)) return;
    // The press already gave the item focus: it is the focusable element around its label.
    choose(item, event);
    const entry = entryOf(item);
    if (entry?.hasGroup()) entry.expand(!entry.expanded(), event);
  };

  // The first items are in: the first marked one gives the value, unless the tree was given one.
  $effect(() => {
    untrack(() => {
      node = ref;
      settled = true;
      if (value !== undefined) return;
      const m = entries.find((e) => e.selected && e.read() !== '');
      if (m) hold(m.read(), m);
    });
  });
  // Items that come, go or move in the page: their positions, and the first item of the value.
  $effect(() => {
    const el = untrack(() => ref)!;
    const observer = new MutationObserver(() => {
      sync();
      flushSync();
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role'] });
    return () => observer.disconnect();
  });
  // After each change of the value or of an item's: the first item of the value may be another.
  $effect(() => {
    void value;
    for (const e of entries) e.own();
    untrack(sync);
  });
  // The behaviours read the element they were given, so that only their cleanup ends them.
  $effect(() => {
    const el = untrack(() => ref)!;
    const showing = () => ownOf(el).filter((item) => showsIn(el, item));
    return rovingFocus(el, {
      items: showing,
      orientation: () => 'vertical',
      wrap: false,
      current: () => ownOf(el).find((item) => item.getAttribute('aria-selected') === 'true' && showsIn(el, item)),
      skip: disabled,
      watch: ['aria-expanded', 'aria-selected'],
    });
  });
  $effect(() => {
    const el = untrack(() => ref)!;
    return typeahead(el, {
      items: () => ownOf(el).filter((item) => showsIn(el, item)),
      skip: disabled,
      text: (item: HTMLElement) => item.querySelector(LABEL)?.textContent ?? '',
      onMatch: (item: HTMLElement) => item.focus(),
    });
  });

  setContext(LEVEL, 1);

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<!-- svelte-ignore a11y_interactive_supports_focus: the tree takes no focus; roving focus gives it to its items -->
<div
  {...rest}
  bind:this={ref}
  {role}
  data-ui="tree"
  onkeydown={keydown}
  onclick={click}
  onmousedown={mousedown}
>{@render children?.()}</div>
