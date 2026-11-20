<script lang="ts">
  // spinbutton.svelte: the spinbutton for Svelte (docs/specs/targets.md, V1 to V7; J59 to J61, J81 and J48 of
  // docs/specs/patterns.md).
  //
  // The root is a <span> with data-ui="spinbutton" and no role: a field around the author's native text input, the
  // child marked data-part="input" (D14), which is found in the DOM and never cloned, moved or wrapped. The input
  // carries the name and the value and takes part in the form by itself; this component gives it the spinbutton role,
  // inputmode and aria-valuemin, -max and -now (J59), steps it from the keys and from the two buttons it renders after
  // the author's children, <span data-part="decrease"> and <span data-part="increase"> (J60), and makes it invalid
  // with setCustomValidity when its text is not a number or lies outside the limits. Once the user is due to be told
  // (J48) it writes aria-invalid on the input and renders invalid on the root. As the React spinbutton.
  //
  // States (X2): the root has no role, so disabled and invalid are the author attributes the conditions select;
  // focus-within and hover are the root's own pseudo-classes; read-only is the input's own readonly, which the recipe
  // reads through :has(). A disabled field disables the input, and enables only an input it disabled.
  //
  // The input's own input and change are the manifest's events: a step writes the value and dispatches input then
  // change, bubbling, from the input, so bind:value on the author's input follows a step. Keys go through onkeydown on
  // the root, after the author's own; the input, blur and invalid of the input are heard by native listeners added in
  // an effect, so the author's oninput and onfocusout on the root still reach it.
  import { flushSync, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec } from '../../components/spinbutton/spinbutton.props.js';

  type Props = Omit<HTMLAttributes<HTMLSpanElement>, 'children'> & {
    min?: number;
    max?: number;
    step?: number;
    disabled?: boolean;
    /** The root, for `bind:ref`. */
    ref?: HTMLSpanElement | null;
    children?: Snippet;
  };

  let { min, max, step, disabled = false, onkeydown, onpointerdown, ref = $bindable(null), children, ...rest }: Props = $props();

  /** The names of the two buttons: messages.increase and messages.decrease in spinbutton.manifest.json. */
  const NAMES = { increase: 'Increase', decrease: 'Decrease' };
  /** What the browser shows for an invalid value: messages.notANumber, rangeUnderflow and rangeOverflow in the manifest. */
  const NOT_A_NUMBER = 'Enter a number.';
  const BELOW = (n: number) => `Enter a number of ${n} or more.`;
  const ABOVE = (n: number) => `Enter a number of ${n} or less.`;
  /** The keys that step, and by how many steps. Home and End go to a limit instead. */
  const STEPS: Record<string, number> = { ArrowUp: 1, ArrowDown: -1, PageUp: 10, PageDown: -10 };

  /** The step's default from the manifest. */
  const stepDefault = (): number => (spec.step as { default?: number }).default ?? 1;
  /** A limit is set when it is a number; with none there is no limit. */
  const limitOf = (v: unknown): number | null => (typeof v === 'number' && Number.isFinite(v) ? v : null);
  /** The number a text says: null for an empty text, NaN for one that is not a number. */
  const read = (text: string): number | null => {
    const t = text.trim();
    if (t === '') return null;
    const n = Number(t);
    return Number.isFinite(n) ? n : NaN;
  };
  /** How many decimals a number is written with. */
  const decimals = (n: number): number => { const text = String(n); const dot = text.indexOf('.'); return dot === -1 ? 0 : text.length - dot - 1; };
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };
  /** The author's input, a direct child marked data-part="input", looked up each time. */
  const inputOf = (el: Element | null): HTMLInputElement | null => {
    const found = el?.querySelector(':scope > [data-part="input"]');
    return found instanceof HTMLInputElement ? found : null;
  };

  const lo = $derived(limitOf(min));
  const hi = $derived(limitOf(max));
  /** The invalid mark is shown on the root (J48). */
  let shown = $state(false);
  /** What the component holds: the user changed the input, the user is due to be told, the mark it wrote, the message it set, the input it disabled. */
  const held = { changed: false, told: false, marked: false, message: '', disabledInput: null as HTMLInputElement | null };

  /** Writes everything the input and the root carry. It runs at mount, when a prop changes and after each event that may change them. */
  const sync = () => {
    const el = inputOf(ref);
    if (!el) return;
    if (disabled) {
      if (!el.disabled) { el.disabled = true; held.disabledInput = el; }
    } else if (held.disabledInput) {
      held.disabledInput.disabled = false;
      held.disabledInput = null;
    }
    if (!el.hasAttribute('role')) el.setAttribute('role', 'spinbutton');
    if (!el.hasAttribute('inputmode')) el.setAttribute('inputmode', 'decimal');
    put(el, 'aria-valuemin', lo === null ? null : String(lo));
    put(el, 'aria-valuemax', hi === null ? null : String(hi));
    const n = read(el.value);
    put(el, 'aria-valuenow', n === null || Number.isNaN(n) ? null : String(n));
    const message = n === null ? '' : Number.isNaN(n) ? NOT_A_NUMBER : lo !== null && n < lo ? BELOW(lo) : hi !== null && n > hi ? ABOVE(hi) : '';
    if (message !== held.message) { el.setCustomValidity(message); held.message = message; }
    // Only a mark this component wrote is taken off: an author's aria-invalid and invalid stay as written.
    const show = held.told && !el.validity.valid;
    if (show || held.marked) {
      put(el, 'aria-invalid', show ? 'true' : null);
      held.marked = show;
      shown = show;
    }
  };
  /** Brings everything in step from a native listener, so the root shows it before the listener returns. */
  const now = () => { if (ref?.isConnected) { sync(); flushSync(); } };

  const setup = (el: HTMLSpanElement) => {
    const stop = new AbortController();
    const listen = { signal: stop.signal };
    el.addEventListener('input', (event) => { if (event.target === inputOf(el)) { held.changed = true; now(); } }, listen);
    // blur does not bubble: focusout is the input's leaving.
    el.addEventListener('focusout', (event) => {
      if (event.target !== inputOf(el)) return;
      if (held.changed) held.told = true;
      now();
    }, listen);
    // invalid does not bubble: the submit attempt reaches the root in the capture phase.
    el.addEventListener('invalid', (event) => { if (event.target === inputOf(el)) { held.told = true; now(); } }, { capture: true, signal: stop.signal });
    // A reset restores the input after the event, so the state is read again in the next task.
    el.ownerDocument.addEventListener('reset', (event) => {
      const field = inputOf(el);
      if (!field || event.target !== field.form) return;
      held.changed = held.told = false;
      setTimeout(now);
    }, listen);
    // An input put in or marked later by markup that re-renders without this component, or by a script, is seen by
    // an observer, in a microtask.
    const observer = new MutationObserver(now);
    observer.observe(el, { childList: true, attributes: true, subtree: true, attributeFilter: ['data-part'] });
    sync();
    return () => { stop.abort(); observer.disconnect(); };
  };

  // Mounted once. `ref` is read untracked: a parent's function binding re-reads it whenever the parent's own state
  // changes, and a rerun here would forget what the user has been told.
  $effect(() => untrack(() => (ref ? setup(ref) : undefined)));
  // min, max, step and disabled take effect in the flush that changes them.
  $effect(() => {
    void lo; void hi; void disabled;
    untrack(sync);
  });

  /** Writes a value, held inside the limits, and dispatches input and change from the input when it changed. */
  const set = (value: number) => {
    const el = inputOf(ref);
    if (!el || el.disabled || el.readOnly) return;
    let next = value;
    if (hi !== null) next = Math.min(next, hi);
    if (lo !== null) next = Math.max(next, lo);
    const text = String(next);
    if (el.value === text) return;
    el.value = text;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    // A page that rewrites the input from its own oninput does so in its flush: read the input again after it.
    queueMicrotask(now);
  };

  /** Steps the value by count steps, held inside the limits. A step from an empty field starts at the minimum, or at 0. */
  const stepBy = (count: number) => {
    const el = inputOf(ref);
    if (!el) return;
    const given = step ?? stepDefault();
    const size = typeof given === 'number' && given > 0 ? given : 1;
    const n = read(el.value);
    if (n === null || Number.isNaN(n)) { set(lo ?? 0); return; }
    const places = Math.max(decimals(size), decimals(n));
    set(Number((n + count * size).toFixed(places)));
  };

  const keydown = (event: KeyboardEvent & { currentTarget: EventTarget & HTMLSpanElement }) => {
    onkeydown?.(event);
    const el = inputOf(event.currentTarget);
    if (!el || event.target !== el || event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.key in STEPS) {
      event.preventDefault();
      stepBy(STEPS[event.key]);
    } else if (event.key === 'Home' || event.key === 'End') {
      const limit = event.key === 'Home' ? lo : hi;
      if (limit === null) return;
      event.preventDefault();
      set(limit);
    }
  };

  /** A press anywhere on the field but the input keeps focus in the input (J60) and puts it there (J47). */
  const pointerdown = (event: PointerEvent & { currentTarget: EventTarget & HTMLSpanElement }) => {
    onpointerdown?.(event);
    const root = event.currentTarget;
    const el = inputOf(root);
    if (!el || event.target === el || !(event.target instanceof Node) || !root.contains(event.target)) return;
    event.preventDefault();
    if (!el.disabled && document.activeElement !== el) el.focus({ preventScroll: true });
  };

  // The span has no disabled or invalid of its own: they are author attributes, as on the Web Component. An invalid
  // the author wrote stays as written (J48).
  const mirrored = $derived({ disabled: disabled ? '' : undefined, invalid: shown ? '' : (rest as Record<string, unknown>).invalid });

  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions: the keys are the author's input's, which bubble to the root -->
<span
  {...rest}
  bind:this={ref}
  data-ui="spinbutton"
  {...mirrored}
  onkeydown={keydown}
  onpointerdown={pointerdown}
>{@render children?.()}<!-- svelte-ignore a11y_click_events_have_key_events, a11y_interactive_supports_focus: not a Tab stop; the keys of the input do the same (J60) --><span data-part="decrease" role="button" tabindex="-1" aria-label={NAMES.decrease} aria-disabled={disabled ? 'true' : undefined} onclick={() => stepBy(-1)}></span><!-- svelte-ignore a11y_click_events_have_key_events, a11y_interactive_supports_focus --><span data-part="increase" role="button" tabindex="-1" aria-label={NAMES.increase} aria-disabled={disabled ? 'true' : undefined} onclick={() => stepBy(1)}></span></span>
