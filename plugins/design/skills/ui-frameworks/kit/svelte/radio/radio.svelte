<script lang="ts">
  // radio.svelte: one radio, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <label> that holds a native <input type="radio"> marked data-part="input", then the author's text,
  // as the checkbox is. The input takes focus and carries the group's name and its own value; the radio group
  // decides which one is checked. The label mirrors the state in the attributes the recipe's conditions select:
  // checked and its own disabled as author attributes (a disabled group disables the inputs and paints its radios
  // as the Web Component's group does, which is as enabled ones), and data-focus-visible and data-active while
  // focus or a key press is on the input (X2). In a segmented group the recipe draws the label alone, as the
  // segment; while checked it names itself the anchor of the group's thumb (C32). As the React radio.
  //
  // It registers with the nearest radio group as it is created, so a radio with no value has its position among
  // the group's radios as its value. `checked` marks the radio the group starts with, when the group has no value
  // of its own (J4). Outside a radio group a radio holds its own state: `checked` is $bindable. onclick is the
  // input's, called with (checked, event).
  import { flushSync, getContext, type Snippet } from 'svelte';
  import type { HTMLLabelAttributes } from 'svelte/elements';
  import { press } from '../../behaviours/press.js';
  import { RADIO_GROUP, type RadioGroupContext, type RadioEntry } from '../radio-group/radio-group.context.js';
  import { role } from '../../components/radio/radio.props.js';

  type Props = Omit<HTMLLabelAttributes, 'children' | 'onclick'> & {
    value?: string;
    checked?: boolean;
    disabled?: boolean;
    /** Called with the input's state, once per activation. */
    onclick?: (checked: boolean, event: MouseEvent) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLLabelElement | null;
    children?: Snippet;
  };

  let { value, checked = $bindable(false), disabled = false, onclick, ref = $bindable(null), children, ...rest }: Props = $props();

  // The manifest's role is the native input's own, so no role is written.
  void role;
  const group = getContext<RadioGroupContext | undefined>(RADIO_GROUP);
  const entry: RadioEntry = {
    get value() { return value; },
    get checked() { return checked; },
  };
  group?.add(entry);
  $effect(() => () => group?.remove(entry));

  const own = $derived(value ?? (group ? group.valueOf(entry) : ''));
  // A function, not $derived: on the server the group's value can change as the later radios register.
  const on = () => (group ? group.value() !== '' && group.value() === own : checked);
  const off = $derived(disabled || (group?.disabled() ?? false));
  /** An author attribute that holds while `yes`: present and empty, or absent. */
  const flag = (yes: boolean) => (yes ? '' : undefined);

  const input = (event: Event & { currentTarget: HTMLInputElement }) => {
    if (group) return group.input(own, event);
    checked = event.currentTarget.checked;
    flushSync();
  };
  const change = (event: Event & { currentTarget: HTMLInputElement }) => {
    if (group) return group.change(own, event);
    // A binding that kept its value has the last word, as a controlled input has in React.
    if (event.currentTarget.checked !== checked) event.currentTarget.checked = checked;
  };

  /** Focus and a key press happen on the input, a part: the root carries their state (X2). */
  const mirror = (el: HTMLInputElement) => {
    const label = el.parentElement as HTMLElement;
    const put = (attr: string, yes: boolean) => { if (label.hasAttribute(attr) !== yes) label.toggleAttribute(attr, yes); };
    const pressed = new MutationObserver(() => put('data-active', el.hasAttribute('data-active')));
    pressed.observe(el, { attributes: true, attributeFilter: ['data-active'] });
    const abort = new AbortController();
    el.addEventListener('focus', () => put('data-focus-visible', el.matches(':focus-visible')), { signal: abort.signal });
    el.addEventListener('blur', () => put('data-focus-visible', false), { signal: abort.signal });
    return () => { pressed.disconnect(); abort.abort(); put('data-active', false); put('data-focus-visible', false); };
  };

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<label
  {...rest}
  bind:this={ref}
  data-ui="radio"
  {...{ checked: flag(on()), disabled: flag(disabled) }}
><input
    type="radio"
    data-part="input"
    value={own}
    name={group?.name()}
    form={group?.anonymous() ? '' : undefined}
    disabled={off}
    required={group?.required()}
    checked={on()}
    oninput={input}
    onchange={change}
    oninvalid={(event) => group?.invalid(event)}
    onclick={(event) => onclick?.(event.currentTarget.checked, event)}
    {@attach (el) => press(el, { disabled: () => el.matches(':disabled') })}
    {@attach mirror}
  />{@render children?.()}</label>
