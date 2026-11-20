<script lang="ts">
  // splitter.svelte: the splitter for Svelte (docs/specs/targets.md, V1 to V7; J62 and J63 of docs/specs/patterns.md).
  //
  // The root is a <div> with data-ui="splitter" and no role, around the two panes the author writes, marked
  // data-part="start" and data-part="end", which are found in the DOM and never cloned, moved or wrapped. After them
  // it renders the bar the Web Component creates, <div data-part="bar"> with the separator role, a Tab stop,
  // aria-valuemin, -max and -now, the name Resize from the manifest's messages, aria-orientation across the split, and
  // aria-controls naming the first pane, which gets an id from $props.id() when it has none (J63). The share of the
  // first pane goes to the recipe as --_share on the root's style, beside the author's own, so the server markup is
  // laid out at any share before hydration. Vertical is the author attribute orientation="vertical", which the
  // condition selects: a div with no role cannot carry aria-orientation (X2). As the React splitter.
  //
  // value is $bindable: bind:value follows the user, a plain value only starts it (50 by default). oninput(value,
  // event) is called while the bar moves and onchange(value, event) when the user has finished, once the root shows
  // the share. Keys go through onkeydown on the bar; a drag captures the pointer on the bar, through native listeners
  // added in an effect.
  import { flushSync, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec } from '../../components/splitter/splitter.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'oninput' | 'onchange'> & {
    value?: number;
    min?: number;
    max?: number;
    orientation?: 'horizontal' | 'vertical';
    /** Called while the user moves the bar, once the root shows the share. */
    oninput?: (value: number, event: Event) => void;
    /** Called when the user has finished: after a key, or at the end of a drag that moved the bar. */
    onchange?: (value: number, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { value = $bindable(), min, max, orientation, oninput, onchange, ref = $bindable(null), children, ...rest }: Props = $props();

  /** The bar's name when the author gave none: messages.bar in splitter.manifest.json. */
  const NAME = 'Resize';
  /** A number prop's default from the manifest. */
  const fallback = (prop: string): number => (spec[prop] as { default?: number }).default ?? 0;
  /** A prop that should be a number, or the default when it is none. */
  const numberOr = (v: unknown, d: number): number => (typeof v === 'number' && Number.isFinite(v) ? v : d);
  /** An enum prop's value, or its default when the value is not one of the manifest's. */
  const pick = (prop: string, given: unknown): string => {
    const p = spec[prop] as { values: readonly string[], default: string };
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };
  const clamp = (n: number, lo: number, hi: number) => Math.min(Math.max(n, lo), hi);

  const uid = $props.id();
  // The limits and the share as they are used: 0 ≤ min ≤ value ≤ max ≤ 100.
  const lo = $derived(clamp(numberOr(min, fallback('min')), 0, 100));
  const hi = $derived(clamp(numberOr(max, fallback('max')), lo, 100));
  const now = $derived(clamp(numberOr(value, fallback('value')), lo, hi));
  const vertical = $derived(pick('orientation', orientation) === 'vertical');
  /** The id of the first pane, which the bar names in aria-controls; null while there is no first pane. */
  let controls: string | null = $state(null);
  let bar: HTMLDivElement | null = $state(null);
  /** The share the first pane had when Enter last collapsed it. */
  let restore: number | null = null;
  /** The drag in progress: the pointer, where it held the bar, and the share it started from. */
  let drag: { id: number, grip: number, from: number } | null = null;

  // aria-controls on the first pane, which the author may add or replace later; a pane with no id gets one.
  $effect(() => untrack(() => {
    const el = ref;
    if (!el) return;
    const name = () => {
      const start = el.querySelector(':scope > [data-part="start"]');
      if (start && !start.id) start.id = uid;
      return start ? start.id : null;
    };
    controls = name();
    const observer = new MutationObserver(() => { controls = name(); flushSync(); });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['id', 'data-part'] });
    return () => observer.disconnect();
  }));

  /** Moves the bar to a share, rounded to hundredths and held inside the limits, and calls oninput when it moved. */
  const move = (share: number, event: Event): boolean => {
    const next = clamp(Math.round(share * 100) / 100, lo, hi);
    if (next === now) return false;
    value = next;
    flushSync();
    oninput?.(next, event);
    return true;
  };

  /** The room the two panes share, along the split: the root's content box less the bar. */
  const room = (el: HTMLDivElement, b: HTMLDivElement) => {
    const rect = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    const px = (name: string) => parseFloat(s.getPropertyValue(name)) || 0;
    const rtl = s.direction === 'rtl';
    const padStart = vertical ? px('padding-top') + px('border-top-width') : px(rtl ? 'padding-right' : 'padding-left') + px(rtl ? 'border-right-width' : 'border-left-width');
    const content = vertical
      ? rect.height - px('padding-top') - px('padding-bottom') - px('border-top-width') - px('border-bottom-width')
      : rect.width - px('padding-left') - px('padding-right') - px('border-left-width') - px('border-right-width');
    const size = b.getBoundingClientRect();
    return { rect, start: padStart, length: content - (vertical ? size.height : size.width) };
  };

  /** How far a pointer is along the split from the start edge of a box: from the top, the left, or the right right to left. */
  const along = (el: HTMLDivElement, event: PointerEvent, rect: DOMRect, offset = 0) => {
    if (vertical) return event.clientY - rect.top - offset;
    return getComputedStyle(el).direction === 'rtl' ? rect.right - event.clientX - offset : event.clientX - rect.left - offset;
  };

  const keydown = (event: KeyboardEvent) => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || !ref) return;
    const rtl = getComputedStyle(ref).direction === 'rtl';
    const keys: Record<string, number> = vertical ? { ArrowUp: -1, ArrowDown: 1 } : { ArrowLeft: rtl ? 1 : -1, ArrowRight: rtl ? -1 : 1 };
    let next: number;
    if (event.key in keys) next = now + keys[event.key];
    else if (event.key === 'Home') next = lo;
    else if (event.key === 'End') next = hi;
    else if (event.key === 'Enter') {
      if (now > lo) { restore = now; next = lo; }
      else if (restore !== null) next = restore;
      else return;
    } else return;
    event.preventDefault();
    if (move(next, event)) onchange?.(now, event);
  };

  // The pointer: a press on the bar grabs it where it was pressed and captures the pointer; the drag ends when the
  // capture is lost, which follows a release, a cancel and the bar leaving the document.
  $effect(() => {
    const b = bar, el = untrack(() => ref);
    if (!b || !el) return;
    const stop = new AbortController();
    const listen = { signal: stop.signal };
    b.addEventListener('pointerdown', (event) => {
      if (event.button !== 0) return;
      // WebKit selects the text a captured drag passes over unless the press is cancelled; Chromium and Firefox do not.
      event.preventDefault();
      b.focus({ preventScroll: true });
      drag = { id: event.pointerId, grip: along(el, event, b.getBoundingClientRect()), from: now };
      b.setPointerCapture(event.pointerId);
    }, listen);
    b.addEventListener('pointermove', (event) => {
      const d = drag;
      if (!d || event.pointerId !== d.id) return;
      const r = room(el, b);
      if (r.length <= 0) return;
      move(((along(el, event, r.rect, r.start) - d.grip) / r.length) * 100, event);
    }, listen);
    b.addEventListener('lostpointercapture', (event) => {
      const d = drag;
      if (!d || event.pointerId !== d.id) return;
      drag = null;
      if (now !== d.from) onchange?.(now, event);
    }, listen);
    return () => stop.abort();
  });

  // The root has no orientation of its own: it is an author attribute, as on the Web Component.
  const mirrored = $derived({ orientation: vertical ? 'vertical' : undefined });

  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<div
  {...rest}
  bind:this={ref}
  data-ui="splitter"
  {...mirrored}
  style:--_share={String(now)}
>{@render children?.()}<!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions: a separator that is moved is a widget (J63) --><div
  bind:this={bar}
  data-part="bar"
  role="separator"
  tabindex="0"
  aria-label={NAME}
  aria-valuemin={lo}
  aria-valuemax={hi}
  aria-valuenow={now}
  aria-orientation={vertical ? 'horizontal' : 'vertical'}
  aria-controls={controls ?? undefined}
  onkeydown={keydown}
></div></div>
