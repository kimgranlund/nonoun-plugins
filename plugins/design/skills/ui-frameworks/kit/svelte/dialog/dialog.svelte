<script lang="ts">
  // dialog.svelte: a window over the page that holds focus until it is closed, for Svelte (docs/specs/targets.md,
  // V1 to V7; J39 to J42 and J122 of docs/specs/patterns.md).
  //
  // The root is a <div> that takes no room (the recipe gives it display: contents), as the Web Component's root is.
  // The modal layer is the browser's own dialog element, which the author writes inside the root and marks
  // data-part="panel" (D91): it is found in the DOM, never cloned or wrapped. In an effect after mount, while the
  // dialog is open the part is shown with showModal(), in the same flush as the change, and closed when it is not
  // (J39); the server renders it closed. When the browser closes the part (Escape, a form with method="dialog", a
  // native button's command="close") the dialog closes; when the browser opens it (a native button's
  // command="show-modal", a script's showModal()) the dialog opens (D118). A binding that refuses the write (a
  // function binding whose setter keeps the value) keeps the state: a part the browser opened is closed again at
  // once, and a part the browser closed stays closed until `open` changes.
  //
  // In the same effects and on each change in its subtree it names the part after the element marked
  // data-part="title" and describes it by the one marked data-part="description", giving each an id when it has
  // none, and with `alert` gives the part the alertdialog role; it never replaces what the author wrote (J41). It
  // adds no focus handling, no inertness and no Escape handling of its own (J40).
  //
  // Its open state is the author attribute `open` on the root (X2); the part's own `open` and :modal are the
  // platform's. `open` is $bindable: `bind:open` holds it, a plain `open` only starts it. `onclose` is not the DOM
  // event's handler: it is called as onclose(false, event), with the part's close event, once the page shows the
  // dialog closed by the browser; `onopen(true, event)`, with the part's toggle event, once it shows the dialog
  // opened by the browser. A change of `open` from outside calls neither. The part's own close event and
  // returnValue stay the author's interface, as on the Web Component. `side` is the variant data-side, which makes
  // a drawer (J122).
  import { flushSync, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { props as spec } from '../../components/dialog/dialog.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'onclose' | 'onopen'> & {
    /** Whether the dialog is showing: `bind:open` controls it, a plain `open` only starts it. */
    open?: boolean;
    /** The dialog interrupts with a message that needs an answer: the part gets the alertdialog role. */
    alert?: boolean;
    side?: 'center' | 'inline-start' | 'inline-end' | 'block-end';
    /** Called once the page shows the dialog closed by the browser, with the part's close event. */
    onclose?: (open: boolean, event: Event) => void;
    /** Called once the page shows the dialog opened by the browser, with the part's toggle event. */
    onopen?: (open: boolean, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { open = $bindable(false), alert = false, side, onclose, onopen, ref = $bindable(null), children, ...rest }: Props = $props();
  const uid = $props.id();

  /** An enum prop's value, or its default when the value is not one of the manifest's. */
  const pick = (prop: string, given: unknown): string => {
    const p = spec[prop] as { values: readonly string[], default: string };
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };

  /** The part whose events are heard, and how to stop hearing them. */
  let bound: { part: HTMLDialogElement | null, off: () => void } = { part: null, off: () => {} };
  /** What this element wrote on the part, by attribute. */
  const wrote = new Map<string, string>();
  /** The browser is opening the part and has not yet said so with `toggle`: the part is not closed meanwhile. */
  let opening = false;
  /** This element is the one showing the part. */
  let mine = false;

  /** The dialog part, or null while it is missing or not a dialog element. */
  const part = () => {
    const el = ref?.querySelector(':scope > [data-part="panel"]');
    return el instanceof HTMLDialogElement && el.isConnected ? el : null;
  };

  /** Sets or removes an attribute this element wrote, only when it differs; never one the author wrote. */
  const write = (el: Element, name: string, value: string | null) => {
    const own = wrote.get(name);
    if (el.hasAttribute(name) && el.getAttribute(name) !== own) return; // the author's
    if (value === null) { el.removeAttribute(name); wrote.delete(name); return; }
    if (el.getAttribute(name) !== value) el.setAttribute(name, value);
    wrote.set(name, value);
  };

  /** Listens for the close and the opening of the part, and again when the part is replaced. */
  const bind = () => {
    const el = part();
    if (el === bound.part) return;
    bound.off();
    wrote.clear();
    if (!el) { bound = { part: null, off: () => {} }; return; }
    const off = new AbortController();
    const listen = { signal: off.signal };
    el.addEventListener('close', (event) => {
      if (el.open || !open) return;
      open = false;
      // In the same task: the author's own listener on the part finds the dialog closed.
      flushSync();
      // A binding that refused the write has not closed.
      if (!open) onclose?.(false, event);
    }, listen);
    el.addEventListener('beforetoggle', (event) => {
      opening = (event as ToggleEvent).newState === 'open' && !mine;
    }, listen);
    // The browser opened the part itself: an invoker command, or a script. The state follows, as it follows a close.
    el.addEventListener('toggle', (event) => {
      opening = false;
      if ((event as ToggleEvent).newState !== 'open' || open) return;
      open = true;
      flushSync();
      if (open) onopen?.(true, event);
      else if (el.open) el.close();
    }, listen);
    bound = { part: el, off: () => off.abort() };
  };

  /** Names and describes the part, and gives it the alertdialog role. */
  const name = () => {
    const el = part();
    if (!el) return;
    const idOf = (x: Element | null, what: string) => {
      if (!x) return null;
      if (!x.id) x.id = `dialog-${what}-${uid.replace(/[^\w-]/g, '')}`;
      return x.id;
    };
    write(el, 'aria-labelledby', idOf(el.querySelector('[data-part="title"]'), 'title'));
    write(el, 'aria-describedby', idOf(el.querySelector('[data-part="description"]'), 'description'));
    write(el, 'role', alert ? 'alertdialog' : null);
  };

  /** Brings the part in step with the open state. */
  const apply = () => {
    const el = part();
    if (!el || !ref?.isConnected) return;
    if (open && !el.matches(':modal')) {
      // A part that is open but not modal is shown again as a modal.
      if (el.open) el.close();
      mine = true;
      el.showModal();
      mine = false;
    } else if (!open && el.open && !opening) el.close();
  };

  const refresh = () => { bind(); name(); apply(); };

  // Mounted once. `ref` is read untracked: a parent's function binding re-reads it whenever the parent's own state
  // changes, and a rerun would forget what this element wrote. The observer catches a part, a title or a
  // description that comes, goes or is replaced, in the author's markup, which re-renders without this component.
  $effect(() => untrack(() => {
    const el = ref;
    if (!el) return;
    const observer = new MutationObserver(refresh);
    observer.observe(el, { childList: true, subtree: true });
    refresh();
    return () => { observer.disconnect(); bound.off(); bound = { part: null, off: () => {} }; };
  }));
  // The props can change at any time: the part follows in the flush that changed them.
  $effect(() => {
    void open;
    void alert;
    untrack(refresh);
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
  data-ui="dialog"
  data-side={pick('side', side)}
  {...state}
>{@render children?.()}</div>
