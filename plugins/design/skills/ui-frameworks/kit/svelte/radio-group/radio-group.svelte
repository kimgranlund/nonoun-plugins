<script lang="ts">
  // radio-group.svelte: the radio group for Svelte (docs/specs/targets.md, V1 to V7). It is the form control of the
  // family and coordinates its radios through context (radio-group.context.js).
  //
  // The root is a <div role="radiogroup">. Its radios are labels around native radio inputs, and the group gives
  // them all one `name`, so the browser's own grouping, its radio keys and its form value do the work. With no
  // `name` it makes one up for the grouping and writes form="" on the inputs, so that nothing is submitted under it.
  // The group still mounts roving focus, as the Web Component does: it makes the group one stop in the Tab order,
  // moves focus with the arrows of both orientations, wraps, skips what is disabled, and adds Home and End. Roving
  // focus prevents the arrows' default action, which is the browser's own move-and-check, so the group checks the
  // radio that then has focus by clicking it. As the React radio group.
  //
  // States on the root, in the ARIA the radiogroup role allows (X2): aria-required, aria-invalid once the user is
  // due to be told (F5), aria-disabled, aria-orientation="horizontal"; the variant is data-variant. The segmented
  // variant's thumb (C32) is the recipe's ::before, anchored on the checked radio's label: nothing to render.
  //
  // value is $bindable: bind:value follows the user, a plain value only starts it, and a function binding that
  // keeps its value decides, as a controlled value in React. With none, it is the value of the first radio marked
  // `checked` when the group mounts (J4). A radio without a value has its position among the group's radios, in
  // the order they were created, as its value. oninput(value, event) and onchange(value, event) are called when the
  // user chooses another radio, after the radios are up to date (J6); neither is called when the value prop changes.
  import { flushSync, setContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes, KeyboardEventHandler } from 'svelte/elements';
  import { rovingFocus } from '../../behaviours/roving-focus.js';
  import { RADIO_GROUP, type RadioGroupContext, type RadioEntry } from './radio-group.context.js';
  import { props as spec, role } from '../../components/radio-group/radio-group.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'oninput' | 'onchange' | 'onkeydown'> & {
    value?: string;
    name?: string;
    required?: boolean;
    disabled?: boolean;
    orientation?: 'vertical' | 'horizontal';
    variant?: 'plain' | 'segmented';
    oninput?: (value: string, event: Event) => void;
    onchange?: (value: string, event: Event) => void;
    /** The root's own keydown, called before the group acts on an arrow. */
    onkeydown?: KeyboardEventHandler<HTMLDivElement>;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let {
    value = $bindable(), name, required = false, disabled = false, orientation, variant,
    oninput, onchange, onkeydown, ref = $bindable(null), children, ...rest
  }: Props = $props();

  /** Shown by the browser when a required group has no choice. From the manifest's `messages`. */
  const VALUE_MISSING = 'Please choose one';
  const ARROWS = ['ArrowDown', 'ArrowRight', 'ArrowUp', 'ArrowLeft'];
  const INPUT = 'input[data-part="input"][type="radio"]';

  const uid = $props.id();
  const pick = (key: 'orientation' | 'variant', given: unknown) => {
    const p = spec[key] as { values: readonly string[], default: string };
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };
  const horizontal = $derived(pick('orientation', orientation) === 'horizontal');
  const kind = $derived(pick('variant', variant));

  let radios: RadioEntry[] = $state.raw([]);
  const valueOf = (entry: RadioEntry) => entry.value ?? String(radios.indexOf(entry));
  /** The value of the first radio marked checked, among the radios known so far. */
  const first = () => {
    const radio = radios.find((r) => r.checked);
    return radio ? valueOf(radio) : '';
  };
  // A function, not $derived: on the server a derived keeps the value it first had, before the later radios register.
  const current = () => value ?? first();
  /** The user is due to be told that the value is invalid (F5): after a change or a submit attempt, until a reset. */
  let told = $state(false);
  const named = () => (radios.length ? radios.some((r) => valueOf(r) === current()) : current() !== '');
  const invalid = $derived(told && required && !named());

  /** The inputs of this group's own radios, and not of a group nested in one. */
  const inputsOf = (root: HTMLElement | null) => [...(root?.querySelectorAll<HTMLInputElement>(INPUT) ?? [])].filter((el) => el.closest('[data-ui="radio-group"]') === root);
  const inputs = () => inputsOf(ref);
  /** Puts each input's checked state on the group's value: after a reset, or a user change a binding refused. */
  const write = () => {
    const now = current();
    for (const el of inputs()) if (el.checked !== (now !== '' && el.value === now)) el.checked = !el.checked;
  };

  setContext<RadioGroupContext>(RADIO_GROUP, {
    name: () => name ?? uid,
    anonymous: () => name === undefined,
    value: current,
    disabled: () => disabled,
    required: () => required,
    add(entry) { radios = [...radios, entry]; },
    remove(entry) { radios = radios.filter((r) => r !== entry); },
    valueOf,
    // The browser fires input and change only when a radio becomes checked, so each is a change of value.
    input(next, event) {
      told = true;
      value = next;
      // The radios are written before oninput and onchange are called, so a listener reads them up to date (J6).
      flushSync();
      oninput?.(next, event);
    },
    change(next, event) {
      onchange?.(next, event);
      // A binding that kept its value has the last word: the inputs are put back once the listeners have seen them.
      write();
    },
    invalid() { told = true; },
  });

  // The value the group starts with is fixed when it mounts: a radio marked checked later does not change it (J4).
  let initial = '';
  $effect(() => {
    untrack(() => {
      if (value === undefined) value = first();
      initial = current();
    });
  });

  // The browser's own message is replaced by the manifest's while a required group has no choice.
  $effect(() => {
    const message = required && !named() ? VALUE_MISSING : '';
    for (const el of inputs()) el.setCustomValidity(message);
  });

  $effect(() => {
    const el = ref;
    if (!el) return;
    return rovingFocus(el, {
      items: () => inputsOf(el),
      orientation: () => 'both',
      current: () => inputsOf(el).find((input) => input.checked),
      skip: (item) => item.matches(':disabled'),
      watch: ['checked'],
    });
  });

  // A form reset puts the inputs back to their defaults; the value follows, and the inputs are written (F6).
  $effect(() => {
    const form = ref?.closest('form');
    if (!form) return;
    const off = new AbortController();
    form.addEventListener('reset', () => setTimeout(() => {
      value = initial;
      told = false;
      flushSync();
      write();
    }), { signal: off.signal });
    return () => off.abort();
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });

  const keydown = (event: KeyboardEvent & { currentTarget: EventTarget & HTMLDivElement }) => {
    onkeydown?.(event);
    // Roving focus has moved focus to the next radio and prevented the browser's own move, which would have
    // checked it: the radio that has focus now is chosen (J5).
    if (!ARROWS.includes(event.key) || !event.defaultPrevented) return;
    const active = document.activeElement;
    if (active !== event.target && active instanceof HTMLInputElement && inputs().includes(active)) active.click();
  };
</script>

<div
  {...rest}
  bind:this={ref}
  {role}
  data-ui="radio-group"
  data-variant={kind}
  aria-orientation={horizontal ? 'horizontal' : undefined}
  aria-required={required ? 'true' : undefined}
  aria-disabled={disabled ? 'true' : undefined}
  aria-invalid={invalid ? 'true' : undefined}
  onkeydown={keydown}
>{@render children?.()}</div>
