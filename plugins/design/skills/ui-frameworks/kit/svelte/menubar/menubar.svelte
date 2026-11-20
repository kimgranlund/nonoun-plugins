<script lang="ts">
  // menubar.svelte: a row of menus, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="menubar">. Its buttons are the triggers of the menu buttons the author writes inside
  // it, which belong to another family, so it finds them in the DOM as the Web Component does: the elements with
  // the button role, or native buttons, that are not inside a menu and that their menu button has marked with
  // aria-haspopup, not of a menubar nested in this one. It mounts roving focus, which writes their tabindex and
  // moves focus among them along the row, wrapping (J26).
  //
  // While one of its menus is open, ArrowRight and ArrowLeft pressed inside it, through onkeydown, move focus to
  // the next or the previous button, which closes the open menu (focus leaves it), and open that button's menu. A
  // Svelte menu has no open attribute (its open state is :popover-open), so the menubar opens it as Enter does:
  // with a click on its button. A key whose default action is already prevented, such as an arrow a submenu took,
  // is left alone. A button's menu is the element its aria-controls names. As the React menubar.
  import { untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes, KeyboardEventHandler } from 'svelte/elements';
  import { rovingFocus } from '../../behaviours/roving-focus.js';
  import { role } from '../../components/menubar/menubar.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'role'> & {
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { ref = $bindable(null), onkeydown, children, ...rest }: Props = $props();

  const BUTTON = 'button, [role="button"]';
  const MENU = '[role="menu"]';
  const ROOT = '[role="menubar"]';
  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

  /** The buttons of a menubar, in document order. */
  const buttonsOf = (el: HTMLElement) => ([...el.querySelectorAll(BUTTON)] as HTMLElement[]).filter((b) => b.closest(ROOT) === el
    && b.hasAttribute('aria-haspopup') && !b.closest(MENU));

  // Mounted once, after hydration: roving focus writes the buttons' tabindex.
  $effect(() => untrack(() => {
    const el = ref!;
    return rovingFocus(el, {
      items: () => buttonsOf(el),
      orientation: () => 'horizontal',
      skip: disabled,
      // A trigger becomes a button of the bar when its menu button marks it.
      watch: ['aria-haspopup'],
    });
  }));

  /** An arrow along the row, pressed inside an open menu, moves to the next or the previous menu (J26). */
  const keys: KeyboardEventHandler<HTMLDivElement> = (event) => {
    onkeydown?.(event);
    // Svelte keeps a delegated handler on the element after unmount, and hears the event on the document too.
    const el = ref;
    if (!el || event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    const target = event.target;
    if (!(target instanceof Element)) return;
    const buttons = buttonsOf(el).filter((b) => !disabled(b));
    const at = buttons.findIndex((b) => {
      const id = b.getAttribute('aria-controls');
      const menu = id ? el.querySelector(`#${CSS.escape(id)}`) : null;
      return !!menu && menu.contains(target);
    });
    if (at < 0) return;
    const forward = (event.key === 'ArrowRight') === (getComputedStyle(el).direction !== 'rtl');
    const next = buttons[(at + (forward ? 1 : -1) + buttons.length) % buttons.length];
    event.preventDefault();
    // Focus leaving the open menu closes it, and every menu inside it (G14).
    next.focus();
    next.click();
  };

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
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
  data-ui="menubar"
  onkeydown={keys}
>{@render children?.()}</div>
