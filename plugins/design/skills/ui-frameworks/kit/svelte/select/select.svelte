<script lang="ts">
  // select.svelte: the APG's select-only combobox, a control that shows one chosen option and opens a list to choose
  // another, for Svelte (docs/specs/targets.md, V1 to V7). As the React select.
  //
  // The root is a <div role="combobox">: the one stop in the Tab order, which keeps focus. It renders the value part,
  // a <span> at its start with the chosen option's text, or the placeholder when none is chosen, and holds the
  // author's popup (the child marked data-part="popup"), which holds the kit's listbox. The option the keys point at
  // carries data-highlighted and is named by aria-activedescendant on the root (J82 to J86).
  //
  // The popup is the author's element, and the listbox and the options are of another family, so the select finds
  // them in the DOM, by data-part and by role, and writes what its manifest says it writes, only where it differs,
  // whenever its value or its open state changes and whenever its subtree changes: popover="manual" on a popup that
  // has none, an id and tabindex="-1" on the listbox, aria-controls on itself, and selected and data-focus on the
  // options; activeDescendant writes data-highlighted, the options' ids and aria-activedescendant. The select's value
  // decides which option is selected: it writes `selected` on that option and on no other, whoever else writes it.
  // The listbox's own logic still runs: a click on an option selects it there first, and the listbox then takes the
  // select's choice as its own.
  //
  // `value` and `open` are $bindable: `bind:value` and `bind:open` follow the user, a plain prop only starts them.
  // With no value, the value is the last option marked selected, once the options are in the DOM. oninput(value,
  // event) and then onchange(value, event) are called when the user chooses another option, after the value part, the
  // options and the closed list are written. The value part's text is read from the DOM, so the server, which cannot
  // read an option's text from its snippet, renders it empty (and unmarked) while a value is given (see the report).
  //
  // It is a form control with no native control of its own, so it renders a native <input type="hidden"> part with
  // `name` and the value (V6). A reset of the form restores the first value. Required-ness is only aria-required:
  // without ElementInternals nothing blocks a submit.
  import { flushSync, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { activeDescendant } from '../../behaviours/active-descendant.js';
  import { typeahead } from '../../behaviours/typeahead.js';
  import { dismiss } from '../../behaviours/dismiss.js';
  import { role, tabindex } from '../../components/select/select.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'oninput' | 'onchange' | 'role' | 'placeholder'> & {
    value?: string;
    name?: string;
    placeholder?: string;
    open?: boolean;
    required?: boolean;
    disabled?: boolean;
    oninput?: (value: string, event: Event) => void;
    onchange?: (value: string, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let {
    value = $bindable(), name, placeholder, open = $bindable(false), required = false, disabled = false,
    oninput, onchange, onkeydowncapture, ref = $bindable(null), children, ...rest
  }: Props = $props();
  const uid = $props.id();

  type Known = { value: string; text: string };
  const LISTBOX = '[role="listbox"]';
  const OPTION = '[role="option"]';
  const MARK = 'data-highlighted';
  const OPENERS = ['ArrowDown', 'ArrowUp', 'Home', 'End', 'Enter', ' '];

  const off = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  /** An option's text, as the value part shows it. */
  const textOf = (el: Element) => (el.textContent ?? '').trim();
  /** An option's value: its `value` attribute, or else its text. */
  const valueOf = (el: Element) => el.getAttribute('value') ?? textOf(el);
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, attr: string, to: string | null) => {
    if (el.getAttribute(attr) === to) return;
    if (to === null) el.removeAttribute(attr);
    else el.setAttribute(attr, to);
  };
  const same = (a: Known[], b: Known[]) => a.length === b.length && a.every((k, i) => k.value === b[i].value && k.text === b[i].text);

  /** The options in the DOM, with their values and texts, once read; null until then, and on the server. */
  let known: Known[] | null = $state.raw(null);
  const isOpen = $derived(open && !disabled);
  const current = () => value ?? '';
  // Functions, not $derived: what the template shows is read where it is shown.
  const chosen = () => (current() === '' || !known ? undefined : known.find((k) => k.value === current()));
  /** A value is given but the options are not read yet: the server, and the first render in the browser. */
  const pending = () => known === null && current() !== '';
  const submitted = () => (name && !disabled && (chosen() || pending()) ? current() : null);

  /** The root, kept after unmount, so that a listener or an observer that outlived it would still act, and be seen. */
  let node: HTMLDivElement | null = null;
  /** The value once the select first settled with its options: what a reset restores. */
  let initial: string | null = null;
  /** The option the list opens on, when Home, End or a typed letter opened it. */
  let target: HTMLElement | null = null;
  /** Whether the key going down opened the list, so that activeDescendant does not move on with it. */
  let opened = false;

  const popup = () => (node?.querySelector(':scope > [data-part="popup"]') ?? null) as HTMLElement | null;
  const listbox = () => (popup()?.querySelector(LISTBOX) ?? null) as HTMLElement | null;
  /** The options of the listbox, and not of a listbox nested in one. */
  const options = () => {
    const list = listbox();
    return list ? [...list.querySelectorAll<HTMLElement>(OPTION)].filter((el) => el.closest(LISTBOX) === list) : [];
  };
  const chosenOption = () => (current() === '' ? null : options().find((el) => valueOf(el) === current()) ?? null);
  const highlighted = () => options().find((el) => el.hasAttribute(MARK)) ?? null;
  /** Points at `to`, or else at the chosen option, or else at the first; never at a disabled one. */
  const point = (to: HTMLElement | null = null) => {
    const usable = options().filter((el) => !off(el));
    const at = chosenOption();
    const next = to ?? (at && usable.includes(at) ? at : usable[0]);
    if (next) put(next, MARK, '');
  };

  /** Opens or closes the list because the user asked; the popup follows in the same task. */
  const request = (next: boolean) => {
    if (next && disabled) return;
    if (next === isOpen) return;
    open = next;
    flushSync();
  };
  /** Opens the list on `to`, or on the chosen option. */
  const openAt = (to: HTMLElement | null | undefined) => { target = to ?? null; request(true); };

  /** Brings the listbox's passivity, the options' selection, the known texts and the painted highlight in step. */
  const sync = () => {
    const el = node, box = popup(), list = listbox();
    if (!el) return;
    if (box && !box.hasAttribute('popover')) box.setAttribute('popover', 'manual');
    if (list) {
      if (!list.id) list.id = `${uid}-listbox`;
      put(list, 'tabindex', '-1');
    }
    put(el, 'aria-controls', list ? list.id : null);
    const all = options();
    const now = all.map((o) => ({ value: valueOf(o), text: textOf(o) }));
    if (!known || !same(known, now)) known = now;
    if (all.length && initial === null) {
      // No value given: take the last option marked, by the author or by the listbox.
      if (value === undefined) {
        const marked = all.filter((o) => o.hasAttribute('selected') || o.getAttribute('aria-selected') === 'true').pop();
        value = marked ? valueOf(marked) : '';
      }
      initial = current();
    }
    const at = chosenOption();
    for (const option of all) put(option, 'selected', option === at ? '' : null);
    for (const option of all) put(option, 'data-focus', isOpen && option.hasAttribute(MARK) ? '' : null);
  };

  /**
   * Chooses an option because the user asked, closes the list, and then calls oninput and onchange when the value
   * changed. None only closes it.
   */
  const choose = (option: HTMLElement | null, event: Event) => {
    const before = current();
    const next = option ? valueOf(option) : before;
    if (next !== before) value = next;
    open = false;
    // The value part, the options and the closed list are written before oninput and onchange are called.
    flushSync();
    if (next === before) return;
    oninput?.(next, event);
    onchange?.(next, event);
  };

  // The observer and the listeners. `ref` is read untracked: a parent's function binding re-reads it whenever the
  // parent's own state changes, and a rerun would forget the first value.
  $effect(() => {
    const el = untrack(() => ref)!;
    node = el;
    const stop = new AbortController();
    const listen = { signal: stop.signal };
    // Something else hid the popup, such as a script calling hidePopover(): the state follows.
    el.addEventListener('toggle', (event) => {
      const box = popup();
      if (!box || event.target !== box || box.matches(':popover-open') || !isOpen) return;
      open = false;
      flushSync();
    }, { capture: true, signal: stop.signal });
    // A press on the select opens the list, or closes it; the press itself gives the root focus. A press in the
    // popup moves no focus: it would focus the listbox. A native listener, so that the author's onmousedown runs too.
    el.addEventListener('mousedown', (event) => {
      if (!(event.target instanceof Node)) return;
      if (popup()?.contains(event.target)) { event.preventDefault(); return; }
      if (event.button !== 0) return; // request() opens no disabled select
      request(!isOpen);
    }, listen);
    // A click on an option chooses it. The listbox has selected it already, and the select's value decides.
    el.addEventListener('click', (event) => {
      const option = (event.target instanceof Element ? event.target.closest(OPTION) : null) as HTMLElement | null;
      if (option && !off(option) && options().includes(option)) choose(option, event);
    }, listen);
    // A reset of the form puts the first value back, once the platform has reset its own controls.
    el.closest('form')?.addEventListener('reset', () => setTimeout(() => {
      if (initial !== null && initial !== current()) value = initial;
    }), listen);
    const watch = new MutationObserver(() => {
      // Options that arrive in an open list: point at one.
      if (isOpen && !highlighted()) point();
      sync();
    });
    watch.observe(el, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['role', 'id', 'value', 'tabindex', 'popover', 'selected', 'aria-selected', 'disabled', 'aria-disabled', MARK, 'data-focus'] });
    return () => { stop.abort(); watch.disconnect(); };
  });
  $effect(() => activeDescendant(untrack(() => ref)!, {
    items: options,
    skip: off,
    // A key on a closed select opens it first and sets `opened`, so this alone keeps a closed list still.
    active: () => !opened,
  }));
  $effect(() => typeahead(untrack(() => ref)!, {
    // The search starts from the option the keys point at, or from the chosen one while the list is closed.
    items: options,
    current: () => highlighted() ?? chosenOption(),
    skip: off,
    onMatch: (option) => {
      if (isOpen) put(option, MARK, '');
      else openAt(option);
    },
  }));
  // Escape, a press outside and focus that leaves close the list and keep the value. Escape goes no further.
  $effect(() => dismiss(untrack(() => ref)!, {
    active: () => isOpen,
    onDismiss: () => request(false),
  }));

  // The options follow the value.
  $effect(() => {
    void current();
    untrack(sync);
  });
  // A disabled select closes its list, which stays closed once it is enabled again (J86).
  $effect(() => {
    if (disabled) untrack(() => { if (open) open = false; });
  });
  // Shows or hides the popup in the same flush as the change that opened or closed it; points at an option when the
  // list opens, and at none once it closes.
  $effect(() => {
    const want = isOpen;
    untrack(() => {
      const box = popup();
      sync(); // writes popover="manual" on a popup that has none, before it is shown
      const showing = !!box?.matches(':popover-open');
      if (box && want !== showing) {
        if (want) box.showPopover();
        else box.hidePopover();
      }
      if (want && !showing) point(target);
      target = null;
      if (!want) for (const option of options()) put(option, MARK, null);
      sync();
    });
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });

  // While a value is given but its option is not read yet (the server), the value part holds a no-break space, so that
  // it has the line's height it will have once the text is read.
  // A div has no open attribute in svelte/elements: the author attribute the recipe reads (X2).
  const mirrored = $derived({ open: isOpen ? '' : undefined });
</script>

<!-- svelte-ignore a11y_no_noninteractive_tabindex: the role is combobox, read from the generated props -->
<div
  {...rest}
  bind:this={ref}
  {role}
  data-ui="select"
  tabindex={disabled ? undefined : tabindex}
  aria-haspopup="listbox"
  aria-expanded={isOpen ? 'true' : 'false'}
  aria-required={required ? 'true' : undefined}
  aria-disabled={disabled ? 'true' : undefined}
  {...mirrored}
  onkeydowncapture={(event) => {
    // Before the behaviours, which listen on this root: the keys that open the list, and those that choose.
    onkeydowncapture?.(event);
    opened = false;
    if (event.target !== node || disabled || event.altKey || event.ctrlKey || event.metaKey) return;
    if (!isOpen) {
      if (!OPENERS.includes(event.key)) return;
      const usable = options().filter((el) => !off(el));
      event.preventDefault();
      opened = true;
      openAt(event.key === 'Home' ? usable[0] : event.key === 'End' ? usable[usable.length - 1] : null);
    } else if (event.key === 'Enter' || event.key === ' ' || event.key === 'Tab') {
      // Tab keeps its default: the choice is made, and focus moves on.
      if (event.key !== 'Tab') event.preventDefault();
      choose(highlighted(), event);
    }
  }}
><span data-part="value" data-placeholder={chosen() || pending() ? undefined : ''}>{chosen()?.text ?? (pending() ? '\u00a0' : placeholder ?? '')}</span>{@render children?.()}{#if submitted() !== null}<input type="hidden" data-part="input" {name} value={submitted()} />{/if}</div>
