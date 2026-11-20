<script lang="ts">
  // alert.svelte: a short message that assistive technology announces as soon as it appears, for Svelte
  // (docs/specs/targets.md, V1 to V7; rules J15 and J16 of docs/specs/patterns.md).
  //
  // The root is a <div> with the alert role unless the author wrote a role (role="status" for a polite message).
  // The variant is data-variant. It takes no focus and renders its children as given. As the React alert.
  import type { Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec, role as kitRole } from '../../components/alert/alert.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    variant?: 'neutral' | 'info' | 'success' | 'warning' | 'critical';
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { variant, role = kitRole, ref = $bindable(null), children, ...rest }: Props = $props();

  /** An enum prop's value, or its default when the value is not one of the manifest's. */
  const pick = (prop: string, given: unknown): string => {
    const p = spec[prop] as { values: readonly string[], default: string };
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
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
  data-ui="alert"
  data-variant={pick('variant', variant)}
>{@render children?.()}</div>
