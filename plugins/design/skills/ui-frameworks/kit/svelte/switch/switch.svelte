<script lang="ts">
  // switch.svelte: the switch for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <label> that holds a native <input type="checkbox" role="switch"> marked data-part="input", then
  // the author's text. The input takes focus, holds the value and takes part in the form; its role and its checked
  // state are the browser's own, so no aria-checked is written. The label mirrors the state in the attributes the
  // recipe's conditions select on an element with no native form of them: checked, disabled, required and invalid
  // as author attributes, and data-focus-visible and data-active while focus or a key press is on the input (X2).
  // The track and the thumb are the recipe's ::before and ::after. As the React switch.
  //
  // checked is $bindable: bind:checked follows the user, a plain checked only starts it. The first value is the
  // input's default, so a form reset puts it back (F6). oninput, onchange and onclick are the input's events,
  // called with (checked, event); input and change once the root shows the new state.
  import { flushSync, untrack } from 'svelte';
  import type { Snippet } from 'svelte';
  import type { HTMLLabelAttributes, FormEventHandler } from 'svelte/elements';
  import { press } from '../../behaviours/press.js';
  import { props as spec } from '../../components/switch/switch.props.js';

  type Props = Omit<HTMLLabelAttributes, 'children' | 'oninput' | 'onchange' | 'onclick' | 'oninvalid'> & {
    checked?: boolean;
    required?: boolean;
    disabled?: boolean;
    value?: string;
    name?: string;
    oninput?: (checked: boolean, event: Event) => void;
    onchange?: (checked: boolean, event: Event) => void;
    /** Called with the input's state: the root follows at input, as a click can still be cancelled. */
    onclick?: (checked: boolean, event: MouseEvent) => void;
    /** The input's own invalid event. */
    oninvalid?: FormEventHandler<HTMLInputElement>;
    /** The root, for `bind:ref`. */
    ref?: HTMLLabelElement | null;
    children?: Snippet;
  };

  let {
    checked = $bindable(false), required = false, disabled = false, value, name,
    oninput, onchange, onclick, oninvalid, ref = $bindable(null), children, ...rest
  }: Props = $props();

  /** Shown by the browser when a required switch is off. From the manifest's `messages`. */
  const VALUE_MISSING = 'Please turn this on';
  // The first value is the input's default, which a form reset restores (F6).
  const first = untrack(() => checked);
  /** The value submitted while on, when the author gives none: the manifest's default. */
  const defaultValue = (spec.value as { default?: string }).default ?? 'on';
  // Written as the attribute, so it does not rest on the platform's own "on" (as the checkbox).
  const submitted = $derived(value ?? defaultValue);
  /** The user is due to be told that the value is invalid (F5): after a change or a submit attempt, until a reset. */
  let told = $state(false);
  const invalid = $derived(told && required && !checked);
  /** An author attribute that holds while `on`: present and empty, or absent. */
  const flag = (on: boolean) => (on ? '' : undefined);

  // The label has no checked, required, disabled or invalid of its own: they are author attributes.
  const mirrored = $derived({ checked: flag(checked), invalid: flag(invalid), required: flag(required), disabled: flag(disabled) });

  /** What the user turned the switch to, for input and change. */
  let asked = false;
  const input = (event: Event & { currentTarget: HTMLInputElement }) => {
    const el = event.currentTarget;
    asked = el.checked;
    checked = asked;
    told = true;
    flushSync();
    oninput?.(asked, event);
  };
  // input always comes first, so the state is the input's already.
  const change = (event: Event & { currentTarget: HTMLInputElement }) => {
    onchange?.(asked, event);
    // A function binding that kept its value has the last word, as a controlled input has in React: the input is
    // put back once the listeners have seen it as the user left it.
    if (event.currentTarget.checked !== checked) event.currentTarget.checked = checked;
  };
  const click = (event: MouseEvent & { currentTarget: HTMLInputElement }) => onclick?.(event.currentTarget.checked, event);
  const invalidEvent = (event: Event & { currentTarget: EventTarget & HTMLInputElement }) => { told = true; oninvalid?.(event); };

  /** Focus and a key press happen on the input, a part: the root carries their state (X2). A reset is followed (F6). */
  const mirror = (el: HTMLInputElement) => {
    const label = el.parentElement as HTMLElement;
    const put = (attr: string, yes: boolean) => { if (label.hasAttribute(attr) !== yes) label.toggleAttribute(attr, yes); };
    const pressed = new MutationObserver(() => put('data-active', el.hasAttribute('data-active')));
    pressed.observe(el, { attributes: true, attributeFilter: ['data-active'] });
    const off = new AbortController();
    el.addEventListener('focus', () => put('data-focus-visible', el.matches(':focus-visible')), { signal: off.signal });
    el.addEventListener('blur', () => put('data-focus-visible', false), { signal: off.signal });
    // A form reset puts the input back to its default by itself, after the event; the state that mirrors it follows.
    el.form?.addEventListener('reset', () => setTimeout(() => { checked = el.checked; told = false; }), { signal: off.signal });
    return () => { pressed.disconnect(); off.abort(); put('data-active', false); put('data-focus-visible', false); };
  };

  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<label
  {...rest}
  bind:this={ref}
  data-ui="switch"
  {...mirrored}
><input
    type="checkbox"
    role="switch"
    data-part="input"
    {name}
    value={submitted}
    {disabled}
    {required}
    aria-invalid={invalid ? 'true' : undefined}
    defaultChecked={first}
    {checked}
    oninput={input}
    onchange={change}
    onclick={click}
    oninvalid={invalidEvent}
    {@attach (el) => { el.setAttribute('value', submitted); }}
    {@attach (el) => { el.setCustomValidity(required && !checked ? VALUE_MISSING : ''); }}
    {@attach (el) => press(el, { disabled: () => el.matches(':disabled') })}
    {@attach mirror}
  />{@render children?.()}</label>
