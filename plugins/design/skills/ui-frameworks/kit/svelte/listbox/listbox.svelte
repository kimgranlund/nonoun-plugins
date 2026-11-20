<script lang="ts">
  // listbox.svelte: a list from which one option, or several, can be chosen, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="listbox">, one stop in the Tab order, that keeps focus: the options never take it. It
  // mounts activeDescendant and typeahead as the Web Component does, so the keys, a typed letter and a press move the
  // highlight, which the behaviour writes as data-highlighted and names in aria-activedescendant. In a single listbox
  // the selection follows the highlight; with `multiple` the keys only move it, and Space or a click toggles an option
  // (J27 to J29). As the React listbox.
  //
  // `value` is $bindable: `bind:value` follows the user, a plain `value` only starts it. With none, it is the options
  // the author marked `selected`, the last one in a single listbox. It is a string, the selected values joined by
  // commas with `multiple`, as on the Web Component. oninput(value, event) and then onchange(value, event) are called
  // when the user changes the selection, once the options are written (J29).
  //
  // The DOM is where the selection lives, because a combobox or a select of another family holds a listbox and writes
  // its options too: whenever the value or the subtree changes, the listbox writes `selected` on the options its value
  // names and on no other, only where it differs, and a `selected` that something else writes (a script, a select) is
  // read back as the value. The listbox renders none of the attributes another component writes on it or on its
  // options: tabindex, id, aria-activedescendant, selected, hidden, data-highlighted and data-focus are written into
  // the DOM, so Svelte never holds a value for them and never writes them again. tabindex="0" is written only where
  // the element has none, so a holder's tabindex="-1" stays.
  //
  // It is a form control with no native control of its own, so it renders a native <input type="hidden"> part per
  // submitted value, under `name` (V6, J30). A reset of the form restores the first value. Required-ness is only
  // aria-required: without ElementInternals nothing blocks a submit.
  //
  // On the server an option with no value prop has no known value (its text is a snippet), so a value that names it
  // is painted, and submitted, once the listbox has read its options in the browser.
  import { flushSync, setContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { activeDescendant } from '../../behaviours/active-descendant.js';
  import { typeahead } from '../../behaviours/typeahead.js';
  import { LISTBOX, type ListboxContext, type ListboxEntry } from './listbox.context.js';
  import { role } from '../../components/listbox/listbox.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'oninput' | 'onchange' | 'role'> & {
    value?: string;
    multiple?: boolean;
    name?: string;
    required?: boolean;
    disabled?: boolean;
    oninput?: (value: string, event: Event) => void;
    onchange?: (value: string, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let {
    value = $bindable(), multiple = false, name, required = false, disabled = false,
    oninput, onchange, onkeydown, onkeydowncapture, ref = $bindable(null), children, ...rest
  }: Props = $props();

  const OPTION = '[role="option"]';
  const LIST = '[role="listbox"]';
  const MARK = 'data-highlighted';

  const off = (el: Element) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, attr: string, to: string | null) => {
    if (el.getAttribute(attr) === to) return;
    if (to === null) el.removeAttribute(attr);
    else el.setAttribute(attr, to);
  };
  /** An option's value in the DOM: its `value` attribute, or else its text. */
  const valueOf = (el: Element) => el.getAttribute('value') ?? (el.textContent ?? '').trim();
  const known = (v: string | undefined): v is string => v !== undefined;

  /** The options as they registered, for the first render; afterwards the DOM's. */
  let entries: ListboxEntry[] = $state.raw([]);
  /** The values of the options in the DOM, in their order, once read; null until then. */
  let present: string[] | null = $state.raw(null);

  /** The values a value names: one, or with multiple those between the commas. */
  const split = (v: string) => (v === '' ? [] : multiple ? v.split(',') : [v]);
  /** Before the DOM is read and with no value: the options marked selected, the last one in a single listbox. */
  const marked = () => {
    const on = entries.filter((e) => e.selected);
    return (multiple ? on : on.slice(-1)).map((e) => e.value).filter(known);
  };
  // Functions, not $derived: on the server a derived keeps the value it first had, before the options register.
  const chosen = () => (value !== undefined ? split(value) : marked());
  const submitted = () => {
    if (!name || disabled) return [];
    const now = chosen();
    const list = present ?? entries.map((e) => e.value).filter(known);
    return multiple ? list.filter((v, i) => now.includes(v) && list.indexOf(v) === i) : now.length && list.includes(now[0]) ? [now[0]] : [];
  };

  setContext<ListboxContext>(LISTBOX, {
    given: () => value !== undefined,
    chosen,
    add(entry) { entries = [...entries, entry]; },
    remove(entry) { entries = entries.filter((e) => e !== entry); },
  });

  /** The root, kept after unmount, so that a listener or an observer that outlived it would still act, and be seen. */
  let node: HTMLDivElement | null = null;
  /** The value once the listbox first settled with its options: what a reset restores. */
  let initial: string | null = null;
  /** The option that was highlighted when the current key went down. */
  let before: HTMLElement | null = null;

  /** The options of this listbox, and not of another listbox nested in it. */
  const mine = () => (node ? [...node.querySelectorAll<HTMLElement>(OPTION)].filter((x) => x.closest(LIST) === node) : []);
  /** The values among `values` that name an option, once each, in the order of the options. */
  const ordered = (values: string[]) => [...new Set(mine().map(valueOf).filter((v) => values.includes(v)))];
  /** The highlighted option; while two carry the mark, the one that is not `was`. */
  const highlighted = (was: HTMLElement | null = null) => {
    const on = mine().filter((x) => x.hasAttribute(MARK));
    return on.find((x) => x !== was) ?? (was && on.includes(was) ? was : null);
  };
  /** Paints the highlight while the listbox has focus: data-focus on the highlighted option alone. */
  const mirror = (on: boolean) => {
    for (const option of mine()) put(option, 'data-focus', on && option.hasAttribute(MARK) ? '' : null);
  };
  /** Takes a value that the DOM says; Svelte writes the options in the next microtask, as an observer would. */
  const adopt = (next: string) => {
    if (next !== (value ?? '')) value = next;
  };

  /**
   * Takes the value from `selected` attributes that something else wrote: a script, a select, or an option whose
   * selected prop changed. Every record is read before anything is written.
   */
  const read = (records: MutationRecord[]) => {
    const options = mine();
    let now = chosen();
    let changed = false;
    for (const record of records) {
      const option = record.target as HTMLElement;
      if (record.attributeName !== 'selected' || !options.includes(option)) continue;
      const v = valueOf(option);
      if (option.hasAttribute('selected') && !now.includes(v)) now = multiple ? [...now, v] : [v];
      else if (!option.hasAttribute('selected') && now.includes(v)) now = now.filter((x) => x !== v);
      else continue;
      changed = true;
    }
    if (changed) adopt(multiple ? ordered(now).join(',') : now[0] ?? '');
  };

  /** Brings the options' `selected` in step with the value, and the values of the options with the DOM. */
  const sync = () => {
    const options = mine();
    const values = options.map(valueOf);
    if (!present || present.length !== values.length || present.some((v, i) => v !== values[i])) present = values;
    if (!options.length) return;
    const settling = initial === null;
    if (settling) {
      // No value given: take what the options rendered, the marks the author wrote.
      if (value === undefined) {
        const on = options.filter((x) => x.getAttribute('aria-selected') === 'true').map(valueOf);
        value = (multiple ? on : on.slice(-1)).join(',');
      }
      initial = value ?? '';
    }
    const now = chosen();
    for (const option of options) put(option, 'selected', now.includes(valueOf(option)) ? '' : null);
    // An option renders its first aria-selected before the options after it are known; the first look settles it.
    if (settling) for (const option of options) put(option, 'aria-selected', String(option.hasAttribute('selected')));
  };

  /** Selects an option, or with multiple toggles it, because the user asked; then tells the props. */
  const choose = (option: HTMLElement | null | undefined, event: Event) => {
    if (!option || off(option)) return;
    const v = valueOf(option);
    let next = v;
    if (multiple) {
      const now = chosen();
      next = ordered(now.includes(v) ? now.filter((x) => x !== v) : [...now, v]).join(',');
    }
    if (next === (value ?? '')) return;
    value = next;
    // The options are written before oninput and onchange are called (J29).
    flushSync();
    oninput?.(next, event);
    onchange?.(next, event);
  };

  // The observer and the listeners.
  $effect(() => {
    const el = ref!;
    node = el;
    const watch = new MutationObserver((records) => {
      read(records);
      sync();
      if (el.ownerDocument.activeElement === el) mirror(true);
    });
    watch.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'value', 'selected', 'disabled', 'aria-disabled', MARK] });
    const stop = new AbortController();
    const listen = { signal: stop.signal };
    // A press on an option highlights it and selects it, or with multiple toggles it. The options take no focus, so
    // the press leaves focus on the listbox, or gives it to the listbox. A disabled listbox answers nothing.
    el.addEventListener('click', (event) => {
      if (disabled) return;
      const option = (event.target instanceof Element ? event.target.closest(OPTION) : null) as HTMLElement | null;
      if (!option || !mine().includes(option)) return;
      put(option, MARK, '');
      choose(option, event);
    }, listen);
    // Taking focus highlights the first selected option, or the first that is not disabled, when none is.
    el.addEventListener('focus', () => {
      if (!highlighted()) {
        const usable = mine().filter((x) => !off(x));
        const first = usable.find((x) => x.hasAttribute('selected')) ?? usable[0];
        if (first) put(first, MARK, '');
      }
      mirror(true);
    }, listen);
    el.addEventListener('blur', () => mirror(false), listen);
    // A reset of the form puts the first value back, once the platform has reset its own controls.
    el.closest('form')?.addEventListener('reset', () => setTimeout(() => { if (initial !== null) adopt(initial); }), listen);
    return () => { watch.disconnect(); stop.abort(); };
  });
  $effect(() => activeDescendant(ref!, {
    items: mine,
    skip: off,
    fallback: () => mine().find((x) => x.hasAttribute('selected')),
  }));
  // The search starts from the highlighted option: focus stays on the listbox, so typeahead cannot see it.
  $effect(() => typeahead(ref!, { items: mine, current: () => highlighted(), skip: off, onMatch: (option) => put(option, MARK, '') }));

  // The options follow the value. A mark written since is read by the observer after this, and loses to the value.
  $effect(() => {
    chosen();
    untrack(sync);
  });
  // tabindex is written only where there is none, so a holder's tabindex="-1" stays; a disabled listbox has none.
  $effect(() => {
    const el = ref!;
    if (disabled) { if (el.getAttribute('tabindex') === '0') el.removeAttribute('tabindex'); }
    else if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<!-- svelte-ignore a11y_interactive_supports_focus: tabindex is written into the DOM, so that a holder's stays -->
<div
  {...rest}
  bind:this={ref}
  {role}
  data-ui="listbox"
  aria-multiselectable={multiple ? 'true' : undefined}
  aria-required={required ? 'true' : undefined}
  aria-disabled={disabled ? 'true' : undefined}
  onkeydowncapture={(event) => {
    // Before the behaviours, which listen on the root: which option was highlighted when the key went down.
    onkeydowncapture?.(event);
    if (event.target === node) before = highlighted();
  }}
  onkeydown={(event) => {
    // After the behaviours: a single listbox selects the option a key moved the highlight to; with multiple, Space
    // toggles the highlighted option.
    onkeydown?.(event);
    if (event.target !== node || disabled) return;
    if (multiple) {
      if (event.key !== ' ' || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      event.preventDefault();
      choose(highlighted(), event);
      return;
    }
    const after = highlighted(before);
    if (after !== before) choose(after, event);
  }}
>{@render children?.()}{#each submitted() as v (v)}<input type="hidden" data-part="input" {name} value={v} />{/each}</div>
