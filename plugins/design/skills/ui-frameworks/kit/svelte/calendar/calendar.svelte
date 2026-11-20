<script lang="ts">
  // calendar.svelte: one month of days in a grid, for Svelte (docs/specs/targets.md, V1 to V7; J103 to J107 of
  // docs/specs/patterns.md). As the React calendar.
  //
  // The root is a <div> with the group role, unless the author gives another, so the author's name is announced. It
  // renders everything the Web Component creates: a header part with a native button for the previous month, the
  // month's name as a polite live region and a native button for the next month; a grid part, a <table> with the grid
  // role named by the title, whose head row names the weekdays and whose body rows are the weeks; one <td> per day with
  // the gridcell role and data-part="day". The days of the neighbouring months that fill the first and the last week
  // are marked data-outside. A div is no form control, so a hidden input marked data-part="input" carries name and
  // value (V6), and the form submits it only while a date between min and max is chosen.
  //
  // The date arithmetic is the shared calendar.dates.js (D113): plain year, month and day numbers, so no time zone can
  // shift a day. The language is the nearest lang once the calendar is in the page, read again whenever a prop or the
  // month shown changes, as React reads it in each render; before that, on the server and while hydrating, it is the
  // root's own lang, or English. Today is the `today` prop (yyyy-mm-dd) when given, otherwise the user's clock: a test
  // or a server injects it, so the server markup shows the same month and cells as the browser.
  //
  // States (X2): the days carry the ARIA the conditions select (aria-selected, aria-current="date", aria-disabled),
  // the root and the grid aria-disabled while disabled, by the prop or a fieldset; hover, focus-visible and active are
  // the parts' own pseudo-classes. rovingFocus keeps the days of the month one Tab stop, and the stop is written after
  // every draw as well, in the same flush (J105). The days' tabindex is never rendered.
  //
  // The calendar's keys go through onkeydowncapture on the root, so they run before rovingFocus's listener on it,
  // which passes over a key whose default is already prevented (B8, D111). A press is a native listener added in an
  // effect, so the author's onclick still reaches the root.
  //
  // `value` is $bindable: bind:value follows the user, a plain value only starts it. oninput(value, event) and then
  // onchange(value, event) are called when the user chooses another day, once the grid shows it; input and change are
  // then dispatched, bubbling, from the root, so a component of another family, such as a date field, hears the
  // choice in the DOM. Such a component hands the calendar value, min and max as attributes written on its root: the
  // calendar watches them and renders none of the three. A value written there is taken as the value, and its month
  // shown again, even when it is the same; a min or max written there wins over the prop while it is present.
  import { flushSync, untrack } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { rovingFocus } from '../../behaviours/roving-focus.js';
  import { daysIn, serial, fromSerial, weekday, iso, parseDate, parseMonth, addMonths, weekStart, format, FIRST, LAST } from '../../components/calendar/calendar.dates.js';
  import { role as kitRole } from '../../components/calendar/calendar.props.js';

  type Day = { y: number, m: number, d: number };
  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'oninput' | 'onchange'> & {
    value?: string;
    name?: string;
    min?: string;
    max?: string;
    month?: string;
    required?: boolean;
    disabled?: boolean;
    /** Today, as yyyy-mm-dd; without it, the user's clock. */
    today?: string;
    /** Called when the user chooses another day, once the grid shows it. */
    oninput?: (value: string, event: Event) => void;
    /** Called after oninput. */
    onchange?: (value: string, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
  };

  let {
    value = $bindable(), name, min, max, month, required = false, disabled = false, today,
    oninput, onchange, onkeydowncapture, ref = $bindable(null), ...rest
  }: Props = $props();

  /** The names of the two buttons. */
  const NAMES = { previous: 'Previous month', next: 'Next month' };
  const DAY = '[data-part="day"]';

  /** Sets or removes an attribute, only when it differs. */
  const put = (el: Element, attr: string, to: string | null) => {
    if (el.getAttribute(attr) === to) return;
    if (to === null) el.removeAttribute(attr);
    else el.setAttribute(attr, to);
  };
  /** A language as Intl reads it, or English. */
  const canonical = (lang: string | null | undefined, fallback: string) => {
    try { return Intl.getCanonicalLocales(lang || fallback)[0] ?? 'en'; } catch { return fallback || 'en'; }
  };
  /** The language of the names: the nearest lang, or the browser's where that is empty, which HTML reads as unknown. */
  const langOf = (el: Element) => canonical(el.closest('[lang]')?.getAttribute('lang') || navigator.language, navigator.language || 'en');
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
  /** The grid of a calendar root. */
  const gridOf = (el: Element | null) => el?.querySelector<HTMLTableElement>(':scope > [data-part="grid"]') ?? null;
  /** Every cell of the grid's body. */
  const cellsOf = (el: Element | null) => [...(gridOf(el)?.querySelectorAll<HTMLElement>(`:scope > tbody > tr > ${DAY}`) ?? [])];
  /** The days of the month shown, which take focus, in order. */
  const daysOf = (el: Element | null) => cellsOf(el).filter((cell) => !cell.hasAttribute('data-outside'));

  const uid = $props.id();
  const titleId = `${uid}title`;

  /** The month the user moved to, with the value and the month given when they did: a new one from the page voids it. */
  type Moved = { y: number, m: number, value: string | undefined, month: string | undefined };
  let moved = $state.raw<Moved | null>(null);
  /** min and max written on the root by a component of another family, such as a date field. */
  let written = $state.raw<{ min: string | null, max: string | null }>({ min: null, max: null });
  let mounted = $state(false);
  let fieldsetOff = $state(false);
  // The first value, which a form reset restores (F6).
  const first = untrack(() => value) ?? '';

  const held = $derived(value ?? '');
  const off = $derived(disabled || fieldsetOff);
  const lo = $derived(parseDate(written.min ?? min));
  const hi = $derived(parseDate(written.max ?? max));
  const from = $derived(Math.max(FIRST, lo ? serial(lo) : FIRST));
  const to = $derived(Math.min(LAST, hi ? serial(hi) : LAST));
  const day = $derived(parseDate(held));
  const chosen = $derived(day && serial(day) >= from && serial(day) <= to ? iso(day) : null);
  const now = $derived(today ?? clock());
  const lang = $derived.by(() => {
    // Read again whenever a prop or the month shown changes, as React reads it in each render.
    void [value, name, min, max, month, required, disabled, today, moved, written, fieldsetOff, { ...rest }];
    return mounted && ref ? langOf(ref) : canonical(rest.lang, 'en');
  });
  const start = $derived(weekStart(lang));
  // A new value or month from the page voids the user's month, before the draw, so the page's month is shown in the
  // same flush; a choice moves with the value it sets, and keeps its month.
  $effect.pre(() => {
    if (moved && (moved.value !== value || moved.month !== month)) moved = null;
  });
  const shown = $derived(moved ?? parseMonth(month) ?? day ?? parseDate(now) ?? { y: 1970, m: 1 });
  const sy = $derived(shown.y);
  const sm = $derived(shown.m);

  // What does not change while the month and the language stay: the weeks, the numbers and the names.
  const sheet = $derived.by(() => {
    const number = new Intl.NumberFormat(lang, { useGrouping: false });
    // 2023-01-01 was a Sunday.
    const heads = Array.from({ length: 7 }, (_, n) => ({
      abbr: format(lang, { weekday: 'long' }, 2023, 1, 1 + ((start + n) % 7)),
      text: format(lang, { weekday: 'short' }, 2023, 1, 1 + ((start + n) % 7)),
    }));
    const one = serial({ y: sy, m: sm, d: 1 });
    const begin = one - ((weekday(one) - start + 7) % 7);
    const weeks = Math.ceil((one - begin + daysIn(sy, sm)) / 7);
    const rows = Array.from({ length: weeks }, (_, w) => Array.from({ length: 7 }, (__, n) => {
      const at = begin + w * 7 + n;
      const d = fromSerial(at);
      const inside = at >= FIRST && at <= LAST;
      return {
        at, text: number.format(d.d), outside: d.m !== sm || d.y !== sy,
        date: inside ? iso(d) : null, label: inside ? format(lang, { dateStyle: 'full' }, d.y, d.m, d.d) : null,
      };
    }));
    return { heads, rows, title: format(lang, { month: 'long', year: 'numeric' }, sy, sm, 1) };
  });

  /** Whether a day can be chosen: it has a date, between min and max. */
  const allowed = (date: string | null) => { const d = parseDate(date); return d !== null && serial(d) >= from && serial(d) <= to; };
  /** The cell of a day among the days of the month shown. */
  const cellOf = (date: string | null) => (date === null ? null : daysOf(ref).find((cell) => cell.getAttribute('data-date') === date) ?? null);
  /** The day that is the Tab stop while focus is outside the grid: the chosen day, or today, or the first day shown. */
  const preferred = () => cellOf(chosen) || cellOf(now) || daysOf(ref)[0] || null;

  /** Shows a day's month and moves focus to the day. */
  const focusDay = (d: Day) => {
    moved = { y: d.y, m: d.m, value, month };
    flushSync();
    cellOf(iso(d))?.focus();
  };

  /** Chooses a day because the user asked for it, then tells listeners on the root, who find the grid already written. */
  const choose = (d: Day, event: Event, el: HTMLDivElement) => {
    const n = serial(d);
    if (n < from || n > to) { focusDay(d); return; }
    const next = iso(d);
    const changed = next !== held;
    if (changed) value = next;
    focusDay(d);
    if (!changed) return;
    oninput?.(next, event);
    onchange?.(next, event);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };

  /** The calendar's keys on a day (date.grid-keys), ahead of rovingFocus. */
  const keydown = (event: KeyboardEvent & { currentTarget: EventTarget & HTMLDivElement }) => {
    onkeydowncapture?.(event);
    const el = event.currentTarget;
    const cell = event.target as HTMLElement;
    // WebKit keeps focus on a day that loses its tabindex when the calendar is disabled: its keys stop here.
    if (event.altKey || event.ctrlKey || event.metaKey || off || !daysOf(el).includes(cell)) return;
    const d = parseDate(cell.getAttribute('data-date'));
    if (!d) return;
    const paging = event.key === 'PageUp' || event.key === 'PageDown';
    if (event.shiftKey && !paging) return;
    const n = serial(d);
    const forward = getComputedStyle(el).direction === 'rtl' ? -1 : 1;
    const back = (weekday(n) - start + 7) % 7;
    let target: number | null = null;
    if (event.key === 'ArrowRight') target = n + forward;
    else if (event.key === 'ArrowLeft') target = n - forward;
    else if (event.key === 'ArrowDown') target = n + 7;
    else if (event.key === 'ArrowUp') target = n - 7;
    else if (event.key === 'Home') target = n - back;
    else if (event.key === 'End') target = n - back + 6;
    else if (paging) {
      const next = addMonths(d, (event.shiftKey ? 12 : 1) * (event.key === 'PageUp' ? -1 : 1));
      target = next ? serial(next) : n;
    } else if (event.key !== 'Enter' && event.key !== ' ') return;
    // rovingFocus would walk the days as a list; it passes over a key whose default is prevented (B8).
    event.preventDefault();
    if (target === null) { choose(d, event, el); return; }
    focusDay(fromSerial(target < FIRST || target > LAST ? n : target));
  };

  // A press on a day chooses it; on a button, shows the month before or after.
  $effect(() => {
    const el = untrack(() => ref!);
    const stop = new AbortController();
    el.addEventListener('click', (event) => {
      if (off || !(event.target instanceof Element)) return;
      const button = event.target.closest('[data-part="previous"], [data-part="next"]');
      if (button && button.parentElement?.parentElement === el) {
        // At 0001 or 9999 the button is aria-disabled, and addMonths stops there.
        const next = addMonths({ y: sy, m: sm, d: 1 }, button.getAttribute('data-part') === 'next' ? 1 : -1);
        if (next) { moved = { y: next.y, m: next.m, value, month }; flushSync(); }
      }
      // A button holds no day, so a press on one chooses nothing.
      const cell = event.target.closest(DAY);
      const d = cell && gridOf(el)?.contains(cell) ? parseDate(cell.getAttribute('data-date')) : null;
      if (d) choose(d, event, el);
    }, { signal: stop.signal });
    return () => stop.abort();
  });

  // The page's language and a fieldset around it are known once the calendar is in the page (F4).
  $effect(() => {
    const el = untrack(() => ref!);
    mounted = true;
    fieldsetOff = fenced(el);
    const observer = new MutationObserver(() => { fieldsetOff = fenced(el); flushSync(); });
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) observer.observe(f, { attributes: true, attributeFilter: ['disabled'] });
    return () => observer.disconnect();
  });

  // value, min and max written on the root by a component of another family (see the header).
  $effect(() => {
    const el = untrack(() => ref!);
    const read = () => ({ min: el.getAttribute('min'), max: el.getAttribute('max') });
    const observer = new MutationObserver((records) => {
      const at = read();
      if (at.min !== written.min || at.max !== written.max) written = at;
      if (records.some((r) => r.attributeName === 'value')) { value = el.getAttribute('value') ?? ''; moved = null; }
      flushSync();
    });
    observer.observe(el, { attributes: true, attributeFilter: ['value', 'min', 'max'] });
    untrack(() => {
      if (el.hasAttribute('min') || el.hasAttribute('max')) written = read();
      if (el.hasAttribute('value')) value = el.getAttribute('value') ?? '';
    });
    return () => observer.disconnect();
  });

  // Mounted untracked: rovingFocus asks current() and skip() as it mounts, and the effect must not run again whenever
  // the chosen day, today or disabled changes.
  $effect(() => {
    const el = untrack(() => ref!);
    return untrack(() => rovingFocus(el, {
      items: () => daysOf(el),
      current: () => preferred(),
      skip: () => off,
    }));
  });

  // The day focus is on before the grid is drawn again: a cell that is replaced gives focus back to the same day.
  let refocus: string | null = null;
  $effect.pre(() => {
    void sheet;
    untrack(() => {
      const active = ref?.ownerDocument.activeElement;
      refocus = active && gridOf(ref)?.contains(active) ? active.getAttribute('data-date') : null;
    });
  });

  // After every draw, in the same flush: one day of the month is the Tab stop, as rovingFocus will write it, and a
  // grid drawn again gives focus back to the day that had it (J105). A day of a neighbouring month takes no focus.
  $effect(() => {
    void [sheet, chosen, now, off];
    untrack(() => {
      const el = ref!;
      const days = daysOf(el);
      const active = el.ownerDocument.activeElement;
      const back = refocus && !(active && gridOf(el)?.contains(active)) ? cellOf(refocus) : null;
      const stop = off ? null : back || days.find((cell) => cell === active) || preferred();
      for (const cell of cellsOf(el)) put(cell, 'tabindex', stop === null || !days.includes(cell) ? null : cell === stop ? '0' : '-1');
      back?.focus();
      refocus = null;
    });
  });

  // A form reset puts the value back to its first one, and shows its month (F6).
  $effect(() => {
    const form = untrack(() => ref)?.querySelector<HTMLInputElement>(':scope > [data-part="input"]')?.form;
    if (!form) return;
    const stop = new AbortController();
    form.addEventListener('reset', () => setTimeout(() => { value = first; moved = null; flushSync(); }), { signal: stop.signal });
    return () => stop.abort();
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions: the keys are the days', which take focus; the root takes none -->
<div
  role={kitRole}
  {...rest}
  bind:this={ref}
  data-ui="calendar"
  aria-disabled={off ? 'true' : undefined}
  onkeydowncapture={keydown}
><div data-part="header"><button
  type="button" data-part="previous" aria-label={NAMES.previous}
  aria-disabled={sy === 1 && sm === 1 ? 'true' : undefined} disabled={off}
></button><span data-part="title" id={titleId} aria-live="polite">{sheet.title}</span><button
  type="button" data-part="next" aria-label={NAMES.next}
  aria-disabled={sy === 9999 && sm === 12 ? 'true' : undefined} disabled={off}
></button></div><!-- svelte-ignore a11y_role_supports_aria_props: as React and the Web Component, the grid says the calendar is required --><table
  data-part="grid" role="grid" aria-labelledby={titleId}
  aria-required={required ? 'true' : undefined} aria-disabled={off ? 'true' : undefined}
><thead><tr>{#each sheet.heads as h, n (n)}<th scope="col" abbr={h.abbr}>{h.text}</th>{/each}</tr></thead><tbody>{#each sheet.rows as row, w (w)}<tr>{#each row as c (c.date ?? `at${c.at}`)}<td
  role="gridcell" data-part="day"
  data-outside={c.outside ? '' : undefined} data-date={c.date ?? undefined} aria-label={c.label ?? undefined}
  aria-selected={c.date !== null && c.date === chosen ? 'true' : undefined}
  aria-current={c.date !== null && c.date === now ? 'date' : undefined}
  aria-disabled={allowed(c.date) ? undefined : 'true'}
>{c.text}</td>{/each}</tr>{/each}</tbody></table><input type="hidden" data-part="input" {name} value={chosen ?? ''} disabled={off || chosen === null} /></div>
