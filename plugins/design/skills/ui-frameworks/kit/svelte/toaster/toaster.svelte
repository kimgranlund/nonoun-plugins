<script lang="ts">
  // toaster.svelte: the stack that holds toasts, for Svelte (docs/specs/targets.md, V1 to V7; J94 of
  // docs/specs/patterns.md).
  //
  // The root is a <div> with the region role and popover="manual", named "Notifications" (strings.label) in
  // aria-label unless the author passed aria-label or aria-labelledby; a role or a popover the author passes wins
  // (J94). All of it is rendered, so the server markup has it too, and the server renders it out of the top layer.
  // In the browser it shows in the top layer exactly while one of its children has the status or the alert role
  // and `open`, and leaves it when none has. It finds toasts by role in the DOM, as the Web Component and React
  // do, so a toast of any target counts. It looks after mount, after each change of its own props, whenever a
  // child, its `open` or its role changes (a MutationObserver), and, in the same flush, when a Svelte toast inside
  // it opens, closes or goes (through the family's context). It writes nothing on a toast.
  //
  // `placement` is the variant data-placement: the recipe places the stack in that corner of the window, with the
  // newest toast, the last child, nearest it, and lets presses through wherever no toast is.
  import { setContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec, role as region } from '../../components/toaster/toaster.props.js';
  import { TOASTER, type ToasterContext } from './toaster.context.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    placement?: 'block-end inline-end' | 'block-end inline-start' | 'block-start inline-end' | 'block-start inline-start';
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { placement, ref = $bindable(null), children, ...rest }: Props = $props();

  /** The roles of a toast. */
  const ROLES = ['status', 'alert'];

  /** An enum prop's value, or its default when the value is not one of the manifest's. */
  const pick = (prop: string, given: unknown): string => {
    const p = spec[prop] as { values: readonly string[], default: string };
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };

  /** Shows the popover while a toast is open and hides it when none is. */
  const look = () => {
    const el = untrack(() => ref);
    // A popover the author took away leaves nothing to show.
    if (!el?.isConnected || !el.hasAttribute('popover')) return;
    const holds = [...el.children].some((x) => ROLES.includes(x.getAttribute('role') ?? '') && x.hasAttribute('open'));
    if (holds === el.matches(':popover-open')) return;
    if (holds) el.showPopover();
    else el.hidePopover();
  };
  setContext<ToasterContext>(TOASTER, { look });

  // Mounted once; `ref` is read untracked, so a parent's function binding does not start a second observer.
  $effect(() => untrack(() => {
    const el = ref;
    if (!el) return;
    const observer = new MutationObserver(look);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['open', 'role'] });
    return () => observer.disconnect();
  }));
  // After mount, and after each change of its own props, which can take the popover away or give it back: it
  // looks again in the flush that changed them.
  $effect(() => {
    void placement;
    void { ...rest };
    look();
  });

  const named = $derived(rest['aria-label'] !== undefined || rest['aria-labelledby'] !== undefined);
  const name = $derived(named ? {} : { 'aria-label': strings.label });

  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<script lang="ts" module>
  /**
   * The name the toaster has when the author gave it none, read at each render, as the Web Component's static
   * field is: `import { strings } from '.../toaster.svelte'` and write it.
   */
  export const strings = { label: 'Notifications' };
</script>

<div
  role={region}
  popover="manual"
  {...name}
  {...rest}
  bind:this={ref}
  data-ui="toaster"
  data-placement={pick('placement', placement)}
>{@render children?.()}</div>
