<script lang="ts">
  // toast.svelte: an alert with a time limit, for Svelte (docs/specs/targets.md, V1 to V7; J92 to J95 of
  // docs/specs/patterns.md).
  //
  // The root is a <div> with the status role, or alert when the variant is critical, unless the author passed a
  // role (J92). Its open state is the author attribute `open` on the root, which the recipe gives a box from (X2);
  // the variant is data-variant. `open` is $bindable: `bind:open` holds it, a plain `open` only starts it.
  //
  // The time is the component's own, written with the Web Component's rules (J93): a toast that is open closes
  // itself `duration` milliseconds after it opened, or after it mounted open; with 0 it stays. The time does not
  // run while the pointer is over the toast or focus is inside it, and starts again from the full duration once
  // both have left. A press on a descendant marked data-part="close" of this toast, and Escape while focus is
  // inside (through the dismiss behaviour), close it. `onclose` is not the DOM event's handler: closing by any of
  // these is a write of `open`, and once the page shows the toast closed, onclose(false, event) is called once,
  // with the click or the key that closed it (none when the time ran out). A binding that refuses the write (a
  // function binding whose setter keeps the value) leaves the toast open, and onclose is not called; a change of
  // `open` from outside calls nothing. As on the Web Component, the root dispatches `close`, an event that
  // bubbles, once after each change from open to closed, whoever made it. The toast never removes itself.
  //
  // The entry (J95): when it opens, or mounts open, the root's own inline style gets the private custom property
  // --_entering, 1, for two frames; the recipe reads it, only when motion is allowed, as the starting opacity of
  // a transition. That is the one style it writes.
  //
  // Inside a Svelte toaster it asks the toaster, through the family's context, to look again in the same flush
  // as each change of its open state and when it goes; the toaster decides from the DOM.
  import { flushSync, getContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { dismiss } from '../../behaviours/dismiss.js';
  import { props as spec } from '../../components/toast/toast.props.js';
  import { TOASTER, type ToasterContext } from '../toaster/toaster.context.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'onclose'> & {
    /** Whether the toast is showing: `bind:open` controls it, a plain `open` only starts it. */
    open?: boolean;
    variant?: 'neutral' | 'info' | 'success' | 'warning' | 'critical';
    /** Milliseconds it stays open; with 0 it stays until it is closed. */
    duration?: number;
    /** Called once the page shows the toast closed by itself, with the click or the key that closed it. */
    onclose?: (open: boolean, event?: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { open = $bindable(false), variant, duration, onclose, role, ref = $bindable(null), children, ...rest }: Props = $props();
  const toaster = getContext<ToasterContext | undefined>(TOASTER);

  const CLOSE = '[data-part="close"]';
  const ROOT = '[data-ui="toast"]';

  /** An enum prop's value, or its default when the value is not one of the manifest's. */
  const pick = (prop: string, given: unknown): string => {
    const p = spec[prop] as { values: readonly string[], default: string };
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };
  /** The duration in milliseconds, or the manifest's default when it is not a number. */
  const time = (given: unknown): number => {
    const n = Number(given ?? NaN);
    return Number.isFinite(n) ? n : (spec.duration as { default: number }).default;
  };

  const kind = $derived(pick('variant', variant));

  /** The pointer is over the toast; focus is inside it; the open state last seen; the running time; the entry's frame. */
  let hovered = false, focused = false, wasOpen = false;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let frame: number | undefined;

  /** Closes the toast, and once the page shows it closed, says so. */
  const close = (event?: Event) => {
    if (!open) return;
    open = false;
    // In the same task: onclose and a listener further up find the toast closed.
    flushSync();
    // A binding that refused the write has not closed.
    if (!open) onclose?.(false, event);
  };

  /** Stops the time. */
  const pause = () => { clearTimeout(timer); timer = undefined; };
  /** Starts the time from the full duration, unless it is closed, paused or has no duration. */
  const start = () => {
    pause();
    const ms = time(duration);
    if (!open || ms <= 0 || hovered || focused) return;
    timer = setTimeout(() => close(), ms);
  };

  /** Removes --_entering, and the style attribute when nothing else is left in it. */
  const entered = (el: HTMLElement) => {
    el.style.removeProperty('--_entering');
    if (el.getAttribute('style') === '') el.removeAttribute('style');
  };
  /** Hands --_entering to the recipe for two frames: the first paints the start, the second starts the transition. */
  const enter = (el: HTMLElement) => {
    if (frame !== undefined) cancelAnimationFrame(frame);
    el.style.setProperty('--_entering', '1');
    frame = requestAnimationFrame(() => {
      frame = requestAnimationFrame(() => { frame = undefined; entered(el); });
    });
  };

  // The listeners, mounted once. `ref` is read untracked: a parent's function binding re-reads it whenever the
  // parent's own state changes, and a rerun would forget the pointer and the focus it had seen.
  $effect(() => untrack(() => {
    const el = ref;
    if (!el) return;
    const off = new AbortController();
    const listen = { signal: off.signal };
    el.addEventListener('pointerenter', () => { hovered = true; pause(); }, listen);
    el.addEventListener('pointerleave', () => { hovered = false; start(); }, listen);
    el.addEventListener('focusin', () => { focused = true; pause(); }, listen);
    // Focus that moves inside the toast leaves one element and enters another: focusin stops the time again.
    el.addEventListener('focusout', () => { focused = false; start(); }, listen);
    // A press on the close part of this toast, by the pointer or by a key that clicks it.
    el.addEventListener('click', (event) => {
      const part = event.target instanceof Element ? event.target.closest(CLOSE) : null;
      if (part && part.closest(ROOT) === el) close(event);
    }, listen);
    return () => {
      off.abort();
      pause();
      if (frame !== undefined) { cancelAnimationFrame(frame); frame = undefined; entered(el); }
      hovered = focused = false;
      wasOpen = false;
      // Gone from the page: the toaster that held it looks again.
      toaster?.look();
    };
  }));
  // Escape while focus is inside. A press outside and focus that leaves close nothing.
  $effect(() => untrack(() => dismiss(ref!, {
    active: () => open,
    onDismiss: (reason, event) => { if (reason === 'escape') close(event); },
  })));

  // Each change of the open state, the first included, once the page shows it: an opening enters and starts the
  // time, a closing stops it and dispatches close.
  $effect(() => {
    const now = open;
    untrack(() => {
      const el = ref;
      if (!el || now === wasOpen) return;
      wasOpen = now;
      toaster?.look();
      if (now) { enter(el); start(); return; }
      pause();
      el.dispatchEvent(new Event('close', { bubbles: true }));
    });
  });

  // The root has no `open` of its own: it is an author attribute, present and empty, or absent.
  const state = $derived({ open: open ? '' : undefined });

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
  role={role ?? (kind === 'critical' ? 'alert' : 'status')}
  data-ui="toast"
  data-variant={kind}
  {...state}
>{@render children?.()}</div>
