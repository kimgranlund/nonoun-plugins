<script lang="ts">
  // breadcrumb.svelte: the trail of links from the top of a site to the current page, for Svelte
  // (docs/specs/targets.md, V1 to V7; rules J13 and J14 of docs/specs/patterns.md).
  //
  // The root is a native <nav>, which has the navigation role itself, so no role is written. It is named
  // "Breadcrumb" (messages.label of the manifest) unless the author wrote aria-label or aria-labelledby, an empty
  // aria-label included, so the server markup already carries the name. The links are the author's anchors and are
  // rendered as given; the author marks the current page with aria-current="page". As the React breadcrumb.
  import type { Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { role as kitRole } from '../../components/breadcrumb/breadcrumb.props.js';

  type Props = Omit<HTMLAttributes<HTMLElement>, 'children'> & {
    /** The root, for `bind:ref`. */
    ref?: HTMLElement | null;
    children?: Snippet;
  };

  let { ref = $bindable(null), children, ...rest }: Props = $props();

  /** The name written when the author wrote none: messages.label in breadcrumb.manifest.json. */
  const LABEL = 'Breadcrumb';
  // A <nav> has the role the manifest names; an author's own role goes through the rest.
  void kitRole;

  const named = $derived(rest['aria-label'] !== undefined || rest['aria-labelledby'] !== undefined);

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<nav
  {...rest}
  bind:this={ref}
  data-ui="breadcrumb"
  aria-label={named ? rest['aria-label'] : LABEL}
>{@render children?.()}</nav>
