<script lang="ts">
  // toolbar.svelte: a row of controls that is one stop in the Tab order, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="toolbar">. Its controls are the author's elements of other families, so it finds them
  // in the DOM by their role, as the Web Component and the React toolbar do: the button, checkbox, switch and link
  // roles, a native button, a native link, and the native checkbox, whose role is implicit (the Svelte checkbox's
  // input). It mounts roving focus in an effect after mount, which writes their tabindex and moves focus among them
  // with the arrow keys (J19); no control renders a tabindex of its own, so the server markup carries none. Vertical
  // is written as aria-orientation, ARIA's form (X2).
  import { untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { rovingFocus } from '../../behaviours/roving-focus.js';
  import { props as spec, role } from '../../components/toolbar/toolbar.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    orientation?: 'horizontal' | 'vertical';
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { orientation, ref = $bindable(null), children, ...rest }: Props = $props();

  const p = spec.orientation as { values: readonly string[], default: string };
  const o = $derived((p.values.includes(orientation ?? '') ? orientation : p.default) as 'horizontal' | 'vertical');

  /** What counts as a control. The Web Component's list, and the native checkbox, whose checkbox role is implicit. */
  const CONTROL = '[role="button"], [role="checkbox"], [role="switch"], [role="link"], button, a[href], input[type="checkbox"]';
  const ROOT = '[role="toolbar"]';
  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

  const setup = (el: HTMLDivElement) => {
    /** Whether a control lies inside another control below this toolbar: it is a part of that one. */
    const inside = (c: Element) => { const up = c.parentElement?.closest(CONTROL); return !!up && el.contains(up); };
    // In document order; a control of a toolbar nested in this one is that toolbar's.
    const controls = () => [...el.querySelectorAll<HTMLElement>(CONTROL)].filter((c) => c.closest(ROOT) === el && !inside(c));
    return rovingFocus(el, {
      items: controls,
      orientation: () => o,
      skip: disabled,
      // A control that writes its own tabindex="0" later brings the stop back to one.
      watch: ['tabindex'],
    });
  };

  // Mounted once, after hydration, since roving focus writes the controls' tabindex. `ref` is read untracked: a
  // rerun would mount the behaviour again whenever a parent re-reads its binding.
  $effect(() => untrack(() => (ref ? setup(ref) : undefined)));

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
  data-ui="toolbar"
  aria-orientation={o === 'vertical' ? 'vertical' : undefined}
>{@render children?.()}</div>
