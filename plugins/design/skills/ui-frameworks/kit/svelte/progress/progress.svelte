<script lang="ts">
  // progress.svelte: how far a task has got, shown as a filled track, or that it is running when how far is not
  // known, for Svelte (docs/specs/targets.md, V1 to V7; rules J96 and J97 of docs/specs/patterns.md).
  //
  // The root is a <div> with the progressbar role. Its aria-valuemin and aria-valuemax follow min and max, and its
  // aria-valuenow follows value, held between min and max (J96). It is indeterminate when `value` is undefined or
  // null, and 0 is a value: the root then renders no `value` attribute, which is the form its recipe selects for the
  // moving run (`:not([value])`), no aria-valuenow and no --_share. With a value, the share of the range, a number
  // from 0 to 1, goes to the recipe as the private custom property --_share on the root's inline style, as on the
  // Web Component (J97); it is the one style this component writes, and the author's own style is kept beside it.
  // As the React progress.
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec, role as kitRole } from '../../components/progress/progress.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    value?: number | null;
    min?: number;
    max?: number;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
  };

  let { value, min, max, role = kitRole, ref = $bindable(null), ...rest }: Props = $props();

  /** A number prop's value, or its default when the value is not a finite number. */
  const num = (prop: string, given: unknown): number => {
    const n = typeof given === 'string' && given.trim() === '' ? NaN : Number(given);
    return given !== undefined && given !== null && Number.isFinite(n) ? n : (spec[prop] as { default?: number }).default ?? 0;
  };

  // The range as it is used: max is never below min, and the value is held inside.
  const low = $derived(num('min', min));
  const high = $derived(Math.max(num('max', max), low));
  const determinate = $derived(value !== undefined && value !== null);
  const now = $derived(Math.min(Math.max(num('value', value), low), high));
  // As the author gave them, as on the Web Component; a div has no value, min or max in Svelte's types, so they are spread.
  const authored = $derived({ value, min, max });
  const share = $derived(determinate ? String(high > low ? (now - low) / (high - low) : 0) : undefined);

  // In the browser Svelte gives a spread `value` to the element as a property, which a div only keeps as an expando;
  // the server writes it as the attribute. The attribute is the state the recipe selects, so it is written here too;
  // a value that goes back to undefined or null takes Svelte's other path, which removes the attribute.
  $effect(() => {
    const root = ref;
    if (value !== undefined && value !== null) root?.setAttribute('value', String(value));
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6): the run starts then.
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
  data-ui="progress"
  {...authored}
  aria-valuemin={low}
  aria-valuemax={high}
  aria-valuenow={determinate ? now : undefined}
  style:--_share={share}
></div>
