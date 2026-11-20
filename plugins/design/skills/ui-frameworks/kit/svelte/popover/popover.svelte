<script lang="ts">
  // popover.svelte: a non-modal dialog beside the control that opens it, for Svelte (docs/specs/targets.md, V1 to
  // V7; J88 to J91 of docs/specs/patterns.md).
  //
  // The root is a <span>, the inline box the content is placed against, as the Web Component's root is. It holds
  // two things the author wrote, found in the DOM and never cloned: the content, its child marked
  // data-part="content", and the control, its first other child element. In an effect after mount, after each
  // change of `open` and on each change in its subtree, it writes on the content the dialog role, an id,
  // popover="manual" and tabindex="-1" where the author wrote none, and on the control aria-haspopup="dialog",
  // aria-controls and aria-expanded; a former control loses the three (J88).
  //
  // Its open state is the author attribute `open` on the root, which the recipe displays the content from; the
  // content is in the top layer exactly while it is open, in the same flush as the change (X2), and never in the
  // server markup. `open` is $bindable: `bind:open` holds it, a plain `open` only starts it. As on the Web
  // Component, the root dispatches `toggle`, a ToggleEvent that does not bubble, after each change of what is
  // shown, whoever made it. The prop `ontoggle` is not that event's handler: it is called, as ontoggle(open,
  // event), once each time the popover opens or closes itself, with the state already in the page; a binding that
  // refuses the write (a function binding whose setter keeps the value) leaves the page as it was, and it is not
  // called. A change of `open` from outside calls nothing.
  //
  // Each opening after mount moves focus to the content's first focusable element, or to the content (J89); a
  // popover rendered open shows and takes no focus. A click on the control opens it, or closes it and returns
  // focus to the control: Enter and Space do so through the control's own click. Escape, through the dismiss
  // behaviour, closes it, returns focus to the control and goes no further; a press outside and focus that leaves
  // close it and leave focus where it went.
  import { flushSync, type Snippet, untrack } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { dismiss } from '../../behaviours/dismiss.js';

  type Props = Omit<HTMLAttributes<HTMLSpanElement>, 'children' | 'ontoggle'> & {
    /** Whether the panel is showing: `bind:open` controls it, a plain `open` only starts it. */
    open?: boolean;
    /** Called once the page shows a change the popover made, with the new state and the event that made it. */
    ontoggle?: (open: boolean, event?: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLSpanElement | null;
    children?: Snippet;
  };

  let { open = $bindable(false), ontoggle, ref = $bindable(null), children, ...rest }: Props = $props();
  const uid = $props.id();

  /** What can take focus inside the content, in document order. */
  const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  /** The ARIA this element writes on its control. */
  const ARIA = ['aria-haspopup', 'aria-expanded', 'aria-controls'];
  /** Whether a child of the root is marked as the content. */
  const isContent = (el: Element) => el.getAttribute('data-part') === 'content';
  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };
  const toggleState = (to: boolean) => (to ? 'open' : 'closed');

  /** The element that last got this element's ARIA. */
  let owned: HTMLElement | null = null;
  /** Whether the last toggle dispatched said open. */
  let reported = false;
  /** Whether the first sync has run: before it, an opening moves no focus. */
  let live = false;

  const content = () => (ref?.querySelector(':scope > [data-part="content"]') ?? null) as HTMLElement | null;
  const control = () => ([...(ref?.children ?? [])].find((el) => !isContent(el)) ?? null) as HTMLElement | null;

  /** Opens or closes the popover, and once the page shows it, says so. */
  const set = (next: boolean, event?: Event) => {
    if (next === open) return;
    open = next;
    // In the same task: a listener further up sees the content shown or hidden.
    flushSync();
    // A binding that refused the write has not toggled.
    if (open !== next) return;
    ontoggle?.(next, event);
  };
  /** Closes the popover, and with `restore` returns focus to the control. */
  const close = (restore: boolean, event: Event) => {
    set(false, event);
    if (restore) control()?.focus();
  };

  /**
   * Shows or hides the content so that it is showing exactly while the popover is open, moves focus in when it
   * opens after mount, and dispatches `toggle` when the state differs from the last one dispatched.
   */
  const apply = () => {
    const el = content();
    const want = open;
    if (!ref?.isConnected || !el || !el.hasAttribute('popover')) return;
    if (want !== el.matches(':popover-open')) {
      if (want) {
        el.showPopover();
        // The root's open attribute is already written, so the content is displayed and can take focus.
        if (live) ((el.querySelector(FOCUSABLE) ?? el) as HTMLElement).focus();
      } else el.hidePopover();
    }
    if (want === reported) return;
    reported = want;
    ref.dispatchEvent(new ToggleEvent('toggle', { oldState: toggleState(!want), newState: toggleState(want) }));
  };

  /** Writes the role, the id, the popover and the tabindex on the content, and the ARIA on the control. */
  const sync = () => {
    const el = content(), now = control();
    if (el) {
      if (!el.hasAttribute('role')) el.setAttribute('role', 'dialog');
      if (!el.id) el.id = `popover-${uid}`;
      if (!el.hasAttribute('popover')) el.setAttribute('popover', 'manual');
      if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1');
    }
    const before = owned;
    if (before && (before !== now || !el)) {
      for (const name of ARIA) before.removeAttribute(name);
      owned = null;
    }
    if (now && el) {
      put(now, 'aria-haspopup', 'dialog');
      put(now, 'aria-controls', el.id);
      owned = now;
    }
    if (owned) put(owned, 'aria-expanded', String(open));
    apply();
  };

  // The root has no `open` of its own: it is an author attribute, present and empty, or absent.
  const state = $derived({ open: open ? '' : undefined });

  // The parts and the top layer follow `open`; the observer catches a content or a control that comes, goes or changes.
  $effect(() => {
    void open;
    sync();
    live = true;
  });
  $effect(() => {
    const el = ref!;
    const off = new AbortController();
    const listen = { signal: off.signal };
    // A click on the control, from the pointer or from a key that clicks it, opens or closes (J89).
    el.addEventListener('click', (event) => {
      const c = control();
      if (!c || !(event.target instanceof Node) || !c.contains(event.target) || disabled(c)) return;
      if (open) close(true, event);
      else set(true, event);
    }, listen);
    // Something else hid the popover: the state follows. The toggle event does not bubble, so it is caught on its way down.
    el.addEventListener('toggle', (event) => {
      const c = content();
      if (event.target === c && open && !c?.matches(':popover-open')) set(false, event);
    }, { ...listen, capture: true });
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'id'] });
    return () => { off.abort(); observer.disconnect(); };
  });
  // Mounted untracked: dismiss may read `active` while it mounts, and would then be mounted again at every change.
  $effect(() => untrack(() => dismiss(ref!, {
    active: () => open,
    onDismiss: (reason, event) => close(reason === 'escape', event),
  })));

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<span
  {...rest}
  bind:this={ref}
  data-ui="popover"
  {...state}
>{@render children?.()}</span>
