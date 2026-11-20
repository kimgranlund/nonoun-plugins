<script lang="ts">
  // date-field.svelte: a text field for a date, with a calendar to choose it from, for Svelte (docs/specs/targets.md,
  // V1 to V7; J109 to J113 of docs/specs/patterns.md). As the React date field.
  //
  // The root is a <span> with data-ui="date-field" and no role, the box the popup is placed against. It holds the
  // author's children: the native text input marked data-part="input", which has no name, and the element marked
  // data-part="popup", which holds a calendar. Both are found in the DOM and never cloned or wrapped; the input must
  // be uncontrolled (no value of the author's), since the field writes its text. The field renders, after them, a
  // hidden input that carries name and value (V6; the author's input already holds the part name "input", so it
  // carries none), and the toggle part, a <span role="button" tabindex="-1"> at the end.
  //
  // As the Web Component does, the field gives the input the combobox role unless the author wrote one, with
  // aria-haspopup, aria-expanded, aria-controls, aria-required and aria-invalid, disables it while the field is
  // disabled and enables only an input it disabled; it gives the popup popover="manual", the dialog role and an id
  // where the author wrote none. It reads typed text when focus leaves the input and on Enter, with the Web
  // Component's own routines (date-field.text.js, D113), and writes the text of the value held. Its validity is the
  // author's input's: setCustomValidity with the Web Component's messages, so a submit is blocked and focuses the
  // input.
  //
  // The calendar belongs to another family (V4). It is found from the grid inside the popup (the nearest element
  // around the grid with the group role or a custom element's tag), and the field writes `value`, `min` and `max` on
  // it whenever they or the subtree change, and `value` again on opening, so the calendar shows the month of the date
  // held. The Svelte calendar watches those attributes; a Web Component calendar takes them as its own. The day the
  // user chooses comes back from the calendar's change event, read from the day it marks aria-selected.
  //
  // States (X2): open is the author attribute `open` on the root, rendered once the popup is showing, so the server
  // markup paints closed; invalid and disabled are author attributes; hover and focus-within are the root's own;
  // read-only is the input's own readonly, which the recipe reads through :has().
  //
  // `value` and `open` are $bindable: bind:value and bind:open follow the user, a plain prop only starts them, and a
  // new one from the page wins. oninput(value, event) then onchange(value, event) are called when the date changes,
  // after a read or a choice, once the text, the hidden input and the popup are written. `open` opens and closes the
  // popup as the Web Component's attribute does when a script writes it, without moving focus. The keys go through
  // onkeydown, and Enter or Space on the day already held through onkeydowncapture, before the calendar's own
  // capture handler; the press on the toggle is a native listener, so the author's onclick still reaches the root.
  // `today` (yyyy-mm-dd) is injectable, for the century of a two-digit year.
  import { flushSync, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { dismiss } from '../../behaviours/dismiss.js';
  import { parseDate, serial, iso } from '../../components/calendar/calendar.dates.js';
  import { format, read } from '../../components/date-field/date-field.text.js';

  type Props = Omit<HTMLAttributes<HTMLSpanElement>, 'children' | 'oninput' | 'onchange'> & {
    value?: string;
    name?: string;
    min?: string;
    max?: string;
    open?: boolean;
    required?: boolean;
    disabled?: boolean;
    /** Today, as yyyy-mm-dd, for the century of a two-digit year; without it, the user's clock. */
    today?: string;
    /** Called when the date changes, once the field shows it. */
    oninput?: (value: string, event: Event) => void;
    /** Called after oninput. */
    onchange?: (value: string, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLSpanElement | null;
    children?: Snippet;
  };

  let {
    value = $bindable(), name, min, max, open = $bindable(false), required = false, disabled = false, today,
    oninput, onchange, onkeydown, onkeydowncapture, ref = $bindable(null), children, ...rest
  }: Props = $props();

  /** The toggle's name. */
  const TOGGLE = 'Choose a date';
  /** What the browser shows for an invalid field: the Web Component's messages. */
  const VALUE_MISSING = 'Please enter a date.';
  const BAD_INPUT = 'Please enter a whole date.';
  const BELOW = (at: string) => `Please enter a date on or after ${at}.`;
  const ABOVE = (at: string) => `Please enter a date on or before ${at}.`;

  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, attr: string, to: string | null) => {
    if (el.getAttribute(attr) === to) return;
    if (to === null) el.removeAttribute(attr);
    else el.setAttribute(attr, to);
  };
  /** The language of the text: the nearest lang, or the browser's. */
  const langOf = (el: Element) => {
    const lang = el.closest('[lang]')?.getAttribute('lang') || navigator.language || 'en';
    try { return Intl.getCanonicalLocales(lang)[0] ?? 'en'; } catch { return navigator.language || 'en'; }
  };
  /** Today in the user's own time zone, as yyyy-mm-dd: read only when no `today` is given. */
  const clock = () => { const at = new Date(); return iso({ y: at.getFullYear(), m: at.getMonth() + 1, d: at.getDate() }); };
  /** Whether a disabled fieldset around the element disables it (F4): one whose first legend does not hold it. */
  const fenced = (el: Element) => {
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) {
      if (!f.disabled) continue;
      const legend = [...f.children].find((c) => c.localName === 'legend');
      if (!legend || !legend.contains(el)) return true;
    }
    return false;
  };
  const plain = (event: KeyboardEvent) => !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey;

  const uid = $props.id();
  const popupId = `${uid}popup`;

  /** The popup is showing: the root's open attribute. */
  let showing = $state(false);
  /** The invalid mark is shown on the root. */
  let marked = $state(false);
  let fieldsetOff = $state(false);
  // The first value, which a form reset restores.
  const first = untrack(() => value) ?? '';

  const held = $derived(value ?? '');
  const day = $derived(parseDate(held));
  const heldDate = $derived(day ? iso(day) : '');
  const off = $derived(disabled || fieldsetOff);

  /** The root, kept after unmount, so that a listener that outlived it would still act, and be seen. */
  let node: HTMLSpanElement | null = null;
  /** The popup is showing, read by dismiss and the toggle listener while the popover changes, so neither closes it twice. */
  let now = false;
  /**
   * What the field holds between flushes: the user has typed since the text was last written or read; the text is
   * not a date; the user is due to be told; the message set; the input marked aria-invalid; the input disabled; the
   * input the text was last written in.
   */
  const s = {
    draft: false, bad: false, told: false, message: '',
    marked: null as HTMLInputElement | null, disabledInput: null as HTMLInputElement | null, shown: null as HTMLInputElement | null,
  };

  /** The author's input. */
  const inputOf = () => {
    const el = node?.querySelector(':scope > [data-part="input"]');
    return el instanceof HTMLInputElement ? el : null;
  };
  const popupOf = () => node?.querySelector<HTMLElement>(':scope > [data-part="popup"]') ?? null;
  const toggleOf = () => node?.querySelector<HTMLElement>(':scope > [data-part="toggle"]') ?? null;
  /** The calendar in the popup: the nearest element around its grid, inside the popup, that is a group or a custom element. */
  const calendarOf = (): HTMLElement | null => {
    const popup = popupOf();
    const grid = popup?.querySelector('[role="grid"]');
    for (let el = grid?.parentElement ?? null; el && el !== popup; el = el.parentElement) if (el.getAttribute('role') === 'group' || el.localName.includes('-')) return el;
    return null;
  };
  /** The field cannot be changed: its input is read-only or disabled. A disabled field has disabled its input. */
  const locked = () => { const input = inputOf(); return !input || input.readOnly || input.disabled; };
  const lang = () => (node ? langOf(node) : 'en');

  /** Writes the text of a value into the input, and drops a draft and an unreadable text. */
  const show = (v: string) => {
    const input = inputOf();
    s.shown = input;
    s.draft = false;
    s.bad = false;
    if (!input) return;
    const d = parseDate(v);
    const text = d ? format(lang(), d) : '';
    if (input.value !== text) input.value = text;
    if (input.ownerDocument.activeElement === input) {
      // The caret goes to the end of the rewritten text, and the field scrolls to show it (form.caret-after-rewrite).
      input.setSelectionRange(text.length, text.length);
      input.scrollLeft = input.scrollWidth;
    }
  };

  /** The message of the field's validity, or '' when it is valid. */
  const message = () => {
    if (s.bad) return BAD_INPUT;
    if (!day) return required ? VALUE_MISSING : '';
    const lo = parseDate(min), hi = parseDate(max);
    if (lo && serial(day) < serial(lo)) return BELOW(format(lang(), lo));
    if (hi && serial(day) > serial(hi)) return ABOVE(format(lang(), hi));
    return '';
  };

  /** Writes value, min and max on the calendar. On opening, the value is written again so the calendar shows its month. */
  const hand = (opening = false) => {
    const calendar = calendarOf();
    if (!calendar) return;
    const v = heldDate || null;
    if (opening && v !== null) calendar.setAttribute('value', v);
    else put(calendar, 'value', v);
    put(calendar, 'min', min || null);
    put(calendar, 'max', max || null);
  };

  /** Brings the input's, the popup's, the toggle's and the calendar's attributes in step, and the validity and the mark. */
  const sync = () => {
    const input = inputOf(), popup = popupOf();
    if (popup) {
      if (!popup.hasAttribute('popover')) popup.setAttribute('popover', 'manual');
      if (!popup.hasAttribute('role')) popup.setAttribute('role', 'dialog');
      if (!popup.id) popup.id = popupId;
    }
    if (input) {
      // Disabled, by the prop or a fieldset: the input is disabled with it; only an input the field disabled is enabled.
      if (off && !input.disabled) { input.disabled = true; s.disabledInput = input; }
      else if (!off && s.disabledInput) { s.disabledInput.disabled = false; s.disabledInput = null; }
      if (!input.hasAttribute('role')) input.setAttribute('role', 'combobox');
      put(input, 'aria-haspopup', 'dialog');
      put(input, 'aria-expanded', String(now));
      put(input, 'aria-controls', popup ? popup.id : null);
      put(input, 'aria-required', required ? 'true' : null);
      const text = message();
      if (s.message !== text || input.validationMessage !== text) { input.setCustomValidity(text); s.message = text; }
    }
    hand();
    // Marked while the user is due to be told (J111); only a mark the field wrote is taken off.
    const shown = !!input && (s.bad || (s.told && s.message !== ''));
    if (s.marked && s.marked !== input) put(s.marked, 'aria-invalid', null);
    if (input && (shown || s.marked === input)) put(input, 'aria-invalid', shown ? 'true' : null);
    s.marked = shown ? input : null;
    marked = shown;
  };

  /**
   * Shows or hides the popup. A field that cannot be changed does not open (J113). From an event the page shows it
   * in the same task; from an effect, in the flush already running.
   */
  const apply = (want: boolean, flush = true) => {
    const popup = popupOf();
    const yes = want && !!popup && !locked() && !off;
    if (popup) {
      const was = popup.matches(':popover-open');
      now = yes;
      if (yes && !was) { sync(); hand(true); popup.showPopover(); }
      else if (!yes && was) popup.hidePopover();
    }
    now = yes;
    showing = yes;
    if (open !== yes) open = yes;
    if (flush) { sync(); flushSync(); }
    return yes;
  };

  /** Sets the value because the user asked for it, and tells listeners when it changed. */
  const set = (next: string, event: Event, keep = false) => {
    const before = held;
    s.told = true;
    value = next;
    flushSync();
    if (!keep) show(next);
    sync();
    flushSync();
    if (next === before) return;
    oninput?.(next, event);
    onchange?.(next, event);
  };

  /** Reads what the user typed, when they typed (J110, J111). */
  const commit = (event: Event) => {
    const input = inputOf();
    if (!input || !s.draft || locked()) return;
    const year = parseDate(today ?? clock())?.y ?? 2000;
    const v = read(lang(), input.value, year);
    s.draft = false;
    if (v === null) { s.bad = true; set('', event, true); }
    else set(v, event);
  };

  /** Moves focus to the calendar's Tab stop, which is the chosen day when there is one in the month shown. */
  const enter = () => popupOf()?.querySelector<HTMLElement>('[role="grid"] [tabindex="0"]')?.focus();

  /**
   * Opens the popup because the user asked for it: reads a draft first, then hands the calendar the date and moves
   * focus into it. The Svelte calendar takes the attributes from its observer, a microtask later: focus follows then.
   */
  const openUp = (event: Event) => {
    commit(event);
    if (apply(true)) queueMicrotask(enter);
  };

  /** Closes the popup, and gives focus back to the input when it was in the popup. */
  const close = () => {
    const popup = popupOf();
    const inside = !!popup && popup.contains(popup.ownerDocument.activeElement);
    apply(false);
    if (inside) inputOf()?.focus();
  };

  /** Takes the day chosen in the calendar, closes the popup and gives focus back to the input. */
  const take = (v: string | null | undefined, event: Event) => {
    if (!parseDate(v)) return;
    apply(false);
    inputOf()?.focus();
    set(v as string, event);
  };

  /** The day the calendar holds: the one it marks selected, or else the one it focused when it was chosen. */
  const chosenIn = (calendar: HTMLElement) => calendar.querySelector('[role="grid"] [aria-selected="true"]')?.getAttribute('data-date')
    ?? (calendar.contains(calendar.ownerDocument.activeElement) ? calendar.ownerDocument.activeElement?.getAttribute('data-date') : null);

  // The listeners and the observers. `ref` is read untracked: a parent's binding would run this again, and lose them.
  $effect(() => untrack(() => {
    const el = ref!;
    node = el;
    const quit = new AbortController();
    const listen = { signal: quit.signal };
    // A disabled fieldset around the field disables it (F4); its disabled attribute is watched, since no event tells.
    fieldsetOff = fenced(el);
    const fence = new MutationObserver(() => { fieldsetOff = fenced(el); flushSync(); });
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) fence.observe(f, { attributes: true, attributeFilter: ['disabled'] });
    // The calendar's own events stop here: the field's say when the date changed. A day chosen comes from its change.
    for (const type of ['input', 'change']) {
      el.addEventListener(type, (event) => {
        const calendar = calendarOf();
        if (calendar && event.target === calendar) {
          event.stopPropagation();
          if (type === 'change' && now) take(chosenIn(calendar), event);
          return;
        }
        if (type === 'input' && event.target === inputOf()) s.draft = true;
      }, listen);
    }
    // Focus that leaves the input reads what was typed.
    el.addEventListener('focusout', (event) => { if (event.target === inputOf()) commit(event); }, listen);
    // A submit attempt tells the user. invalid does not bubble: it reaches the root in the capture phase.
    el.addEventListener('invalid', (event) => { if (event.target === inputOf()) { s.told = true; sync(); flushSync(); } }, { ...listen, capture: true });
    // Something else hid the popup, such as a script calling hidePopover(): the state follows. toggle does not bubble.
    el.addEventListener('toggle', (event) => {
      const popup = popupOf();
      if (popup && event.target === popup && now && !popup.matches(':popover-open')) apply(false);
    }, { ...listen, capture: true });
    // The toggle opens and closes; a press on the day already held closes the popup with it. The calendar hears the
    // press first, and dispatches nothing for the day it holds.
    el.addEventListener('click', (event) => {
      if (!(event.target instanceof Element)) return;
      const toggle = toggleOf();
      if (toggle && toggle.contains(event.target)) {
        if (now) close();
        else openUp(event);
        return;
      }
      const cell = event.target.closest('[role="gridcell"]');
      const calendar = calendarOf();
      if (now && cell && calendar?.contains(cell) && cell.getAttribute('aria-selected') === 'true') take(cell.getAttribute('data-date'), event);
    }, listen);
    // A press on the field outside the input and the popup moves no focus to the press, and puts it in the input.
    el.addEventListener('mousedown', (event) => {
      const input = inputOf();
      const target = event.target instanceof Node ? event.target : null;
      if (!input || !target || target === input || popupOf()?.contains(target)) return;
      event.preventDefault();
      if (!input.disabled && !toggleOf()?.contains(target) && input.ownerDocument.activeElement !== input) input.focus();
    }, listen);
    // A reset puts the value back after the event: to its first, and its text; the user is no longer due to be told.
    el.ownerDocument.addEventListener('reset', (event) => {
      if (!(event.target instanceof HTMLFormElement) || !event.target.contains(el)) return;
      setTimeout(() => {
        if (!el.isConnected) return;
        s.told = false;
        value = first;
        flushSync();
        show(first);
        sync();
        flushSync();
      });
    }, listen);
    // An input or a popup that arrives or is replaced, a calendar that appears later, readonly or disabled written on the input.
    const observer = new MutationObserver(() => {
      if (inputOf() !== s.shown) show(held);
      if (now && locked()) apply(false);
      sync();
      flushSync();
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'role', 'readonly', 'disabled', 'id', 'popover'] });
    return () => { quit.abort(); fence.disconnect(); observer.disconnect(); };
  }));

  // Escape, a press outside and focus that leaves close the popup. Escape goes no further (overlay.escape-innermost).
  $effect(() => untrack(() => dismiss(ref!, {
    active: () => now,
    onDismiss: (reason: string) => {
      if (reason === 'escape') close();
      else apply(false);
    },
  })));

  // The attributes, the validity and the mark, in the flush that changes what they read.
  $effect(() => {
    void [heldDate, held, min, max, required, off, showing];
    untrack(sync);
  });

  // The text of the value held, whenever it changes. Unreadable text stays as typed while the value it emptied is
  // held (J111).
  $effect(() => {
    const at = heldDate;
    untrack(() => {
      if (s.bad && at === '') return;
      const input = inputOf();
      const d = parseDate(at);
      if (input && input.value === (d ? format(lang(), d) : '') && s.shown === input) return;
      show(at);
    });
  });

  // open from the page opens and closes the popup, as the Web Component's attribute does, without moving focus.
  $effect(() => {
    const want = open;
    untrack(() => apply(want, false));
  });

  // Disabled while open: the popup closes, in the same flush (J113).
  $effect(() => {
    void off;
    untrack(() => { if (now && (off || locked())) apply(false, false); });
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });

  /** The input's keys, and Alt+ArrowDown and Alt+ArrowUp (J110 to J112). */
  const keydown = (event: KeyboardEvent & { currentTarget: EventTarget & HTMLSpanElement }) => {
    onkeydown?.(event);
    const input = inputOf();
    if (event.altKey && !event.ctrlKey && !event.metaKey && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      if (event.key === 'ArrowDown' && event.target === input && !now) {
        event.preventDefault();
        openUp(event);
      } else if (event.key === 'ArrowUp' && now) {
        event.preventDefault();
        close();
      }
      return;
    }
    if (event.target !== input || !plain(event)) return;
    // Enter keeps its default, so the form is submitted with the date just read.
    if (event.key === 'Enter') commit(event);
    else if (event.key === 'Escape' && !now && s.draft) {
      event.preventDefault();
      event.stopPropagation();
      show(held);
      sync();
      flushSync();
    }
  };

  /**
   * Enter or Space on the day already held: the calendar would do nothing the field could hear, so the field takes
   * that day itself, before the calendar's own capture handler sees the key. The key is not stopped: the calendar then
   * chooses the same day in a popup already hidden, and its focus goes nowhere.
   */
  const keydowncapture = (event: KeyboardEvent & { currentTarget: EventTarget & HTMLSpanElement }) => {
    onkeydowncapture?.(event);
    if ((event.key !== 'Enter' && event.key !== ' ') || !plain(event) || !now) return;
    const cell = event.target instanceof Element ? event.target.closest('[role="gridcell"]') : null;
    const calendar = calendarOf();
    if (!cell || !calendar?.contains(cell) || cell.getAttribute('aria-selected') !== 'true') return;
    take(cell.getAttribute('data-date'), event);
  };

  // The span has no open, disabled or invalid of its own: they are author attributes, as on the Web Component. An
  // invalid the author wrote stays as written (J111).
  const mirrored = $derived({ open: showing ? '' : undefined, disabled: off ? '' : undefined, invalid: marked ? '' : (rest as Record<string, unknown>).invalid });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions: the keys are the author's input's and the calendar's, heard on their way -->
<span
  {...rest}
  bind:this={ref}
  data-ui="date-field"
  {...mirrored}
  onkeydown={keydown}
  onkeydowncapture={keydowncapture}
>{@render children?.()}<input type="hidden" {name} value={heldDate} disabled={off || heldDate === ''} /><span data-part="toggle" role="button" tabindex="-1" aria-label={TOGGLE} aria-disabled={off ? 'true' : undefined}></span></span>
