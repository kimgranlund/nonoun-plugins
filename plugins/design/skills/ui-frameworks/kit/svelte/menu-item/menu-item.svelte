<script lang="ts">
  // menu-item.svelte: one action in a menu, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="menuitem">, which has no native disabled state, so disabled is written as
  // aria-disabled (X2). It mounts press, as the Web Component does, so Enter and Space click it; the menu's
  // roving focus writes its tabindex, and the menu closes when it is clicked. Its click is the root's own DOM
  // event, so `onclick` reaches the root with the other props.
  import { untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { press } from '../../behaviours/press.js';
  import { role } from '../../components/menu-item/menu-item.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'role'> & {
    /** The action cannot be run, and the item takes no focus. */
    disabled?: boolean;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { disabled = false, ref = $bindable(null), children, ...rest }: Props = $props();

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
  data-ui="menu-item"
  aria-disabled={disabled ? 'true' : undefined}
  {@attach (el) => press(el, { disabled: () => disabled })}
>{@render children?.()}</div>
