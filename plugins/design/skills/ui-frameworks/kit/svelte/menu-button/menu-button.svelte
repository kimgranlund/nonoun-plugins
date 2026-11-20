<script lang="ts">
  // menu-button.svelte: the element that holds a trigger and its menu, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <span>, the box the menu is placed against. It holds whether the menu is open, as the
  // $bindable `open`, and gives it to its menu through the family's context (menu-button.context.js). Its
  // trigger is the author's own element of another family, such as the kit's Button, so it finds it in the DOM
  // as the Web Component does: the first element with the button role, or native button, that is not inside
  // the menu (G10). It writes the pattern's ARIA on the trigger and the menu's name, only where it differs,
  // after each change of `open` and whenever its subtree changes; a click on the trigger, and so Enter and
  // Space, opens or closes the menu, and ArrowDown and ArrowUp open it (G11).
  import { flushSync, setContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes, KeyboardEventHandler } from 'svelte/elements';
  import { KEY, type MenuButtonState } from './menu-button.context.js';

  type Props = Omit<HTMLAttributes<HTMLSpanElement>, 'children'> & {
    /** Whether the menu is showing: `bind:open` controls it, a plain `open` only starts it. */
    open?: boolean;
    /** The root, for `bind:ref`. */
    ref?: HTMLSpanElement | null;
    children?: Snippet;
  };

  let { open = $bindable(false), ref = $bindable(null), onkeydown, children, ...rest }: Props = $props();
  const uid = $props.id();

  const MENU = '[role="menu"]';
  const BUTTON = 'button, [role="button"]';
  const ITEM = '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]';
  const ROOT = '[data-ui="menu-button"]';

  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };
  /** The menu names this element wrote, so that it never replaces an author's. */
  const named = new WeakMap<Element, string>();

  /** The elements that match and belong to this menu button, not to one nested inside it. */
  const own = (selector: string): HTMLElement[] => {
    const el = untrack(() => ref);
    return el ? ([...el.querySelectorAll(selector)] as HTMLElement[]).filter((x) => x.parentElement?.closest(ROOT) === el) : [];
  };
  const pair = () => {
    const menu = own(MENU)[0];
    const trigger = menu && own(BUTTON).find((el) => !menu.contains(el));
    return trigger ? { menu, trigger } : null;
  };

  const sync = () => {
    const p = pair();
    if (!p) return;
    const { menu, trigger } = p;
    if (!trigger.id) trigger.id = `${uid}-trigger`;
    put(trigger, 'aria-haspopup', 'menu');
    if (menu.id) put(trigger, 'aria-controls', menu.id);
    put(trigger, 'aria-expanded', String(open));
    const name = menu.getAttribute('aria-labelledby');
    if (menu.hasAttribute('aria-label') || (name !== null && name !== named.get(menu))) return;
    put(menu, 'aria-labelledby', trigger.id);
    named.set(menu, trigger.id);
  };

  /** The pair when the event happened on a trigger that is not disabled. */
  const fromTrigger = (event: Event) => {
    const p = pair();
    return p && event.target instanceof Node && p.trigger.contains(event.target) && !disabled(p.trigger) ? p : null;
  };

  setContext<MenuButtonState>(KEY, {
    get open() { return open; },
    setOpen: (next) => { open = next; },
    trigger: () => pair()?.trigger ?? null,
  });

  // The ARIA follows `open`; the observer catches a trigger or a menu that comes, goes or changes its id. `ref`
  // is read untracked: a parent's function binding re-reads it whenever the parent's own state changes, and the
  // listeners and the observer are set up once.
  $effect(() => {
    void open;
    untrack(sync);
  });
  $effect(() => untrack(() => {
    const el = ref!;
    const off = new AbortController();
    el.addEventListener('click', (event) => {
      if (!fromTrigger(event)) return;
      open = !open;
      // Seen in the same task by a listener further up, even for a click that Enter dispatched (G11).
      flushSync();
    }, { signal: off.signal });
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'id'] });
    return () => { off.abort(); observer.disconnect(); };
  }));

  const keys: KeyboardEventHandler<HTMLSpanElement> = (event) => {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      const p = fromTrigger(event);
      if (p) {
        event.preventDefault();
        open = true;
        flushSync();
        if (event.key === 'ArrowUp') ([...p.menu.querySelectorAll(ITEM)] as HTMLElement[]).filter((item) => item.closest(MENU) === p.menu && !disabled(item)).pop()?.focus();
      }
    }
    onkeydown?.(event);
  };

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<span
  {...rest}
  bind:this={ref}
  data-ui="menu-button"
  onkeydown={keys}
>{@render children?.()}</span>
