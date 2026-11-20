<script lang="ts">
  // tooltip.svelte: a short description shown beside the element it describes, for Svelte (docs/specs/targets.md,
  // V1 to V7; J36 to J38 of docs/specs/patterns.md).
  //
  // The root is a <span>, the inline box the content is placed against, as the Web Component's root is. It holds
  // two things the author wrote, found in the DOM and never cloned: the content, its child marked
  // data-part="content", and the subject, its first other child element. In an effect after mount, after each
  // change of `open` and on each change in its subtree, it writes the tooltip role, an id and popover="manual" on
  // the content where the author wrote none, and aria-describedby on the subject unless the author wrote one; it
  // remembers the values it wrote, so that it updates its own and never the author's (J36).
  //
  // Its open state is the author attribute `open` on the root, which the recipe displays the content from; the
  // content is in the top layer exactly while it is open, in the same flush as the change (J37, X2), and never in
  // the server markup. `open` is $bindable: `bind:open` holds it, a plain `open` only starts it. ontoggle(open,
  // event) is called once each time the tooltip opens or closes itself, with the state already in the page; a
  // binding that refuses the write (a function binding whose setter keeps the value) leaves the page as it was,
  // and ontoggle is not called. A change of `open` from outside calls nothing.
  //
  // When it opens and closes, as on the Web Component (J37):
  // - The pointer resting on the root for timing.delay milliseconds opens it; leaving the root closes it after
  //   timing.closeDelay milliseconds, which a return to the root or the content cancels. A touch pointer opens
  //   nothing.
  // - Focus on the subject that matches :focus-visible opens it at once; focus that leaves the subject closes it.
  // - Escape, through the dismiss behaviour, closes it and goes no further. A press on the subject closes it.
  import { flushSync, type Snippet, untrack } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { dismiss } from '../../behaviours/dismiss.js';

  type Props = Omit<HTMLAttributes<HTMLSpanElement>, 'children' | 'ontoggle'> & {
    /** Whether the description is showing: `bind:open` controls it, a plain `open` only starts it. */
    open?: boolean;
    /** Called once the page shows a change the tooltip made, with the new state and the event that made it. */
    ontoggle?: (open: boolean, event?: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLSpanElement | null;
    children?: Snippet;
  };

  let { open = $bindable(false), ontoggle, ref = $bindable(null), children, ...rest }: Props = $props();
  const uid = $props.id();

  /** Whether a child of the root is marked as the content. */
  const isContent = (el: Element) => el.getAttribute('data-part') === 'content';
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };
  /** The aria-describedby values this element wrote. */
  const described = new WeakMap<Element, string>();
  /** The subject that last got this element's aria-describedby. */
  let subject: Element | null = null;
  let timers: { opening?: ReturnType<typeof setTimeout>, closing?: ReturnType<typeof setTimeout> } = {};

  const content = () => (ref?.querySelector(':scope > [data-part="content"]') ?? null) as HTMLElement | null;
  const describes = () => ([...(ref?.children ?? [])].find((el) => !isContent(el)) ?? null) as HTMLElement | null;

  /** Cancels a pending open and a pending close. */
  const stop = () => {
    clearTimeout(timers.opening);
    clearTimeout(timers.closing);
    timers = {};
  };

  /** Opens or closes the tooltip, and once the page shows it, says so. */
  const set = (next: boolean, event?: Event) => {
    stop();
    if (next === open) return;
    open = next;
    // In the same task: a listener further up sees the content shown or hidden.
    flushSync();
    // A binding that refused the write has not toggled.
    if (open !== next) return;
    ontoggle?.(next, event);
  };

  /** Shows or hides the content so that it is showing exactly while the tooltip is open. */
  const apply = () => {
    const el = content();
    const want = open;
    if (!ref?.isConnected || !el || !el.hasAttribute('popover') || want === el.matches(':popover-open')) return;
    if (want) el.showPopover();
    else el.hidePopover();
  };

  /** Writes the role, the id and the popover on the content, and aria-describedby on the subject. */
  const sync = () => {
    const el = content(), now = describes();
    if (el) {
      if (!el.hasAttribute('role')) el.setAttribute('role', 'tooltip');
      if (!el.id) el.id = `tooltip-${uid}`;
      if (!el.hasAttribute('popover')) el.setAttribute('popover', 'manual');
    }
    // A subject this element described, that is no longer the subject or has nothing to name, loses the value
    // this element wrote; a value the author wrote since stays.
    const before = subject;
    if (before && (before !== now || !el)) {
      if (before.getAttribute('aria-describedby') === described.get(before)) before.removeAttribute('aria-describedby');
      described.delete(before);
      subject = null;
    }
    if (now && el) {
      const value = now.getAttribute('aria-describedby');
      if (value === null || value === described.get(now)) {
        put(now, 'aria-describedby', el.id);
        described.set(now, el.id);
        subject = now;
      }
    }
    apply();
  };

  // The root has no `open` of its own: it is an author attribute, present and empty, or absent.
  const state = $derived({ open: open ? '' : undefined });

  // The parts and the top layer follow `open`; the observer catches a content or a subject that comes, goes or changes.
  $effect(() => {
    void open;
    sync();
  });
  $effect(() => {
    const el = ref!;
    const off = new AbortController();
    const listen = { signal: off.signal };
    const onSubject = (node: EventTarget | null) => node instanceof Node && !!describes()?.contains(node);
    // The pointer. Entering the root, the content included, cancels a pending close and starts the delay.
    el.addEventListener('pointerenter', (event) => {
      if (event.pointerType === 'touch') return;
      clearTimeout(timers.closing);
      timers.closing = undefined;
      if (open || timers.opening !== undefined) return;
      timers.opening = setTimeout(() => set(true), timing.delay);
    }, listen);
    el.addEventListener('pointerleave', (event) => {
      if (event.pointerType === 'touch') return;
      clearTimeout(timers.opening);
      timers.opening = undefined;
      if (!open || timers.closing !== undefined) return;
      timers.closing = setTimeout(() => set(false), timing.closeDelay);
    }, listen);
    // The keyboard: focus that the browser would show opens at once, and focus that leaves the subject closes.
    el.addEventListener('focusin', (event) => {
      if (onSubject(event.target) && (event.target as Element).matches(':focus-visible')) set(true, event);
    }, listen);
    el.addEventListener('focusout', (event) => {
      if (onSubject(event.target) && !onSubject(event.relatedTarget)) set(false, event);
    }, listen);
    // A press on the subject, by the pointer or by a key that clicks it, is the user acting: it closes.
    el.addEventListener('pointerdown', (event) => { if (onSubject(event.target)) set(false, event); }, listen);
    el.addEventListener('click', (event) => { if (onSubject(event.target)) set(false, event); }, listen);
    // Something else hid the popover: the state follows. The toggle event does not bubble, so it is caught on its way down.
    el.addEventListener('toggle', (event) => {
      const c = content();
      if (event.target === c && open && !c?.matches(':popover-open')) set(false, event);
    }, { ...listen, capture: true });
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'id'] });
    return () => { off.abort(); observer.disconnect(); stop(); };
  });
  // Mounted untracked: dismiss may read `active` while it mounts, and would then be mounted again at every change.
  $effect(() => untrack(() => dismiss(ref!, {
    active: () => open,
    onDismiss: (reason, event) => { if (reason === 'escape') set(false, event); },
  })));

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<script lang="ts" module>
  /**
   * The milliseconds before the tooltip opens and before it closes, read at each use, as the Web Component's
   * static fields are: `import { timing } from '.../tooltip.svelte'` and write them.
   */
  export const timing = { delay: 500, closeDelay: 100 };
</script>

<span
  {...rest}
  bind:this={ref}
  data-ui="tooltip"
  {...state}
>{@render children?.()}</span>
