<script lang="ts">
  // menu-group.svelte: a set of menu items that belong together, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="group">. Of the radio items inside it, it keeps at most one checked: each radio item
  // adds itself through the family's context (menu-group.context.js), and when the user chooses one, the group
  // turns the others off (J22). A group inside it, or a submenu, starts afresh.
  //
  // Its label is the author's child marked data-part="label", which it never clones or wraps, so it names itself
  // as the Web Component does, in the DOM once mounted, whenever the author's name props change and whenever its
  // subtree changes: aria-labelledby to the label's id, giving the label an id only when it has none, unless the
  // author named the group (J23). As the React menu group.
  import { setContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { GROUP, type MenuGroupEntry, type MenuGroupState } from './menu-group.context.js';
  import { role } from '../../components/menu-group/menu-group.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'role'> & {
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { ref = $bindable(null), children, ...rest }: Props = $props();
  const uid = $props.id();

  /** The radio items of this group. */
  const entries = new Set<MenuGroupEntry>();
  setContext<MenuGroupState>(GROUP, {
    add: (entry) => { entries.add(entry); return () => { entries.delete(entry); }; },
    choose: (chosen) => { for (const entry of entries) if (entry !== chosen) entry.off(); },
  });

  /** The aria-labelledby value this element wrote, so that it never replaces an author's. */
  let named: string | null = null;

  /** Names the group after its label, unless the author named it. Writes nothing when it already is. */
  const name = () => {
    const el = untrack(() => ref);
    if (!el) return;
    const current = el.getAttribute('aria-labelledby');
    if (current !== null && current !== named) return;
    const label = [...el.children].find((c) => c.getAttribute('data-part') === 'label') as HTMLElement | undefined;
    // A name the author gave with aria-label wins: the reference this element wrote would hide it.
    if (!label || el.hasAttribute('aria-label')) {
      if (current !== null) el.removeAttribute('aria-labelledby');
      named = null;
      return;
    }
    if (!label.id) label.id = `${uid}-label`;
    if (current !== label.id) el.setAttribute('aria-labelledby', label.id);
    named = label.id;
  };

  // Once mounted, and in the flush that changes a name the author gives; the observer catches the label.
  $effect(() => {
    void rest['aria-label'];
    void rest['aria-labelledby'];
    untrack(name);
  });
  $effect(() => untrack(() => {
    const observer = new MutationObserver(name);
    observer.observe(ref!, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'id', 'aria-label'] });
    return () => observer.disconnect();
  }));

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<div
  {...rest}
  bind:this={ref}
  {role}
  data-ui="menu-group"
>{@render children?.()}</div>
