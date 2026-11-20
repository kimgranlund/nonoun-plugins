<script lang="ts">
  // submenu.svelte: the element that holds a menu item and the menu it opens, for Svelte (docs/specs/targets.md,
  // V1 to V7).
  //
  // The root is a <div> with no role, a row of the menu around it and the box its menu is placed against (J25):
  // a block among the menu's rows, which a <span> could not hold. It is the menu button one level down, with a
  // menu item as its trigger: it holds whether its menu is open and gives it to the menu through the menu
  // button's context, and it sets the menu group's context to null, so a radio item of its menu belongs to no
  // group around it. The trigger is the child with the menuitem role and the menu the element with the menu role
  // whose nearest submenu is this one; it writes the pattern's ARIA on the trigger and names the menu after it,
  // in the DOM, once mounted, after each change of its state and whenever its subtree changes (G10's way, one
  // level down).
  //
  // A click on the trigger, and so Enter and Space, and the arrow pointing at the inline end, through onkeydown,
  // open the menu, which moves focus to its first item and returns it to the trigger. The arrow pointing at the
  // inline start, pressed in the menu, returns focus to the trigger, and the menu closes as focus leaves it;
  // Escape does the same through the menu's dismiss. An arrow it acts on has its default prevented, which tells
  // a menubar around that the key is taken. A menu around it that closes closes this one too (J24). As the React
  // submenu.
  import { flushSync, setContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes, KeyboardEventHandler } from 'svelte/elements';
  import { KEY, type MenuButtonState } from '../menu-button/menu-button.context.js';
  import { GROUP } from '../menu-group/menu-group.context.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { ref = $bindable(null), onkeydown, children, ...rest }: Props = $props();
  const uid = $props.id();
  let open = $state(false);

  const MENU = '[role="menu"]';
  const ROOT = '[data-ui="submenu"]';

  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };
  /** The menu names this element wrote, so that it never replaces an author's. */
  const named = new WeakMap<Element, string>();

  /** The trigger and the menu, or null while either is missing. */
  const pair = () => {
    const el = untrack(() => ref);
    if (!el) return null;
    const trigger = [...el.children].find((c) => c.getAttribute('role') === 'menuitem') as HTMLElement | undefined;
    const menu = [...el.querySelectorAll(MENU)].find((m) => m.closest(ROOT) === el) as HTMLElement | undefined;
    return trigger && menu ? { menu, trigger } : null;
  };

  const sync = () => {
    const p = pair();
    if (!p) return;
    const { menu, trigger } = p;
    if (!trigger.id) trigger.id = `${uid}-trigger`;
    put(trigger, 'aria-haspopup', 'menu');
    put(trigger, 'aria-controls', menu.id);
    put(trigger, 'aria-expanded', String(open));
    // A menu the author named keeps its name (A2). One this element named follows its trigger.
    const name = menu.getAttribute('aria-labelledby');
    if (menu.hasAttribute('aria-label') || (name !== null && name !== named.get(menu))) return;
    put(menu, 'aria-labelledby', trigger.id);
    named.set(menu, trigger.id);
  };

  /**
   * Opens the menu, which moves focus to its first item. A menu that is open already closes first, with focus
   * on the trigger, and opens again, so that focus goes back into it.
   */
  const show = (p: { menu: HTMLElement, trigger: HTMLElement }) => {
    if (open) {
      open = false;
      flushSync();
      p.trigger.focus();
    }
    open = true;
    flushSync();
  };
  /** The pair, when the event happened on a trigger that is not disabled. */
  const fromTrigger = (event: Event) => {
    const p = pair();
    return p && event.target instanceof Node && p.trigger.contains(event.target) && !disabled(p.trigger) ? p : null;
  };

  setContext<MenuButtonState>(KEY, {
    get open() { return open; },
    setOpen: (next) => { open = next; },
    trigger: () => pair()?.trigger ?? null,
  });
  setContext(GROUP, null);

  // The ARIA follows `open`; the observer catches a trigger or a menu that comes, goes or changes its id.
  $effect(() => {
    void open;
    untrack(sync);
  });
  $effect(() => untrack(() => {
    const el = ref!;
    const off = new AbortController();
    const listen = { signal: off.signal };
    // A click, and so Enter and Space on the item, opens the menu (J24).
    el.addEventListener('click', (event) => { const p = fromTrigger(event); if (p) show(p); }, listen);
    // While the menu is open, the pointer passing over the trigger leaves focus in the menu: the menu around
    // would otherwise move focus to the trigger, and this menu would close as focus left it.
    el.addEventListener('pointermove', (event) => { if (open && fromTrigger(event)) event.stopPropagation(); }, listen);
    // A menu around this one that closes, by a script or otherwise, closes this one too. toggle does not
    // bubble, so it is caught on its way down.
    el.ownerDocument.addEventListener('toggle', (event) => {
      const p = pair();
      const closed = (event as ToggleEvent).newState === 'closed';
      if (closed && p && open && event.target instanceof Node && event.target !== p.menu && event.target.contains(el)) { open = false; flushSync(); }
    }, { ...listen, capture: true });
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'id'] });
    return () => { off.abort(); observer.disconnect(); };
  }));

  const keys: KeyboardEventHandler<HTMLDivElement> = (event) => {
    onkeydown?.(event);
    // Svelte keeps a delegated handler on the element after unmount, and hears the event on the document too.
    const el = ref;
    if (!el || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const rtl = getComputedStyle(el).direction === 'rtl';
    const end = rtl ? 'ArrowLeft' : 'ArrowRight';
    if (event.key === end) {
      const p = fromTrigger(event);
      if (!p) return;
      event.preventDefault();
      show(p);
      return;
    }
    if (event.key !== (rtl ? 'ArrowRight' : 'ArrowLeft')) return;
    const p = pair();
    // Only a key pressed on an item of this menu, not of a menu nested deeper, which has its own submenu.
    if (!p || !open || !(event.target instanceof Element) || event.target.closest(MENU) !== p.menu) return;
    event.preventDefault();
    // Focus leaving the menu closes it, through its dismiss (G14), as on the Web Component's close.
    p.trigger.focus();
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
  data-ui="submenu"
  onkeydown={keys}
>{@render children?.()}</div>
