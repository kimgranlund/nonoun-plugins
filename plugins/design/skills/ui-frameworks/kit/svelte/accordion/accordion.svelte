<script lang="ts">
  // accordion.svelte: the element that stacks disclosures, for Svelte (docs/specs/targets.md, V1 to V7; rule J11 of
  // docs/specs/patterns.md).
  //
  // The root is a <div> with no role; its recipe stacks its children with a hairline between them. Its
  // disclosures are its child elements, whatever they are: one nested deeper belongs to whatever holds it. They are
  // of another family, so with `single` it finds them in the DOM, as the Web Component does, not through context:
  // when one of them gains `open`, from the user or from a script, it removes `open` from the others through their
  // own author attribute (G3), and a Svelte disclosure follows that write and tells its binding. It renders no
  // attribute a disclosure writes. `single` is read when a disclosure opens, so a change of it applies to the next.
  import type { Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    /** Opening one disclosure closes the others. */
    single?: boolean;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { single = false, ref = $bindable(null), children, ...rest }: Props = $props();

  $effect(() => {
    const el = ref as HTMLDivElement;
    const observer = new MutationObserver((records) => {
      // Read here, when a disclosure opens, not when the observer starts.
      if (!single) return;
      /** The last child that gained open and still has it. */
      let opened: Element | null = null;
      for (const r of records) {
        const target = r.target as Element;
        if (target.parentElement === el && r.oldValue === null && target.hasAttribute('open')) opened = target;
      }
      if (!opened) return;
      // Removing an attribute that is absent changes nothing and is not recorded, so this writes only what differs.
      for (const child of el.children) if (child !== opened) child.removeAttribute('open');
    });
    observer.observe(el, { subtree: true, attributes: true, attributeFilter: ['open'], attributeOldValue: true });
    return () => observer.disconnect();
  });

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
  data-ui="accordion"
  data-single={single ? '' : undefined}
>{@render children?.()}</div>
