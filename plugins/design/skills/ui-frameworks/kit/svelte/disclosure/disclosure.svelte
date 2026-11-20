<script lang="ts">
  // disclosure.svelte: the element that holds a trigger and the panel it shows and hides, for Svelte
  // (docs/specs/targets.md, V1 to V7; rules J9 and J10 of docs/specs/patterns.md).
  //
  // The root is a <div>. It has no role and paints nothing; its recipe alone shows the panel, from the root's
  // `open` attribute, so the state is right in the server markup (J10). The panel is the author's child marked
  // `data-part="panel"`; the trigger is the author's own element of another family, such as the kit's Button, so it
  // is found in the DOM as the Web Component finds it: the first element with the button role, or a native button,
  // that belongs to this disclosure and is not inside the panel, a heading included (J9). Its aria-expanded and
  // aria-controls, and an id on the panel that has none, are written in an effect, only where they differ, after
  // each change of `open` and whenever the subtree changes.
  //
  // `open` is $bindable: `bind:open` holds it, a plain `open` only starts it. A click on the trigger, and so Enter
  // and Space on the kit's button, writes it; once the page shows the change, ontoggle(open, event) is called and a
  // `toggle` event that bubbles is dispatched, as on the Web Component. A binding that refuses the write (a function
  // binding whose setter keeps the value) leaves the page as it was, and neither is called. When another party
  // writes `open` on the root, such as an accordion that keeps one disclosure open, the disclosure follows it and
  // writes it to its binding, and calls nothing.
  import { flushSync, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'ontoggle'> & {
    /** Whether the panel is showing: `bind:open` controls it, a plain `open` only starts it. */
    open?: boolean;
    /** Called once the page shows a change the user made, with the new state and the event that made it. */
    ontoggle?: (open: boolean, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { open = $bindable(false), ontoggle, ref = $bindable(null), children, ...rest }: Props = $props();
  const uid = $props.id();

  const ROOT = '[data-ui="disclosure"]';
  const BUTTON = 'button, [role="button"]';

  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };

  /** The panel and its trigger, or null while either is missing. */
  const pair = () => {
    const el = ref;
    if (!el) return null;
    const panel = [...el.children].find((child) => child.matches('[data-part="panel"]')) as HTMLElement | undefined;
    if (!panel) return null;
    const trigger = ([...el.querySelectorAll(BUTTON)] as HTMLElement[]).find((x) => x.closest(ROOT) === el && !panel.contains(x));
    return trigger ? { panel, trigger } : null;
  };
  /** Brings the trigger's ARIA and the panel's id in step, as the root's `open` stands in the page. */
  const sync = () => {
    const p = pair();
    if (!p) return;
    if (!p.panel.id) p.panel.id = `${uid}-panel`;
    put(p.trigger, 'aria-controls', p.panel.id);
    put(p.trigger, 'aria-expanded', String((ref as HTMLDivElement).hasAttribute('open')));
  };

  // The root has no `open` of its own: it is an author attribute, present and empty, or absent.
  const state = $derived({ open: open ? '' : undefined });

  // The ARIA follows `open`; the observer catches a trigger or a panel that comes, goes or changes.
  $effect(() => {
    void open;
    sync();
  });
  $effect(() => {
    const el = ref as HTMLDivElement;
    const off = new AbortController();
    // A click, and so Enter and Space on the kit's button, shows the panel or hides it (J10). It is seen in the
    // same task by a listener further up, which is why the state is flushed here.
    el.addEventListener('click', (event) => {
      const p = pair();
      if (!p || !(event.target instanceof Node) || !p.trigger.contains(event.target) || disabled(p.trigger)) return;
      const next = !open;
      open = next;
      flushSync();
      // A binding that refused the write has not toggled.
      if (el.hasAttribute('open') !== next) return;
      ontoggle?.(next, event);
      el.dispatchEvent(new Event('toggle', { bubbles: true }));
    }, { signal: off.signal });
    const observer = new MutationObserver((records) => {
      sync();
      // `open` written by someone else: an accordion, or a script.
      if (!records.some((r) => r.type === 'attributes' && r.attributeName === 'open' && r.target === el)) return;
      const now = el.hasAttribute('open');
      if (now === open) return;
      open = now;
      flushSync();
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'data-part', 'open'] });
    return () => { off.abort(); observer.disconnect(); };
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
  data-ui="disclosure"
  {...state}
>{@render children?.()}</div>
