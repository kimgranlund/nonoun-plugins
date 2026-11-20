<script lang="ts">
  // menu-item-checkbox.svelte: a menu item that is on or off, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="menuitemcheckbox">, which has no native checked or disabled state, so they are
  // written as aria-checked and aria-disabled (X2). It mounts press, as the Web Component does, so Enter and Space
  // click it. A click turns it on or off: `checked` is $bindable, so `bind:checked` follows the user and a plain
  // `checked` only starts it. onchange(checked, event) is called once per change, after the item is written and
  // while the menu is still open: the click listener is the item's own, native one, which runs before the menu's
  // (J22). The menu writes its tabindex, moves focus to it, and closes after Enter but not after Space or the
  // pointer. As the React menu item checkbox.
  import { flushSync, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { press } from '../../behaviours/press.js';
  import { role } from '../../components/menu-item-checkbox/menu-item-checkbox.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'role' | 'onchange'> & {
    /** The item is on: `bind:checked` follows the user, a plain `checked` only starts it. */
    checked?: boolean;
    /** It cannot be chosen or focused. */
    disabled?: boolean;
    /** Called once per change, with the new state and the click, once the item shows it. */
    onchange?: (checked: boolean, event: MouseEvent) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { checked = $bindable(false), disabled = false, onchange, ref = $bindable(null), children, ...rest }: Props = $props();

  // A native listener, so it runs before the menu's, which may close the menu (J22); the author's onclick, in
  // rest, still runs.
  $effect(() => untrack(() => {
    const el = ref!;
    const off = new AbortController();
    el.addEventListener('click', (event) => {
      if (disabled) return;
      // What the user asked for: a binding that keeps its own value leaves `checked` as it was.
      const next = !checked;
      checked = next;
      // Written before onchange is called, so a listener reads the item up to date.
      flushSync();
      onchange?.(next, event);
    }, { signal: off.signal });
    return () => off.abort();
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
  data-ui="menu-item-checkbox"
  aria-checked={String(checked) as 'true' | 'false'}
  aria-disabled={disabled ? 'true' : undefined}
  {@attach (el) => press(el, { disabled: () => disabled })}
>{@render children?.()}</div>
