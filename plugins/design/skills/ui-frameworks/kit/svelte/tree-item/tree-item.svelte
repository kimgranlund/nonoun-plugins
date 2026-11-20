<script lang="ts">
  // tree-item.svelte: one item of a tree, for Svelte (docs/specs/targets.md, V1 to V7; rules J32 to J35 of
  // docs/specs/patterns.md).
  //
  // The root is a <div role="treeitem">; it takes focus, and the tree's roving focus writes its tabindex, which it
  // never renders. Its row is the author's child marked `data-part="label"`, and the items inside it are in the
  // author's child marked `data-part="group"`; both are rendered as the author writes them. It renders
  // `aria-selected` ("true" or "false") from its tree's value, `aria-expanded` while it has a group, `aria-disabled`
  // and `aria-level`, from a level context, so the server markup paints every state.
  //
  // The server renders in one pass, so an item cannot know of its group while it renders its own attributes: until
  // it has read the page, an item has a group when it is expanded, which paints the same (a closed group is
  // hidden either way). Its value is its `value` prop, or else the trimmed text of its label, which it reads from
  // the page once mounted: on the server, a tree value that names an item by its label selects it once it has
  // hydrated. Give the item a value for that server markup.
  //
  // `expanded` is $bindable: `bind:expanded` holds it, a plain `expanded` only starts it. onexpandedchange(expanded,
  // event) is called once when the user opens or closes the item, once the item is written. `selected` marks the
  // item: it gives the tree's first value, and a mark that comes or goes later selects the item or clears the
  // tree's value. The tree's value decides which item is selected.
  //
  // Into the DOM, once mounted and whenever its subtree changes, and only where it differs, it writes what belongs
  // to the author's parts: the group role on a group that has no role, an id on a label that has none, and
  // `aria-labelledby` naming the label unless the author named the item: without it, the item's name would include
  // the text of every item in its group.
  import { flushSync, getContext, setContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { TREE, LEVEL, type TreeContext, type TreeEntry } from '../tree/tree.context.js';
  import { role } from '../../components/tree-item/tree-item.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'role'> & {
    value?: string;
    selected?: boolean;
    expanded?: boolean;
    disabled?: boolean;
    /** Called once the page shows an open or a close the user made, with the new state and the event that made it. */
    onexpandedchange?: (expanded: boolean, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { value, selected = false, expanded = $bindable(false), disabled = false, onexpandedchange, ref = $bindable(null), children, ...rest }: Props = $props();

  const uid = $props.id();
  const GROUP = ':scope > [data-part="group"]';
  const LABEL = ':scope > [data-part="label"]';
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, name: string, to: string | null) => {
    if (el.getAttribute(name) === to) return;
    if (to === null) el.removeAttribute(name);
    else el.setAttribute(name, to);
  };

  const tree = getContext<TreeContext | undefined>(TREE);
  const level = getContext<number | undefined>(LEVEL);
  setContext(LEVEL, (level ?? 0) + 1);

  /** The root, kept after unmount. */
  let node: HTMLDivElement | null = null;
  /** Whether the page shows a group, and the label's text; null until the item has read them. */
  let domGroup: boolean | null = $state(null);
  let domText: string | null = $state(null);
  const hasGroup = $derived(domGroup ?? expanded);
  const own = $derived(value ?? domText ?? undefined);
  /** The item's value as the page has it now. */
  const read = () => value ?? ((node ?? ref)?.querySelector(LABEL)?.textContent ?? '').trim();

  const entry: TreeEntry = {
    get el() { return node ?? ref; },
    get selected() { return selected; },
    own: () => own,
    read,
    hasGroup: () => (node ?? ref)?.querySelector(GROUP) != null,
    expanded: () => expanded,
    // Opens or closes the item because the user asked, through the tree's keys or a click on the label.
    expand(next, event) {
      expanded = next;
      flushSync();
      onexpandedchange?.(next, event);
    },
  };
  tree?.add(entry);
  $effect(() => () => tree?.remove(entry));

  const isSelected = $derived(tree ? tree.selects(entry) : selected);

  /** The aria-labelledby value this item wrote, so that it never replaces an author's. */
  let named: string | null = null;
  /** Writes the author's parts' role, id and name, and reads the group and the label text back. */
  const sync = () => {
    const el = node;
    if (!el) return;
    const group = el.querySelector(GROUP);
    if (group && !group.hasAttribute('role')) group.setAttribute('role', 'group');
    // A name the author gave stays (A2). One this item gave follows the label.
    const name = el.getAttribute('aria-labelledby');
    if (name === null || name === named) {
      const label = el.hasAttribute('aria-label') ? null : el.querySelector(LABEL);
      if (label && !label.id) label.id = `${uid}-label`;
      named = label ? label.id : null;
      put(el, 'aria-labelledby', named);
    }
    if (domGroup !== Boolean(group)) domGroup = Boolean(group);
    const text = (el.querySelector(LABEL)?.textContent ?? '').trim();
    if (domText !== text) domText = text;
  };

  $effect(() => {
    const el = untrack(() => ref)!;
    node = el;
    untrack(sync);
    // The children change without this item knowing: an author's markup, or a script.
    const observer = new MutationObserver(() => {
      sync();
      flushSync();
    });
    observer.observe(el, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['data-part', 'id', 'aria-label', 'aria-labelledby'] });
    return () => observer.disconnect();
  });

  // A mark: the tree takes those of the items created with it; later it selects the item or clears it.
  let mounted = false;
  $effect(() => {
    const on = selected;
    untrack(() => {
      const mounting = !mounted;
      mounted = true;
      if (mounting && (!on || tree?.early(entry))) return;
      tree?.mark(entry, on);
    });
  });

  // A new value: on the selected item it becomes the tree's.
  let before: string | undefined;
  $effect(() => {
    const now = own;
    untrack(() => {
      if (before !== undefined && now !== undefined && before !== now) tree?.renamed(entry, before, now);
      before = now;
    });
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<!-- svelte-ignore a11y_interactive_supports_focus: the tree's roving focus writes the item's tabindex -->
<div
  {...rest}
  bind:this={ref}
  {role}
  data-ui="tree-item"
  aria-selected={String(isSelected) as 'true' | 'false'}
  aria-expanded={hasGroup ? String(expanded) as 'true' | 'false' : undefined}
  aria-disabled={disabled ? 'true' : undefined}
  aria-level={tree && level ? level : undefined}
>{@render children?.()}</div>
