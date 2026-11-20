<script lang="ts">
  // combobox.svelte: a text field with a list of suggestions that narrows as the user types, for Svelte
  // (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div>, with no role: it is the field, around the author's input (the child marked
  // data-part="input") and the author's popup (the child marked data-part="popup"), which holds the kit's listbox.
  // Focus stays in the input, which carries the combobox role and the form value under its own name (J43). The list
  // follows the APG's list autocomplete with manual selection: typing filters the options and opens the list, the
  // arrows move a highlight, and only Enter or a click takes an option (J44). While the input carries readonly the
  // list stays closed and the value is left alone (J80). As the React combobox.
  //
  // The input and the popup are the author's, in the `children` snippet, and the listbox and the options are of
  // another family, so the combobox finds them in the DOM, by data-part and by role, and writes what its manifest
  // says it writes, only where it differs, after each change of `open` and whenever its subtree changes: on the
  // input its role and ARIA, on the popup popover="manual" when it has none, on the listbox an id and tabindex="-1",
  // and on the options hidden, selected and data-focus; activeDescendant writes data-highlighted, the options' ids
  // and the input's aria-activedescendant. None of these is rendered by the listbox or the option, so Svelte never
  // writes them back. The listbox's own logic still runs: a click on an option highlights and selects it there
  // first. The root's aria-disabled is written from the input in the DOM: the combobox cannot read its children, so
  // the server markup carries it only when the author writes it on the root too.
  //
  // `open` is the author attribute on the root (X2), which the recipe shows the popup on, and is $bindable:
  // `bind:open` follows the user, a plain `open` only starts it. The popup is shown in the top layer in the same
  // flush. onchange(value, event) is called once the user takes an option, after the input, the options and the
  // list are written. The input's own events are the author's.
  import { flushSync, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes, KeyboardEventHandler } from 'svelte/elements';
  import { activeDescendant } from '../../behaviours/active-descendant.js';
  import { dismiss } from '../../behaviours/dismiss.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'onchange'> & {
    /** Whether the list is showing: `bind:open` follows the user, a plain `open` only starts it. */
    open?: boolean;
    /** Called once the user takes an option, with the input's new text. */
    onchange?: (value: string, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { open = $bindable(false), onchange, onkeydowncapture, ref = $bindable(null), children, ...rest }: Props = $props();
  const uid = $props.id();

  const LISTBOX = '[role="listbox"]';
  const OPTION = '[role="option"]';
  const MARK = 'data-highlighted';

  const disabled = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  /** An option's text, as the input shows it once taken. */
  const textOf = (el: Element) => (el.textContent ?? '').trim();
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };

  /** The root, kept after unmount, so that a listener or an observer that outlived it would still act, and be seen. */
  let node: HTMLDivElement | null = null;
  /** Whether the key going down is Home or End, which stay with the input's text even while the list is open. */
  let textKey = false;
  /** Whether the list is open now, read without tracking. */
  const now = () => untrack(() => open);

  const input = () => node?.querySelector<HTMLInputElement>(':scope > input[data-part="input"]') ?? null;
  const readOnly = () => !!input()?.hasAttribute('readonly');
  const popup = () => node?.querySelector<HTMLElement>(':scope > [data-part="popup"]') ?? null;
  const listbox = () => popup()?.querySelector<HTMLElement>(LISTBOX) ?? null;
  /** The options of the listbox, and not of a listbox nested in one. */
  const options = () => {
    const list = listbox();
    return list ? [...list.querySelectorAll<HTMLElement>(OPTION)].filter((el) => el.closest(LISTBOX) === list) : [];
  };
  const shown = () => options().filter((el) => !el.hasAttribute('hidden'));

  /**
   * Asks for the list to open or close: the state changes, and the page shows it in the same task. No caller asks
   * for a read-only list to open, and the effect on `open` would close it.
   */
  const request = (next: boolean) => {
    if (next === now()) return;
    open = next;
    flushSync();
  };

  /** Shows the options whose text contains `text`, whatever its case, and hides the others, with the highlight cleared. */
  const filter = (text: string) => {
    const query = text.toLowerCase();
    const all = options();
    for (const option of all) put(option, MARK, null);
    for (const option of all) put(option, 'hidden', textOf(option).toLowerCase().includes(query) ? null : '');
    return shown().length;
  };

  /** Brings the input's ARIA, the listbox's passivity and the painted highlight in step. Writes nothing when they already are. */
  const sync = () => {
    const field = input(), box = popup(), list = listbox(), el = node;
    const on = now();
    if (box && !box.hasAttribute('popover')) box.setAttribute('popover', 'manual');
    if (list) {
      if (!list.id) list.id = `${uid}-listbox`;
      put(list, 'tabindex', '-1');
    }
    if (field) {
      put(field, 'role', 'combobox');
      put(field, 'aria-autocomplete', 'list');
      if (list) put(field, 'aria-controls', list.id);
      put(field, 'aria-expanded', String(on));
      if (el) put(el, 'aria-disabled', field.hasAttribute('disabled') ? 'true' : null);
    }
    // The option's recipe paints the highlight only on data-focus. The input has focus here, so the combobox writes it.
    const focused = !!field && field.ownerDocument.activeElement === field;
    for (const option of options()) put(option, 'data-focus', on && focused && option.hasAttribute(MARK) ? '' : null);
  };

  /**
   * Takes an option: its text goes into the input, it alone is selected, the list closes, and onchange is called
   * once all of that is written.
   */
  const take = (option: HTMLElement | null | undefined, event: Event) => {
    const field = input();
    if (!field || !option || disabled(option) || option.hasAttribute('hidden') || readOnly()) return;
    field.value = textOf(option);
    for (const other of options()) put(other, 'selected', other === option ? '' : null);
    filter(field.value);
    request(false);
    onchange?.(field.value, event);
  };

  // The listeners and the observer. `ref` is read untracked: a parent's binding would run this again, and lose them.
  $effect(() => untrack(() => {
    const el = ref!;
    node = el;
    const off = new AbortController();
    const listen = { signal: off.signal };
    // Something else hid the popup, such as a script calling hidePopover(): the state follows. toggle does not bubble.
    el.addEventListener('toggle', (event) => {
      const box = popup();
      if (!box || event.target !== box || box.matches(':popover-open')) return;
      if (now()) { open = false; flushSync(); }
    }, { capture: true, signal: off.signal });
    // Typing filters the options, and opens the list while one shows (J44). A read-only input fires no input event.
    el.addEventListener('input', (event) => {
      const field = input();
      if (!field || event.target !== field) return;
      request(filter(field.value) > 0);
    }, listen);
    // A click on an option takes it. The listbox has highlighted and selected it already.
    el.addEventListener('click', (event) => {
      const option = (event.target instanceof Element ? event.target.closest(OPTION) : null) as HTMLElement | null;
      if (option && options().includes(option)) take(option, event);
    }, listen);
    // A press moves no focus: inside the popup it would focus the listbox, and on the field around the input it
    // would take focus from the input, which it gives to the input instead.
    el.addEventListener('mousedown', (event) => {
      const field = input();
      if (!(event.target instanceof Node) || event.target === field) return;
      event.preventDefault();
      if (event.target === el) field?.focus();
    }, listen);
    el.addEventListener('focusin', sync, listen);
    el.addEventListener('focusout', sync, listen);
    const observer = new MutationObserver(() => {
      const field = input();
      // A disabled input takes no keys, and a read-only one opens no list, so its list does not stay open.
      if (now() && (field?.hasAttribute('disabled') || field?.hasAttribute('readonly'))) request(false);
      sync();
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'id', 'tabindex', 'popover', 'disabled', 'readonly', MARK, 'data-focus'] });
    sync();
    return () => { off.abort(); observer.disconnect(); };
  }));
  $effect(() => untrack(() => activeDescendant(ref!, {
    items: shown,
    skip: disabled,
    wrap: true,
    focus: () => input() ?? node!,
    active: () => !textKey && !readOnly(),
  })));
  // Escape, a press outside and focus that leaves close the list. A press on the input is inside the root.
  $effect(() => untrack(() => dismiss(ref!, {
    active: now,
    onDismiss: () => request(false),
  })));

  // Shows or hides the popup in the same flush as the change of `open`, and clears the highlight of a closed list.
  $effect(() => {
    const want = open;
    untrack(() => {
      // A read-only or disabled input does not open its list (J80).
      if (want && (readOnly() || input()?.hasAttribute('disabled'))) {
        open = false;
        sync();
        return;
      }
      sync(); // writes popover="manual" on a popup that has none, before it is shown
      const box = popup();
      if (box && want !== box.matches(':popover-open')) {
        if (want) box.showPopover();
        else box.hidePopover();
      }
      if (!want) for (const option of options()) put(option, MARK, null);
      sync();
    });
  });

  // Before the behaviours, which listen on the root: the keys the combobox handles itself.
  const keys: KeyboardEventHandler<HTMLDivElement> = (event) => {
    onkeydowncapture?.(event);
    const field = input();
    if (!field || event.target !== field) return;
    textKey = event.key === 'Home' || event.key === 'End';
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || readOnly()) return;
    const on = now();
    if ((event.key === 'ArrowDown' || event.key === 'ArrowUp') && !on) {
      // Opening first lets activeDescendant, which runs next, take the key: with nothing highlighted, ArrowDown goes
      // to the first option that shows and ArrowUp to the last.
      if (shown().length) request(true);
    } else if (event.key === 'Enter' && on) {
      const option = shown().find((el) => el.hasAttribute(MARK));
      if (!option) return; // Nothing highlighted: Enter submits the form, as in a plain input.
      event.preventDefault();
      take(option, event);
    } else if (event.key === 'Escape' && !on && field.value !== '') {
      // With the list open, dismiss closes it; with the list closed, Escape clears the field.
      event.preventDefault();
      field.value = '';
      filter('');
    }
  };

  // The div has no open of its own: it is an author attribute, as on the Web Component.
  const mirrored = $derived({ open: open ? '' : undefined });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions: the keys are the input's, heard on their way to it -->
<div
  {...rest}
  bind:this={ref}
  data-ui="combobox"
  {...mirrored}
  onkeydowncapture={keys}
>{@render children?.()}</div>
