<script lang="ts">
  // meter.svelte: a value within a known range, shown as a filled track, for Svelte (docs/specs/targets.md, V1 to
  // V7; rules J17 and J18 of docs/specs/patterns.md).
  //
  // The root is a <div> with the meter role. Its aria-valuemin, aria-valuemax and aria-valuenow follow min, max
  // and value, with the value held between min and max and a max that is not above min treated as min (J17). The
  // value's share of the range, a number from 0 to 1, goes to the recipe as the private custom property --_share on
  // the root's inline style, as on the Web Component; it is the one style this component writes, and the author's
  // own style is kept beside it (J18). A value that is missing or is not a number reads as 0, as a number prop does
  // on the Web Component; the value attribute is rendered as the author gave it. As the React meter.
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec, role as kitRole } from '../../components/meter/meter.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    value?: number;
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
  const now = $derived(Math.min(Math.max(num('value', value), low), high));
  // As the author gave them, as on the Web Component; a div has no value, min or max in Svelte's types, so they are spread.
  const authored = $derived({ value, min, max });
  const share = $derived(String(high > low ? (now - low) / (high - low) : 0));

  // In the browser Svelte gives a spread `value` to the element as a property, which a div only keeps as an expando;
  // the server writes it as the attribute. The attribute is the state the recipe selects, so it is written here too;
  // a value that goes back to undefined or null takes Svelte's other path, which removes the attribute.
  $effect(() => {
    const root = ref;
    if (value !== undefined && value !== null) root?.setAttribute('value', String(value));
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
  {role}
  data-ui="meter"
  {...authored}
  aria-valuemin={low}
  aria-valuemax={high}
  aria-valuenow={now}
  style:--_share={share}
></div>
