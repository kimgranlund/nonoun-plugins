<script lang="ts">
  // icon.svelte: one icon from the kit's set, drawn by CSS in the ink of whatever it sits in, for Svelte
  // (docs/specs/targets.md, V1 to V7; docs/specs/icons.md, I1 to I8).
  //
  // The root is a <span> with data-ui="icon" and the name attribute: kit/styles/icons.css gives each glyph on this
  // root as well as on the Web Component's `ui-icon` tag, and the recipe selects the size by data-size. Nothing needs
  // a script to paint it (I1). The icon names itself as the Web Component does (I8): with no aria-label or
  // aria-labelledby it is hidden from assistive technology, with one it is an image, and an aria-hidden or a role
  // the author wrote is never replaced. It writes no label. As the React icon.
  import type { Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec } from '../../components/icon/icon.props.js';

  type Props = Omit<HTMLAttributes<HTMLElement>, 'children'> & {
    name?: string;
    size?: 'sm' | 'md' | 'lg' | 'full';
    /** The root, for `bind:ref`. */
    ref?: HTMLElement | null;
    /** Taken and not rendered: the icon draws nothing of its own, so the root stays empty (X1). */
    children?: Snippet;
  };

  let { name, size, ref = $bindable(null), children: _children, ...rest }: Props = $props();

  /** An enum prop's value, or its default when the value is not one of the manifest's. */
  const pick = (prop: string, given: unknown): string => {
    const p = spec[prop] as { values: readonly string[], default: string };
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };

  // An empty aria-label still names the icon: it is the author's, and is left as written.
  const named = $derived(rest['aria-label'] !== undefined || rest['aria-labelledby'] !== undefined);
  const hidden = $derived(named ? rest['aria-hidden'] : (rest['aria-hidden'] ?? 'true'));
  const role = $derived(named ? (rest.role ?? 'img') : rest.role);
  // The span has no name attribute of its own in Svelte's types, so it is spread: the glyph rules select it.
  const glyph = $derived({ name });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<span
  {...rest}
  bind:this={ref}
  {...glyph}
  data-ui="icon"
  data-size={pick('size', size)}
  aria-hidden={hidden}
  {role}
></span>
