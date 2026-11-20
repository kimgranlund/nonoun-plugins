<script lang="ts">
  // range-slider.svelte: the range slider for Svelte (docs/specs/targets.md, V1 to V7; J57 and J58 of
  // docs/specs/patterns.md, with J53 to J55 for each thumb).
  //
  // The root is a <div> with the group role and data-ui="range-slider". After the author's children it renders the two
  // thumbs the Web Component creates, <span data-part="low"> and <span data-part="high">, each with the slider role, a
  // Tab stop, the name Minimum or Maximum from the manifest's messages, and the limits the other thumb leaves it; then
  // two hidden inputs marked data-part="input" that carry the name twice, the low value first, as the class submits it
  // (V6). Each value's share of the range goes to the recipe as --_low and --_high on the root's style, beside the
  // author's own. Disabled is aria-disabled on the root, which its role allows, and on each thumb, which then has no
  // Tab stop (X2). A disabled fieldset around it disables it too: the component watches the fieldsets around it at
  // mount. As the React range slider.
  //
  // low and high are each $bindable: bind:low and bind:high follow the user, a plain low or high only starts it.
  // oninput({ low, high }, event) is called while the user changes a value and onchange({ low, high }, event) when
  // they have finished, once the DOM shows the new values. Keys go through onkeydown on the thumb that has focus; a
  // press on the track is captured on the root by native listeners added in an effect, and moves the nearer thumb,
  // which takes focus.
  import { flushSync, untrack } from 'svelte';
  import type { Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec, role as kitRole } from '../../components/range-slider/range-slider.props.js';

  type Pair = { low: number, high: number };
  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'oninput' | 'onchange' | 'role'> & {
    low?: number;
    high?: number;
    min?: number;
    max?: number;
    step?: number;
    name?: string;
    disabled?: boolean;
    /** Called while the user changes a value, once the thumbs show it. */
    oninput?: (value: Pair, event: Event) => void;
    /** Called when the user has finished: after a key, or at the end of a gesture that moved a value. */
    onchange?: (value: Pair, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let {
    low = $bindable(), high = $bindable(), min, max, step, name, disabled = false,
    oninput, onchange, ref = $bindable(null), children, ...rest
  }: Props = $props();

  /** The thumbs' names: messages.low and messages.high in range-slider.manifest.json. */
  const MESSAGES = { low: 'Minimum', high: 'Maximum' };
  type Thumb = 'low' | 'high';
  const THUMBS: Thumb[] = ['low', 'high'];
  type Range = { min: number, max: number, step: number };

  /** A number prop's default from the manifest. */
  const fallback = (prop: string): number => (spec[prop] as { default?: number }).default ?? 0;
  /** A prop that should be a number, or the default when it is none. */
  const numberOr = (v: unknown, d: number): number => (typeof v === 'number' && Number.isFinite(v) ? v : d);
  /** The decimals of a number as written, so that a step of 0.1 gives 0.3 and not 0.30000000000000004. */
  const decimals = (n: number): number => {
    const text = String(n), exp = text.indexOf('e-');
    if (exp !== -1) return Number(text.slice(exp + 2));
    const dot = text.indexOf('.');
    return dot === -1 ? 0 : text.length - dot - 1;
  };
  /** A number held between min and max and on a step counted from min. */
  const hold = (v: number, { min: a, max: b, step: s }: Range): number => {
    const places = Math.min(Math.max(decimals(a), decimals(s)), 12);
    const last = a + Math.floor((b - a) / s + 1e-9) * s;
    const steps = Math.round((Math.max(v, a) - a) / s);
    return Number(Math.min(a + steps * s, last).toFixed(places));
  };
  /** How many steps a key moves a value; Home and End are handled apart. */
  const stepsOf = (key: string, rtl: boolean): number | undefined => ({ ArrowRight: rtl ? -1 : 1, ArrowLeft: rtl ? 1 : -1, ArrowUp: 1, ArrowDown: -1, PageUp: 10, PageDown: -10 } as Record<string, number>)[key];
  /** Whether a disabled fieldset disables an element: it is inside one, and not inside that fieldset's first legend. */
  const fenced = (el: Element): boolean => {
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) {
      if (!f.disabled) continue;
      const legend = [...f.children].find((c) => c.localName === 'legend');
      if (!legend || !legend.contains(el)) return true;
    }
    return false;
  };

  // The range as it is used: max is never below min, and the step is above 0.
  const range: Range = $derived.by(() => {
    const lo = numberOr(min, fallback('min'));
    const s = numberOr(step, fallback('step'));
    return { min: lo, max: Math.max(numberOr(max, fallback('max')), lo), step: s > 0 ? s : 1 };
  });
  // Both values are held in the range and on a step, and the high value is never below the low one.
  const now: Pair = $derived.by(() => {
    const a = hold(numberOr(low, 0), range);
    return { low: a, high: Math.max(hold(numberOr(high, 0), range), a) };
  });
  const limits: Record<Thumb, [number, number]> = $derived({ low: [range.min, now.high], high: [now.low, range.max] });
  let fieldsetOff = $state(false);
  const off = $derived(disabled || fieldsetOff);
  const share = (v: number) => String(range.max > range.min ? (v - range.min) / (range.max - range.min) : 0);
  // The first values, which a form reset restores (F6).
  const first = untrack(() => ({ low, high }));
  /** A thumb of the root, a child marked with its part. */
  const part = (el: HTMLElement, thumb: Thumb) => el.querySelector<HTMLSpanElement>(`:scope > [data-part="${thumb}"]`);
  /** The thumb that follows the pointer, and its value when the gesture began. */
  let drag: { thumb: Thumb, before: number } | null = null;

  /** Sets one value as the user chose it, held inside that thumb's limits, and calls oninput once the DOM shows it, if it changed. */
  const choose = (thumb: Thumb, next: number, event: Event): boolean => {
    const [from, to] = limits[thumb];
    const v = Math.min(Math.max(hold(next, range), from), to);
    if (v === now[thumb]) return false;
    if (thumb === 'low') low = v; else high = v;
    flushSync();
    oninput?.({ ...now }, event);
    return true;
  };

  /** The value under the pointer: a thumb's centre runs from half a thumb after the start to half a thumb before the end. */
  const at = (el: HTMLElement, event: PointerEvent): number => {
    const r = el.getBoundingClientRect();
    const thumb = part(el, 'low')?.getBoundingClientRect().width ?? 0;
    const rtl = getComputedStyle(el).direction === 'rtl';
    const along = rtl ? r.right - event.clientX : event.clientX - r.left;
    const length = r.width - thumb;
    const fraction = length > 0 ? Math.min(Math.max((along - thumb / 2) / length, 0), 1) : 0;
    return range.min + fraction * (range.max - range.min);
  };

  /** The thumb nearer to a value; on a tie, the one that can move towards it. */
  const nearer = (v: number): Thumb => {
    const v2 = hold(v, range);
    const toLow = Math.abs(v2 - now.low), toHigh = Math.abs(v2 - now.high);
    if (toLow !== toHigh) return toLow < toHigh ? 'low' : 'high';
    return v2 < now.low || (v2 === now.low && now.high === range.max) ? 'low' : 'high';
  };

  const keydown = (thumb: Thumb, event: KeyboardEvent) => {
    if (off || event.altKey || event.ctrlKey || event.metaKey) return;
    // Right to left swaps the left and right arrows; the direction is read now. Home and End go to the ends of the
    // range, which choose() holds inside what the other thumb leaves.
    const steps = stepsOf(event.key, getComputedStyle(ref as HTMLDivElement).direction === 'rtl');
    const next = event.key === 'Home' ? range.min : event.key === 'End' ? range.max : steps === undefined ? null : now[thumb] + steps * range.step;
    if (next === null) return;
    event.preventDefault();
    if (choose(thumb, next, event)) onchange?.({ ...now }, event);
  };

  // The pointer: a press moves the nearer thumb there, focuses it and captures the pointer on the root; the gesture
  // ends when the capture is lost, which follows a release, a cancel and the root leaving the document.
  $effect(() => {
    const el = ref;
    if (!el) return;
    const stop = new AbortController();
    el.addEventListener('pointerdown', (event) => {
      if (off || event.button !== 0) return;
      // Focus goes to the thumb that moves, not where the pointer went down, so the platform's own focusing is stopped.
      event.preventDefault();
      const v = at(el, event), thumb = nearer(v);
      drag = { thumb, before: now[thumb] };
      el.setPointerCapture(event.pointerId);
      part(el, thumb)?.focus();
      choose(thumb, v, event);
    }, { signal: stop.signal });
    el.addEventListener('pointermove', (event) => {
      if (drag && !off) choose(drag.thumb, at(el, event), event);
    }, { signal: stop.signal });
    el.addEventListener('lostpointercapture', (event) => {
      if (!drag) return;
      const { thumb, before } = drag;
      drag = null;
      if (now[thumb] !== before) onchange?.({ ...now }, event);
    }, { signal: stop.signal });
    return () => stop.abort();
  });

  // A disabled fieldset around the range slider disables it (F4); its disabled attribute is watched.
  $effect(() => {
    const el = ref;
    if (!el) return;
    fieldsetOff = fenced(el);
    const observer = new MutationObserver(() => { fieldsetOff = fenced(el); flushSync(); });
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) observer.observe(f, { attributes: true, attributeFilter: ['disabled'] });
    return () => observer.disconnect();
  });

  // A form reset puts the hidden inputs back by themselves; the values go back to their first ones (F6).
  $effect(() => {
    const form = ref?.querySelector<HTMLInputElement>(':scope > input[data-part="input"]')?.form;
    if (!form) return;
    const stop = new AbortController();
    form.addEventListener('reset', () => setTimeout(() => { low = first.low; high = first.high; flushSync(); }), { signal: stop.signal });
    return () => stop.abort();
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<div
  {...rest}
  bind:this={ref}
  role={kitRole}
  data-ui="range-slider"
  aria-disabled={off ? 'true' : undefined}
  style:--_low={share(now.low)}
  style:--_high={share(now.high)}
>{@render children?.()}{#each THUMBS as thumb (thumb)}<span
    data-part={thumb}
    role="slider"
    tabindex={off ? undefined : 0}
    aria-label={MESSAGES[thumb]}
    aria-valuemin={limits[thumb][0]}
    aria-valuemax={limits[thumb][1]}
    aria-valuenow={now[thumb]}
    aria-disabled={off ? 'true' : undefined}
    onkeydown={(event) => keydown(thumb, event)}
  ></span>{/each}{#each THUMBS as thumb (thumb)}<input type="hidden" data-part="input" {name} value={String(now[thumb])} disabled={off} />{/each}</div>
