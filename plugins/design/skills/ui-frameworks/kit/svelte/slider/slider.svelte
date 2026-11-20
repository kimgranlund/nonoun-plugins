<script lang="ts">
  // slider.svelte: the slider for Svelte (docs/specs/targets.md, V1 to V7; J53 to J56 of docs/specs/patterns.md).
  //
  // The root is a <div> with the slider role, the control itself: no native element is a slider whose track, fill
  // and thumb the recipe can draw as pseudo-elements. It takes focus, so :hover, :focus-visible and :active are its
  // own, and its states are ARIA attributes the role allows: aria-valuemin, aria-valuemax, aria-valuenow,
  // aria-orientation while vertical and aria-disabled while disabled (X2). The value's share of the range, a number
  // from 0 to 1, goes to the recipe as the private custom property --_share on the root's style, beside the author's
  // own, so the server markup is painted at the value before hydration. As the React slider.
  //
  // A div is no form control, so a hidden input marked data-part="input" carries name and value (V6): the form
  // submits it, a disabled slider submits nothing, and a form reset puts the value back to its first one (F6). A
  // disabled fieldset around the slider disables it too: the component watches the fieldsets around it at mount.
  //
  // value is $bindable: bind:value follows the user, a plain value only starts it. oninput(value, event) is called
  // while the user changes the value and onchange(value, event) when they have finished: after each key, and at the
  // end of a pointer gesture that moved it; the root already shows the value. A change by a prop calls neither. Keys
  // go through onkeydown on the root, after the author's own; the pointer is captured on the root by native
  // listeners added in an effect, so the author's onpointerdown and the like still reach the root.
  import { flushSync, untrack } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec, role as kitRole, tabindex } from '../../components/slider/slider.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'oninput' | 'onchange' | 'role'> & {
    value?: number;
    min?: number;
    max?: number;
    step?: number;
    orientation?: 'horizontal' | 'vertical';
    name?: string;
    disabled?: boolean;
    /** Called while the user changes the value, once the root shows it. */
    oninput?: (value: number, event: Event) => void;
    /** Called when the user has finished: after a key, or at the end of a gesture that moved the value. */
    onchange?: (value: number, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
  };

  let {
    value = $bindable(), min, max, step, orientation, name, disabled = false,
    oninput, onchange, onkeydown, ref = $bindable(null), ...rest
  }: Props = $props();

  type Range = { min: number, max: number, step: number };
  /** A number prop's default from the manifest. */
  const fallback = (prop: string): number => (spec[prop] as { default?: number }).default ?? 0;
  /** An enum prop's value, or its default when the value is not one of the manifest's. */
  const pick = (prop: string, given: unknown): string => {
    const p = spec[prop] as { values: readonly string[], default: string };
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };
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
  /** How many steps a key moves the value; Home and End are handled apart. */
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
  const now = $derived(hold(numberOr(value, 0), range));
  const vertical = $derived(pick('orientation', orientation) === 'vertical');
  let fieldsetOff = $state(false);
  const off = $derived(disabled || fieldsetOff);
  const share = $derived(String(range.max > range.min ? (now - range.min) / (range.max - range.min) : 0));
  // The first value, which a form reset restores (F6).
  const first = untrack(() => value);
  /** The value when the pointer went down, while a gesture runs. */
  let start: number | null = null;

  /** Sets the value the user chose, held, and calls oninput once the root shows it, if it changed. */
  const choose = (next: number, event: Event): boolean => {
    const v = hold(next, range);
    if (v === now) return false;
    value = v;
    flushSync();
    oninput?.(v, event);
    return true;
  };

  /** The value under the pointer: the thumb's centre runs from half a thumb after the start to half a thumb before the end. */
  const at = (el: HTMLElement, event: PointerEvent): number => {
    const r = el.getBoundingClientRect();
    const thumb = parseFloat(getComputedStyle(el, '::after').width) || 0;
    const rtl = !vertical && getComputedStyle(el).direction === 'rtl';
    const along = vertical ? r.bottom - event.clientY : rtl ? r.right - event.clientX : event.clientX - r.left;
    const length = (vertical ? r.height : r.width) - thumb;
    const part = length > 0 ? Math.min(Math.max((along - thumb / 2) / length, 0), 1) : 0;
    return range.min + part * (range.max - range.min);
  };

  const keydown = (event: KeyboardEvent & { currentTarget: EventTarget & HTMLDivElement }) => {
    onkeydown?.(event);
    if (event.defaultPrevented || off || event.altKey || event.ctrlKey || event.metaKey) return;
    // Right to left swaps the left and right arrows of a horizontal slider; the direction is read now.
    const rtl = !vertical && getComputedStyle(event.currentTarget).direction === 'rtl';
    const steps = stepsOf(event.key, rtl);
    const next = event.key === 'Home' ? range.min : event.key === 'End' ? range.max : steps === undefined ? null : now + steps * range.step;
    if (next === null) return;
    event.preventDefault();
    if (choose(next, event)) onchange?.(now, event);
  };

  // The pointer: a press moves the value there and captures the pointer on the root; the gesture ends when the
  // capture is lost, which follows a release, a cancel and the root leaving the document.
  $effect(() => {
    const el = ref;
    if (!el) return;
    const stop = new AbortController();
    el.addEventListener('pointerdown', (event) => {
      if (off || event.button !== 0) return;
      start = now;
      el.setPointerCapture(event.pointerId);
      choose(at(el, event), event);
    }, { signal: stop.signal });
    el.addEventListener('pointermove', (event) => {
      if (start !== null && !off) choose(at(el, event), event);
    }, { signal: stop.signal });
    el.addEventListener('lostpointercapture', (event) => {
      if (start === null) return;
      const before = start;
      start = null;
      if (now !== before) onchange?.(now, event);
    }, { signal: stop.signal });
    return () => stop.abort();
  });

  // A disabled fieldset around the slider disables it (F4); its disabled attribute is watched, since no event tells.
  $effect(() => {
    const el = ref;
    if (!el) return;
    fieldsetOff = fenced(el);
    const observer = new MutationObserver(() => { fieldsetOff = fenced(el); flushSync(); });
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) observer.observe(f, { attributes: true, attributeFilter: ['disabled'] });
    return () => observer.disconnect();
  });

  // A form reset puts the hidden input back by itself; the value goes back to its first one (F6).
  $effect(() => {
    const form = ref?.querySelector('input')?.form;
    if (!form) return;
    const stop = new AbortController();
    form.addEventListener('reset', () => setTimeout(() => { value = first; flushSync(); }), { signal: stop.signal });
    return () => stop.abort();
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<!-- svelte-ignore a11y_no_noninteractive_tabindex: the role, read from the generated props, is slider -->
<div
  {...rest}
  bind:this={ref}
  role={kitRole}
  data-ui="slider"
  tabindex={off ? undefined : tabindex}
  aria-valuemin={range.min}
  aria-valuemax={range.max}
  aria-valuenow={now}
  aria-orientation={vertical ? 'vertical' : undefined}
  aria-disabled={off ? 'true' : undefined}
  style:--_share={share}
  onkeydown={keydown}
><input type="hidden" data-part="input" {name} value={String(now)} disabled={off} /></div>
