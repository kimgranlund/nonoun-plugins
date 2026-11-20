<script lang="ts">
  // menu.svelte: a list of actions that opens over the page, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="menu" popover="manual">. It is showing exactly while it is open, and its open state
  // is the platform's own, :popover-open: it writes no open attribute (X2), and the server renders it closed.
  // Inside a menu button, the menu button holds whether it is open, through the family's context; on its own it
  // holds it as the $bindable `open`. When it opens it remembers the element that had focus and moves focus to
  // its first item that is not disabled; its items are the menu items, the checkable ones included. It mounts
  // roving focus, typeahead and dismiss as the Web Component does; the pointer moves focus to the item under it;
  // Escape and the activation of an item close it and return focus, a press outside and focus that leaves close
  // it and leave focus alone (G12 to G15). A checkable item activated by Space or the pointer, and an item that
  // opens a submenu, leave it open (J22, J24).
  import { flushSync, getContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { rovingFocus } from '../../behaviours/roving-focus.js';
  import { typeahead } from '../../behaviours/typeahead.js';
  import { dismiss } from '../../behaviours/dismiss.js';
  import { KEY, type MenuButtonState } from '../menu-button/menu-button.context.js';
  import { role } from '../../components/menu/menu.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'role'> & {
    /** Whether the menu is showing, when it is not in a menu button: `bind:open` controls it, a plain `open` only starts it. */
    open?: boolean;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { open = $bindable(false), ref = $bindable(null), children, ...rest }: Props = $props();
  const uid = $props.id();
  const owner = getContext<MenuButtonState | undefined>(KEY);
  const isOpen = $derived(owner ? owner.open : open);

  const MENU = '[role="menu"]';
  const ITEM = '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]';
  const CHECKABLE = '[role="menuitemcheckbox"], [role="menuitemradio"]';
  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  const itemOf = (event: Event) => (event.target instanceof Element ? event.target.closest(ITEM) : null) as HTMLElement | null;
  const items = () => ([...ref!.querySelectorAll(ITEM)] as HTMLElement[]).filter((x) => x.closest(MENU) === ref);
  /** Whether activating the item leaves its menu open, as on the Web Component: a checkable item after Space or the pointer, and an item that opens a menu. */
  const staysOpen = (item: Element) => ['true', 'menu'].includes(item.getAttribute('aria-haspopup') ?? '')
    || (item.matches(CHECKABLE) && !item.hasAttribute('data-active'));
  /** The element that had focus when the menu last opened. */
  let opener: HTMLElement | null = null;

  /** The state, in the menu button when there is one. */
  const setOpen = (next: boolean) => { if (owner) owner.setOpen(next); else open = next; };

  /** Closes the menu, and with `restore` returns focus to where it was when it opened. */
  const close = (restore: boolean) => {
    const el = ref!;
    const back = opener;
    setOpen(false);
    flushSync();
    if (el.matches(':popover-open')) el.hidePopover();
    if (restore) back?.focus();
  };

  // The listeners and the behaviours first: the items have their tabindex before the menu moves focus to one.
  // Each is mounted once: `ref` is read untracked, as a parent's function binding re-reads it whenever the
  // parent's own state changes.
  $effect(() => untrack(() => {
    const el = ref!;
    const off = new AbortController();
    const listen = { signal: off.signal };
    // Something else hid the popover: the state follows (G15).
    el.addEventListener('toggle', () => {
      if (!untrack(() => isOpen) || el.matches(':popover-open')) return;
      setOpen(false);
      flushSync();
    }, listen);
    // Read before the item's own listener runs: press marks the item data-active only while Enter is down.
    let stays = false;
    el.addEventListener('click', (event) => { const item = itemOf(event); stays = !!item && staysOpen(item); }, { ...listen, capture: true });
    el.addEventListener('click', (event) => {
      const item = itemOf(event);
      if (stays) return;
      if (item && !disabled(item)) close(true);
    }, listen);
    el.addEventListener('mousedown', (event) => event.preventDefault(), listen);
    el.addEventListener('pointermove', (event) => itemOf(event)?.focus({ preventScroll: true }), listen);
    return () => off.abort();
  }));
  $effect(() => untrack(() => rovingFocus(ref!, { items, orientation: () => 'vertical', skip: disabled })));
  $effect(() => untrack(() => typeahead(ref!, { items, skip: disabled, onMatch: (item) => { if (ref!.ownerDocument.activeElement?.closest(MENU) === ref) item.focus(); } })));
  $effect(() => untrack(() => dismiss(ref!, {
    ignore: () => [opener, owner?.trigger()],
    onDismiss: (reason) => close(reason === 'escape'),
  })));

  // Shows or hides the popover in the same flush as the change that opened or closed it.
  $effect(() => {
    const want = isOpen;
    untrack(() => {
      const el = ref!;
      if (want === el.matches(':popover-open')) return;
      if (!want) { el.hidePopover(); return; }
      opener = el.ownerDocument.activeElement as HTMLElement | null;
      el.showPopover();
      items().find((x) => !disabled(x))?.focus();
    });
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<div
  popover="manual"
  id={uid}
  {...rest}
  bind:this={ref}
  {role}
  data-ui="menu"
>{@render children?.()}</div>
