<script lang="ts">
  // tag-group.svelte: the tag group for Svelte (docs/specs/targets.md, V1 to V7; J115 to J117 of
  // docs/specs/patterns.md).
  //
  // The root is a <div role="group">. Its focus stops are the remove controls of its tags: the author's elements
  // marked data-part="remove" inside a direct child. It mounts roving focus as the Web Component does, in an effect,
  // since the behaviour writes the controls' tabindex when it mounts: one of them is the Tab stop and the arrow keys,
  // Home and End move among them without wrapping (J115).
  //
  // The group never removes a tag. A press on a remove control, and Delete or Backspace on one, dispatch `remove` on
  // the group, bubbling, with the tag in `detail.tag`, and call `onremove(tag, event)` with the same event: one
  // dispatch, so the page may listen with either (J116). When the tag that held focus leaves the group the group
  // moves focus to the control of the tag that followed it, else the one before, else the group, which takes
  // tabindex="-1" only for that moment. The page removes the tag by rendering without it; the group sees the node
  // leave, so it does not matter how the page removes it. As the React tag group.
  //
  // A disabled group takes no focus and dispatches nothing: it renders aria-disabled="true" and inert (J117). The
  // `disabled` prop is not rendered as an attribute: aria-disabled is what the group's role allows (X2). The click
  // is heard by a native listener added in an effect, so the author's onclick on the root still runs; Delete and
  // Backspace go through onkeydown on the root, after the author's own.
  import { untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { rovingFocus } from '../../behaviours/roving-focus.js';
  import { role } from '../../components/tag-group/tag-group.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'role'> & {
    disabled?: boolean;
    /** Called when the user asks to remove a tag, with the tag and the `remove` event dispatched on the group. */
    onremove?: (tag: HTMLElement, event: CustomEvent<{ tag: HTMLElement }>) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { disabled = false, onremove, onkeydown, inert, ref = $bindable(null), children, ...rest }: Props = $props();

  const REMOVE = '[data-part="remove"]';
  const off = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

  /** The tag, a direct child of the group, that holds `el`. */
  const tagOf = (group: HTMLElement, el: Element | null): HTMLElement | null => {
    let at = el;
    while (at && at.parentElement !== group) at = at.parentElement;
    return at as HTMLElement | null;
  };
  /** The remove controls of the group, in document order: those inside a direct child. */
  const controls = (group: HTMLElement): HTMLElement[] => [...group.children].flatMap((tag) => [...tag.querySelectorAll<HTMLElement>(REMOVE)]);
  /** Asks the page to remove the tag of a control. */
  const ask = (group: HTMLElement, control: Element) => {
    if (disabled || off(control)) return;
    const tag = tagOf(group, control);
    if (!tag) return;
    const event = new CustomEvent('remove', { detail: { tag }, bubbles: true, cancelable: true });
    group.dispatchEvent(event);
    onremove?.(tag, event);
  };

  // Roving focus, mounted once after hydration: it writes the controls' tabindex when it mounts. `ref` is read
  // untracked, so a parent's function binding that re-reads it does not mount the behaviour again.
  $effect(() => {
    const el = untrack(() => ref);
    if (!el) return;
    return rovingFocus(el, {
      items: () => controls(el),
      skip: (item: Element) => disabled || off(item),
      wrap: false,
    });
  });

  /** Hears the presses, follows the focus and moves it when the tag that held it leaves. */
  const setup = (el: HTMLDivElement) => {
    /** The tag, a direct child, that holds the focus; null while focus is elsewhere. */
    let held: Element | null = null;
    /** The element in it that holds the focus. */
    let focused: HTMLElement | null = null;
    let tabindex = false;
    /** The first remove control of the tags from `from` on, in `step` direction, that is still in the group. */
    const walk = (from: Node | null, step: 'nextSibling' | 'previousSibling'): HTMLElement | null => {
      for (let at = from; at; at = at[step]) {
        if (at.parentNode !== el) return null;
        const control = (at as Element).querySelector?.(REMOVE);
        if (control && !off(control)) return control as HTMLElement;
      }
      return null;
    };
    const focusSelf = () => {
      if (!el.hasAttribute('tabindex')) { el.setAttribute('tabindex', '-1'); tabindex = true; }
      el.focus();
    };

    const abort = new AbortController();
    const listen = { signal: abort.signal };
    el.addEventListener('click', (event) => {
      const control = event.target instanceof Element ? event.target.closest(REMOVE) : null;
      if (control && controls(el).includes(control as HTMLElement)) ask(el, control);
    }, listen);
    el.addEventListener('focusin', (event) => { held = tagOf(el, event.target as Element); focused = event.target as HTMLElement; }, listen);
    el.addEventListener('focusout', (event) => {
      if (tabindex && event.target === el) { el.removeAttribute('tabindex'); tabindex = false; }
      const to = event.relatedTarget;
      if (to instanceof Node) { held = null; return; }
      // Focus that leaves with nowhere to go is either a click on nothing or the removal of the focused tag, and
      // an engine may report the second before the tag has left. The observer settles that in a microtask; a tag
      // still in the group after a task, with focus outside, was a plain blur.
      setTimeout(() => { if (held?.parentNode === el && !el.contains(document.activeElement)) held = null; });
    }, listen);

    const observer = new MutationObserver((records) => {
      const was = held;
      if (!was) return;
      if (was.parentNode === el) {
        // A keyed {#each} moves a tag by taking it out and putting it back, and the browser drops the focus on the
        // way: a tag the page moved within the group gets it back.
        const moved = records.some((r) => [...r.removedNodes].includes(was));
        if (moved && focused && was.contains(focused) && !el.contains(document.activeElement)) focused.focus();
        return;
      }
      const record = records.find((r) => [...r.removedNodes].includes(was));
      held = null;
      const next = walk(record?.nextSibling ?? null, 'nextSibling')
        ?? walk(record?.previousSibling ?? null, 'previousSibling')
        ?? controls(el).find((control) => !off(control));
      if (next) next.focus();
      else focusSelf();
    });
    observer.observe(el, { childList: true });
    return () => { abort.abort(); observer.disconnect(); };
  };

  // Mounted once, as roving focus is.
  $effect(() => untrack(() => (ref ? setup(ref) : undefined)));

  const keydown = (event: KeyboardEvent & { currentTarget: EventTarget & HTMLDivElement }) => {
    onkeydown?.(event);
    if (event.key !== 'Delete' && event.key !== 'Backspace') return;
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const group = event.currentTarget;
    const at = controls(group).find((control) => control === event.target);
    if (!at) return;
    event.preventDefault();
    ask(group, at);
  };

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
  {role}
  data-ui="tag-group"
  aria-disabled={disabled ? 'true' : undefined}
  inert={disabled || inert ? true : undefined}
  onkeydown={keydown}
>{@render children?.()}</div>
