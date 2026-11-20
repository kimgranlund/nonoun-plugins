<script lang="ts">
  import { untrack } from 'svelte';
  // tab-list.svelte: the list of tabs, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="tablist">. It mounts roving focus as the Web Component does, so it is one stop in the
  // Tab order and the arrow keys move among its tabs (B6 to B10); the behaviour writes the tabs' tabindex, which no
  // tab renders. ARIA's default orientation for a tablist is horizontal, so only vertical is written.
  import type { Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { rovingFocus } from '../../behaviours/roving-focus.js';
  import { props as spec, role } from '../../components/tab-list/tab-list.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    orientation?: 'horizontal' | 'vertical';
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { orientation, ref = $bindable(null), children, ...rest }: Props = $props();

  const p = spec.orientation as { values: readonly string[], default: string };
  const o = $derived((p.values.includes(orientation ?? '') ? orientation : p.default) as 'horizontal' | 'vertical');

  const TAB = '[role="tab"]';
  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  const tabsOf = (el: HTMLElement) => [...el.querySelectorAll<HTMLElement>(TAB)];

  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<div
  {...rest}
  bind:this={ref}
  {role}
  data-ui="tab-list"
  aria-orientation={o === 'vertical' ? 'vertical' : undefined}
  {@attach (el) => untrack(() => rovingFocus(el, {
    items: () => tabsOf(el),
    orientation: () => o,
    current: () => tabsOf(el).find((tab) => tab.getAttribute('aria-selected') === 'true'),
    skip: disabled,
    watch: ['aria-selected'],
  }))}
>{@render children?.()}</div>
